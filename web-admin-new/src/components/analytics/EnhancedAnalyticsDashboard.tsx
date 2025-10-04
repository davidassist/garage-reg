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

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

export const EnhancedAnalyticsDashboard: React.FC<{ organizationId?: number }> = ({ 
  organizationId 
}) => {
  const [daysBack, setDaysBack] = useState(30);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

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

  useEffect(() => {
    fetchDashboardData();
  }, [organizationId, daysBack]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'good':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'critical':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const formatChartData = (data: ChartData[]) => {
    return data.map(item => ({
      ...item,
      displayDate: new Date(item.date).toLocaleDateString('hu-HU', {
        month: 'short',
        day: 'numeric'
      })
    }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="text-lg">Adatok betöltése...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
          <span className="text-red-700">Hiba: {error}</span>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="bg-gray-50 border rounded-lg p-4">
        <span className="text-gray-600">Nincsenek elérhető adatok</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <BarChart3 className="w-7 h-7 mr-3 text-blue-600" />
            Analytics Dashboard
          </h2>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <select
                value={daysBack}
                onChange={(e) => setDaysBack(Number(e.target.value))}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm"
              >
                <option value={7}>7 nap</option>
                <option value={30}>30 nap</option>
                <option value={90}>90 nap</option>
              </select>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Áttekintés', icon: Activity },
              { id: 'inspections', name: 'Ellenőrzések', icon: CheckCircle },
              { id: 'sla', name: 'SLA Teljesítmény', icon: TrendingUp },
              { id: 'errors', name: 'Hibastatisztika', icon: AlertTriangle },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {dashboardData.kpis.slice(0, 3).map((kpi, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">{kpi.name}</p>
                <div className="flex items-baseline mt-2">
                  <p className="text-3xl font-semibold text-gray-900">
                    {kpi.value}
                  </p>
                  <span className="ml-1 text-sm text-gray-500">{kpi.unit}</span>
                </div>
                {kpi.target && (
                  <p className="text-xs text-gray-500 mt-1">
                    Cél: {kpi.target} {kpi.unit}
                  </p>
                )}
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(kpi.status)}
                {kpi.trend && getTrendIcon(kpi.trend)}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {/* Lejáró Ellenőrzések Chart */}
          <div className="bg-white rounded-lg shadow-sm border p-6 col-span-1">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Lejáró Ellenőrzések</h3>
              <button
                onClick={() => handleExport('inspections')}
                className="text-blue-600 hover:text-blue-800"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={formatChartData(dashboardData.charts.due_inspections)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="displayDate" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  labelFormatter={(label, payload) => 
                    payload?.[0]?.payload?.date ? 
                    new Date(payload[0].payload.date).toLocaleDateString('hu-HU') : 
                    label
                  }
                />
                <Bar dataKey="count" fill="#3B82F6" name="Ellenőrzések" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* SLA Teljesítmény Chart */}
          <div className="bg-white rounded-lg shadow-sm border p-6 col-span-1">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">SLA Teljesítmény</h3>
              <button
                onClick={() => handleExport('sla')}
                className="text-blue-600 hover:text-blue-800"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={formatChartData(dashboardData.charts.sla_performance)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="displayDate" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  domain={[0, 100]}
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip 
                  formatter={(value: any) => [`${value}%`, 'SLA Megfelelés']}
                  labelFormatter={(label, payload) => 
                    payload?.[0]?.payload?.date ? 
                    new Date(payload[0].payload.date).toLocaleDateString('hu-HU') : 
                    label
                  }
                />
                <Area 
                  type="monotone" 
                  dataKey="percentage" 
                  stroke="#10B981" 
                  fill="#10B981" 
                  fillOpacity={0.3}
                  name="SLA %"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Hibastatisztika Chart */}
          <div className="bg-white rounded-lg shadow-sm border p-6 col-span-1">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Hibastatisztika</h3>
              <button
                onClick={() => handleExport('errors')}
                className="text-blue-600 hover:text-blue-800"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={formatChartData(dashboardData.charts.error_trends)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="displayDate" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip 
                  formatter={(value: any) => [`${value}%`, 'Hibaarány']}
                  labelFormatter={(label, payload) => 
                    payload?.[0]?.payload?.date ? 
                    new Date(payload[0].payload.date).toLocaleDateString('hu-HU') : 
                    label
                  }
                />
                <Line 
                  type="monotone" 
                  dataKey="percentage" 
                  stroke="#EF4444" 
                  strokeWidth={2}
                  dot={{ fill: '#EF4444' }}
                  name="Hibaarány"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Export Actions */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Funkciók</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button
            onClick={() => handleExport('dashboard')}
            className="flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Teljes Dashboard (Excel)
          </button>
          <button
            onClick={() => handleExport('inspections')}
            className="flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Ellenőrzések (CSV)
          </button>
          <button
            onClick={() => handleExport('sla')}
            className="flex items-center justify-center px-4 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            SLA Jelentés (Excel)
          </button>
          <button
            onClick={() => handleExport('errors')}
            className="flex items-center justify-center px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Hibastatisztika (CSV)
          </button>
        </div>
      </div>

      {/* Summary Information */}
      {dashboardData.summaries && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Összefoglaló Adatok</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {dashboardData.summaries.inspections && (
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Ellenőrzések</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>Összesen: {dashboardData.summaries.inspections.total_inspections || 0}</li>
                  <li>Lejárt: {dashboardData.summaries.inspections.overdue_count || 0}</li>
                  <li>Folyamatban: {dashboardData.summaries.inspections.in_progress || 0}</li>
                </ul>
              </div>
            )}
            {dashboardData.summaries.sla && (
              <div>
                <h4 className="font-medium text-gray-700 mb-2">SLA</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>Átlagos megfelelés: {dashboardData.summaries.sla.average_compliance || 0}%</li>
                  <li>Időben teljesített: {dashboardData.summaries.sla.on_time_count || 0}</li>
                  <li>Késő teljesített: {dashboardData.summaries.sla.late_count || 0}</li>
                </ul>
              </div>
            )}
            {dashboardData.summaries.errors && (
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Hibák</h4>
                <ul className="text-sm text-gray-600 space-y-1">
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
  );
};

export default EnhancedAnalyticsDashboard;