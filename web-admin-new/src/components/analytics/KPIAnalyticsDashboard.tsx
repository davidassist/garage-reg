import React, { useState, useEffect } from 'react';

interface KPI {
  name: string;
  value: number | string;
  unit: string;
  status: 'good' | 'warning' | 'critical';
  target?: number | string;
  trend?: 'up' | 'down' | 'stable';
}

interface ChartData {
  date: string;
  count?: number;
  percentage?: number;
  value?: number;
  iso_date?: string;
}

interface DashboardData {
  kpis: KPI[];
  charts: {
    due_inspections: ChartData[];
    sla_performance: ChartData[];
    error_trends: ChartData[];
  };
  summaries: {
    inspections: any;
    sla: any;
    errors: any;
  };
  analysis?: {
    gate_types?: any[];
    priority_breakdown?: any[];
    problematic_gates?: any[];
  };
}

// Simple chart components using SVG
const SimpleBarChart: React.FC<{ data: ChartData[]; title: string }> = ({ data, title }) => {
  const maxValue = Math.max(...data.map(d => d.count || 0));
  const chartHeight = 200;
  const chartWidth = 400;
  const barWidth = chartWidth / data.length - 2;

  return (
    <div className="chart-container">
      <h4 className="chart-title">{title}</h4>
      <svg width={chartWidth} height={chartHeight + 40} className="chart-svg">
        {data.map((item, index) => {
          const height = ((item.count || 0) / maxValue) * chartHeight;
          const x = index * (barWidth + 2);
          const y = chartHeight - height;
          
          return (
            <g key={index}>
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={height}
                fill="#3B82F6"
                className="chart-bar"
              />
              <text
                x={x + barWidth / 2}
                y={chartHeight + 20}
                textAnchor="middle"
                fontSize="10"
                fill="#666"
              >
                {new Date(item.date).toLocaleDateString('hu-HU', { 
                  month: 'short', 
                  day: 'numeric' 
                })}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

const SimpleLineChart: React.FC<{ data: ChartData[]; title: string }> = ({ data, title }) => {
  const maxValue = Math.max(...data.map(d => d.percentage || 0));
  const chartHeight = 200;
  const chartWidth = 400;
  const stepX = chartWidth / (data.length - 1 || 1);

  const pathData = data.map((item, index) => {
    const x = index * stepX;
    const y = chartHeight - ((item.percentage || 0) / maxValue) * chartHeight;
    return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ');

  return (
    <div className="chart-container">
      <h4 className="chart-title">{title}</h4>
      <svg width={chartWidth} height={chartHeight + 40} className="chart-svg">
        <path
          d={pathData}
          stroke="#10B981"
          strokeWidth="2"
          fill="none"
        />
        {data.map((item, index) => {
          const x = index * stepX;
          const y = chartHeight - ((item.percentage || 0) / maxValue) * chartHeight;
          
          return (
            <g key={index}>
              <circle
                cx={x}
                cy={y}
                r="3"
                fill="#10B981"
              />
              <text
                x={x}
                y={chartHeight + 20}
                textAnchor="middle"
                fontSize="10"
                fill="#666"
              >
                {new Date(item.date).toLocaleDateString('hu-HU', { 
                  month: 'short', 
                  day: 'numeric' 
                })}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

export const KPIAnalyticsDashboard: React.FC<{ organizationId?: number }> = ({ 
  organizationId 
}) => {
  const [daysBack, setDaysBack] = useState(30);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      const params = new URLSearchParams({
        days_back: daysBack.toString(),
      });

      if (organizationId) {
        params.append('organization_id', organizationId.toString());
      }

      const response = await fetch(`/api/analytics/dashboard?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const result = await response.json();
      if (result.status === 'success') {
        setDashboardData(result.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (type: 'dashboard' | 'inspections' | 'sla' | 'errors') => {
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams({
        days_back: daysBack.toString(),
      });

      if (organizationId) {
        params.append('organization_id', organizationId.toString());
      }

      const endpoint = type === 'dashboard' ? '/api/analytics/export/dashboard/excel' :
                     type === 'inspections' ? '/api/analytics/export/inspections/csv' :
                     type === 'sla' ? '/api/analytics/export/sla/excel' :
                     '/api/analytics/export/errors/csv';

      const response = await fetch(`${endpoint}?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const fileExt = type === 'sla' || type === 'dashboard' ? 'xlsx' : 'csv';
        a.download = `${type}_export_${new Date().toISOString().split('T')[0]}.${fileExt}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good':
        return '#10B981';
      case 'warning':
        return '#F59E0B';
      case 'critical':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'good':
        return '✓';
      case 'warning':
        return '⚠';
      case 'critical':
        return '✕';
      default:
        return '•';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return '↗';
      case 'down':
        return '↘';
      default:
        return '→';
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [organizationId, daysBack]);

  const styles = `
    .dashboard-container {
      padding: 24px;
      background-color: #f9fafb;
      min-height: 100vh;
      font-family: system-ui, -apple-system, sans-serif;
    }

    .dashboard-header {
      background: white;
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .dashboard-title {
      font-size: 28px;
      font-weight: bold;
      color: #111827;
      margin: 0 0 16px 0;
      display: flex;
      align-items: center;
    }

    .dashboard-controls {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .select-input {
      border: 1px solid #d1d5db;
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 14px;
      background: white;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 24px;
      margin-bottom: 32px;
    }

    .kpi-card {
      background: white;
      border-radius: 8px;
      padding: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      border: 1px solid #e5e7eb;
    }

    .kpi-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
    }

    .kpi-name {
      font-size: 14px;
      font-weight: 500;
      color: #6b7280;
      margin: 0;
    }

    .kpi-value {
      font-size: 32px;
      font-weight: 600;
      color: #111827;
      margin: 8px 0 4px 0;
    }

    .kpi-unit {
      font-size: 14px;
      color: #6b7280;
      margin-left: 4px;
    }

    .kpi-target {
      font-size: 12px;
      color: #6b7280;
      margin: 4px 0 0 0;
    }

    .kpi-status {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .status-icon {
      font-size: 18px;
    }

    .trend-icon {
      font-size: 14px;
      color: #6b7280;
    }

    .charts-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 24px;
      margin-bottom: 32px;
    }

    .chart-container {
      background: white;
      border-radius: 8px;
      padding: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      border: 1px solid #e5e7eb;
    }

    .chart-title {
      font-size: 18px;
      font-weight: 600;
      color: #111827;
      margin: 0 0 16px 0;
    }

    .chart-svg {
      background: #f9fafb;
      border-radius: 4px;
    }

    .chart-bar:hover {
      fill: #2563eb;
    }

    .export-section {
      background: white;
      border-radius: 8px;
      padding: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      margin-bottom: 24px;
    }

    .export-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-top: 16px;
    }

    .export-button {
      background: #3b82f6;
      color: white;
      border: none;
      border-radius: 6px;
      padding: 12px 16px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: background-color 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    .export-button:hover {
      background: #2563eb;
    }

    .export-button.green {
      background: #10b981;
    }

    .export-button.green:hover {
      background: #059669;
    }

    .export-button.yellow {
      background: #f59e0b;
    }

    .export-button.yellow:hover {
      background: #d97706;
    }

    .export-button.red {
      background: #ef4444;
    }

    .export-button.red:hover {
      background: #dc2626;
    }

    .loading-container {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 200px;
      background: white;
      border-radius: 8px;
      margin: 24px;
    }

    .error-container {
      background: #fef2f2;
      border: 1px solid #fecaca;
      border-radius: 8px;
      padding: 16px;
      margin: 24px;
      color: #b91c1c;
    }

    .summary-section {
      background: white;
      border-radius: 8px;
      padding: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      margin-bottom: 24px;
    }

    .summary-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 24px;
      margin-top: 16px;
    }

    .summary-item h4 {
      font-size: 16px;
      font-weight: 600;
      color: #374151;
      margin: 0 0 8px 0;
    }

    .summary-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .summary-list li {
      font-size: 14px;
      color: #6b7280;
      margin-bottom: 4px;
    }
  `;

  if (isLoading) {
    return (
      <div>
        <style>{styles}</style>
        <div className="loading-container">
          <div>
            <div style={{ 
              width: 32, 
              height: 32, 
              border: '3px solid #f3f3f3', 
              borderTop: '3px solid #3b82f6',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 16px'
            }}></div>
            <p>Adatok betöltése...</p>
          </div>
        </div>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <style>{styles}</style>
        <div className="error-container">
          <strong>Hiba:</strong> {error}
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div>
        <style>{styles}</style>
        <div className="error-container">
          Nincsenek elérhető adatok
        </div>
      </div>
    );
  }

  return (
    <div>
      <style>{styles}</style>
      <div className="dashboard-container">
        {/* Header */}
        <div className="dashboard-header">
          <h1 className="dashboard-title">
            📊 KPI Analytics Dashboard
          </h1>
          <div className="dashboard-controls">
            <label>Időszak:</label>
            <select
              value={daysBack}
              onChange={(e) => setDaysBack(Number(e.target.value))}
              className="select-input"
            >
              <option value={7}>7 nap</option>
              <option value={30}>30 nap</option>
              <option value={90}>90 nap</option>
            </select>
          </div>
        </div>

        {/* 3 Key KPI Cards */}
        <div className="kpi-grid">
          {dashboardData.kpis.slice(0, 3).map((kpi, index) => (
            <div key={index} className="kpi-card">
              <div className="kpi-header">
                <div>
                  <p className="kpi-name">{kpi.name}</p>
                  <div className="kpi-value">
                    {kpi.value}
                    <span className="kpi-unit">{kpi.unit}</span>
                  </div>
                  {kpi.target && (
                    <p className="kpi-target">
                      Cél: {kpi.target} {kpi.unit}
                    </p>
                  )}
                </div>
                <div className="kpi-status">
                  <span 
                    className="status-icon" 
                    style={{ color: getStatusColor(kpi.status) }}
                  >
                    {getStatusIcon(kpi.status)}
                  </span>
                  {kpi.trend && (
                    <span className="trend-icon">
                      {getTrendIcon(kpi.trend)}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 3 Main Charts */}
        <div className="charts-grid">
          <SimpleBarChart 
            data={dashboardData.charts.due_inspections} 
            title="Lejáró Ellenőrzések"
          />
          <SimpleLineChart 
            data={dashboardData.charts.sla_performance} 
            title="SLA Teljesítmény (%)"
          />
          <SimpleLineChart 
            data={dashboardData.charts.error_trends} 
            title="Hibastatisztika (%)"
          />
        </div>

        {/* Export Section */}
        <div className="export-section">
          <h3>Export Funkciók</h3>
          <div className="export-grid">
            <button
              onClick={() => handleExport('dashboard')}
              className="export-button"
            >
              📊 Teljes Dashboard (Excel)
            </button>
            <button
              onClick={() => handleExport('inspections')}
              className="export-button green"
            >
              ✅ Ellenőrzések (CSV)
            </button>
            <button
              onClick={() => handleExport('sla')}
              className="export-button yellow"
            >
              ⏱️ SLA Jelentés (Excel)
            </button>
            <button
              onClick={() => handleExport('errors')}
              className="export-button red"
            >
              🚨 Hibastatisztika (CSV)
            </button>
          </div>
        </div>

        {/* Summary Information */}
        {dashboardData.summaries && (
          <div className="summary-section">
            <h3>Összefoglaló Adatok</h3>
            <div className="summary-grid">
              {dashboardData.summaries.inspections && (
                <div className="summary-item">
                  <h4>Ellenőrzések</h4>
                  <ul className="summary-list">
                    <li>Összesen: {dashboardData.summaries.inspections.total_inspections || 0}</li>
                    <li>Lejárt: {dashboardData.summaries.inspections.overdue_count || 0}</li>
                    <li>Folyamatban: {dashboardData.summaries.inspections.in_progress || 0}</li>
                  </ul>
                </div>
              )}
              {dashboardData.summaries.sla && (
                <div className="summary-item">
                  <h4>SLA Teljesítmény</h4>
                  <ul className="summary-list">
                    <li>Átlagos megfelelés: {dashboardData.summaries.sla.average_compliance || 0}%</li>
                    <li>Időben teljesített: {dashboardData.summaries.sla.on_time_count || 0}</li>
                    <li>Késő teljesített: {dashboardData.summaries.sla.late_count || 0}</li>
                  </ul>
                </div>
              )}
              {dashboardData.summaries.errors && (
                <div className="summary-item">
                  <h4>Hibastatisztika</h4>
                  <ul className="summary-list">
                    <li>Összes hiba: {dashboardData.summaries.errors.total_errors || 0}</li>
                    <li>Kritikus: {dashboardData.summaries.errors.critical_errors || 0}</li>
                    <li>Átlagos hibaarány: {dashboardData.summaries.errors.average_error_rate || 0}%</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default KPIAnalyticsDashboard;