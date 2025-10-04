import { useState, useEffect } from 'react';

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
}

interface DashboardData {
  kpis: KPI[];
  charts: {
    due_inspections: ChartData[];
    sla_performance: ChartData[];
    error_trends: ChartData[];
  };
  summaries: any;
}

// Simple SVG Chart Components
const BarChart = ({ data, title, color = '#3B82F6' }: { 
  data: ChartData[], 
  title: string,
  color?: string 
}) => {
  if (!data || data.length === 0) {
    return (
      <div style={{
        height: '200px',
        backgroundColor: '#f9fafb',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column'
      }}>
        <div style={{ fontSize: '14px', color: '#6b7280' }}>
          Nincsenek adatok
        </div>
      </div>
    );
  }

  const maxValue = Math.max(...data.map(d => d.count || d.value || 0));
  const chartWidth = 360;
  const chartHeight = 160;
  const barWidth = (chartWidth - 40) / data.length - 2;
  
  return (
    <div style={{ width: '100%' }}>
      <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '8px' }}>
        {title}
      </div>
      <svg width={chartWidth} height={chartHeight + 40} style={{ width: '100%', height: 'auto' }}>
        {data.map((item, index) => {
          const value = item.count || item.value || 0;
          const height = maxValue > 0 ? (value / maxValue) * chartHeight : 0;
          const x = 20 + index * (barWidth + 2);
          const y = chartHeight - height + 10;
          
          return (
            <g key={index}>
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={height}
                fill={color}
                opacity={0.8}
              />
              <text
                x={x + barWidth / 2}
                y={chartHeight + 25}
                textAnchor="middle"
                fontSize="10"
                fill="#666"
              >
                {new Date(item.date).toLocaleDateString('hu-HU', { 
                  month: 'numeric', 
                  day: 'numeric' 
                })}
              </text>
              <text
                x={x + barWidth / 2}
                y={y - 5}
                textAnchor="middle"
                fontSize="10"
                fill="#333"
              >
                {value}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

const LineChart = ({ data, title, color = '#10B981' }: { 
  data: ChartData[], 
  title: string,
  color?: string 
}) => {
  if (!data || data.length === 0) {
    return (
      <div style={{
        height: '200px',
        backgroundColor: '#f9fafb',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column'
      }}>
        <div style={{ fontSize: '14px', color: '#6b7280' }}>
          Nincsenek adatok
        </div>
      </div>
    );
  }

  const maxValue = Math.max(...data.map(d => d.percentage || d.value || 0));
  const chartWidth = 360;
  const chartHeight = 160;
  const stepX = (chartWidth - 40) / (data.length - 1 || 1);
  
  const pathData = data.map((item, index) => {
    const value = item.percentage || item.value || 0;
    const x = 20 + index * stepX;
    const y = 10 + chartHeight - (maxValue > 0 ? (value / maxValue) * chartHeight : 0);
    return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ');
  
  return (
    <div style={{ width: '100%' }}>
      <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '8px' }}>
        {title}
      </div>
      <svg width={chartWidth} height={chartHeight + 40} style={{ width: '100%', height: 'auto' }}>
        <path
          d={pathData}
          stroke={color}
          strokeWidth="2"
          fill="none"
        />
        {data.map((item, index) => {
          const value = item.percentage || item.value || 0;
          const x = 20 + index * stepX;
          const y = 10 + chartHeight - (maxValue > 0 ? (value / maxValue) * chartHeight : 0);
          
          return (
            <g key={index}>
              <circle
                cx={x}
                cy={y}
                r="3"
                fill={color}
              />
              <text
                x={x}
                y={chartHeight + 35}
                textAnchor="middle"
                fontSize="10"
                fill="#666"
              >
                {new Date(item.date).toLocaleDateString('hu-HU', { 
                  month: 'numeric', 
                  day: 'numeric' 
                })}
              </text>
              <text
                x={x}
                y={y - 8}
                textAnchor="middle"
                fontSize="10"
                fill="#333"
              >
                {value}%
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

export const EnhancedAnalyticsDashboard = ({ organizationId }: { organizationId?: number }) => {
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

  const handleExport = async (type: string) => {
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
        a.download = `${type}_export_${new Date().toISOString().split('T')[0]}.${type === 'sla' || type === 'dashboard' ? 'xlsx' : 'csv'}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [organizationId, daysBack]);

  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '200px',
        fontSize: '18px' 
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '40px', 
            height: '40px',
            border: '4px solid #f3f4f6',
            borderTop: '4px solid #3B82F6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          Adatok betöltése...
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
      <div style={{ 
        padding: '20px', 
        backgroundColor: '#fee2e2', 
        border: '1px solid #fecaca',
        borderRadius: '8px',
        color: '#dc2626'
      }}>
        <h3>Hiba a dashboard betöltésekor</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!dashboardData) return null;

  const { kpis, charts } = dashboardData;

  return (
    <div style={{ padding: '20px', backgroundColor: '#f9fafb', minHeight: '100vh' }}>
      
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '30px',
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
      }}>
        <h1 style={{ 
          fontSize: '28px', 
          fontWeight: 'bold', 
          margin: 0,
          display: 'flex',
          alignItems: 'center'
        }}>
          📊 KPI Analytics Dashboard
        </h1>
        
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          <select
            value={daysBack}
            onChange={(e) => setDaysBack(parseInt(e.target.value))}
            style={{
              padding: '8px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          >
            <option value={7}>Utolsó 7 nap</option>
            <option value={30}>Utolsó 30 nap</option>
            <option value={90}>Utolsó 90 nap</option>
          </select>
          
          <button
            onClick={() => handleExport('dashboard')}
            style={{
              padding: '8px 16px',
              backgroundColor: '#3B82F6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            📥 Teljes jelentés letöltése
          </button>
        </div>
      </div>

      {/* 3 Key KPI Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '20px',
        marginBottom: '30px'
      }}>
        {kpis.slice(0, 3).map((kpi: KPI, index: number) => (
          <div
            key={index}
            style={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
              transition: 'transform 0.2s, box-shadow 0.2s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 8px 0 rgba(0, 0, 0, 0.15)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0px)';
              e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)';
            }}
          >
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              marginBottom: '12px'
            }}>
              <h3 style={{ 
                fontSize: '14px', 
                color: '#6b7280', 
                margin: 0,
                fontWeight: '500',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                {kpi.name}
              </h3>
              <span style={{ 
                fontSize: '24px',
                color: kpi.status === 'good' ? '#16a34a' :
                       kpi.status === 'warning' ? '#d97706' : '#dc2626'
              }}>
                {kpi.status === 'good' ? '✅' :
                 kpi.status === 'warning' ? '⚠️' : '❌'}
              </span>
            </div>
            
            <div style={{ 
              fontSize: '36px', 
              fontWeight: '700',
              marginBottom: '8px',
              color: '#111827'
            }}>
              {kpi.value} <span style={{ fontSize: '16px', fontWeight: '400', color: '#6b7280' }}>{kpi.unit}</span>
            </div>
            
            {kpi.target && (
              <p style={{ fontSize: '14px', color: '#6b7280', margin: '0 0 12px 0' }}>
                Cél: {kpi.target} {kpi.unit}
              </p>
            )}
            
            <div style={{
              display: 'inline-block',
              padding: '6px 12px',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: '600',
              backgroundColor: kpi.status === 'good' ? '#dcfce7' :
                              kpi.status === 'warning' ? '#fef3c7' : '#fee2e2',
              color: kpi.status === 'good' ? '#166534' :
                     kpi.status === 'warning' ? '#92400e' : '#991b1b'
            }}>
              {kpi.status === 'good' ? '✓ Megfelelő' :
               kpi.status === 'warning' ? '⚠ Figyelem' : '✕ Kritikus'}
            </div>
          </div>
        ))}
      </div>

      {/* 3 Main Charts */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '20px',
        marginBottom: '30px'
      }}>
        
        {/* Due Inspections Chart */}
        <div style={{
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '12px',
          padding: '24px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>
              📋 Lejáró ellenőrzések trendje
            </h3>
            <button
              onClick={() => handleExport('inspections')}
              style={{
                padding: '6px 12px',
                backgroundColor: '#10B981',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              📥 CSV
            </button>
          </div>
          
          <BarChart 
            data={charts.due_inspections} 
            title={`${charts.due_inspections.length} nap adatai`}
            color="#3B82F6"
          />
        </div>

        {/* SLA Performance Chart */}
        <div style={{
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '12px',
          padding: '24px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>
              ⏱️ SLA teljesítmény trend
            </h3>
            <button
              onClick={() => handleExport('sla')}
              style={{
                padding: '6px 12px',
                backgroundColor: '#F59E0B',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              📥 Excel
            </button>
          </div>
          
          <LineChart 
            data={charts.sla_performance} 
            title={`${charts.sla_performance.length} nap SLA adatai`}
            color="#10B981"
          />
        </div>

        {/* Error Statistics Chart */}
        <div style={{
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '12px',
          padding: '24px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>
              🚨 Hibastatisztika trend
            </h3>
            <button
              onClick={() => handleExport('errors')}
              style={{
                padding: '6px 12px',
                backgroundColor: '#EF4444',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              📥 CSV
            </button>
          </div>
          
          <LineChart 
            data={charts.error_trends} 
            title={`${charts.error_trends.length} nap hibaaránya`}
            color="#EF4444"
          />
        </div>

      </div>

      {/* Export Actions Panel */}
      <div style={{
        backgroundColor: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
      }}>
        <h3 style={{ fontSize: '20px', fontWeight: '600', margin: '0 0 20px 0' }}>
          📊 Export lehetőségek
        </h3>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px'
        }}>
          <button
            onClick={() => handleExport('dashboard')}
            style={{
              padding: '16px 20px',
              backgroundColor: '#3B82F6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2563EB'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#3B82F6'}
          >
            📊 Teljes Dashboard (Excel)
          </button>
          
          <button
            onClick={() => handleExport('inspections')}
            style={{
              padding: '16px 20px',
              backgroundColor: '#10B981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#059669'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#10B981'}
          >
            📋 Ellenőrzések (CSV)
          </button>
          
          <button
            onClick={() => handleExport('sla')}
            style={{
              padding: '16px 20px',
              backgroundColor: '#F59E0B',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#D97706'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#F59E0B'}
          >
            ⏱️ SLA Jelentés (Excel)
          </button>
          
          <button
            onClick={() => handleExport('errors')}
            style={{
              padding: '16px 20px',
              backgroundColor: '#EF4444',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#DC2626'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#EF4444'}
          >
            🚨 Hibastatisztika (CSV)
          </button>
        </div>
      </div>

    </div>
  );
};

export default EnhancedAnalyticsDashboard;