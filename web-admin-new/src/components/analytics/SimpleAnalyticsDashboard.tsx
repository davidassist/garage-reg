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

export const AnalyticsDashboard = ({ organizationId }: { organizationId?: number }) => {
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
        Betöltés...
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
    <div style={{ padding: '20px' }}>
      
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '30px'
      }}>
        <h2 style={{ fontSize: '28px', fontWeight: 'bold', margin: 0 }}>
          Analitikai Dashboard
        </h2>
        
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
              backgroundColor: '#f9fafb',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            📥 Teljes jelentés letöltése
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '20px',
        marginBottom: '30px'
      }}>
        {kpis.map((kpi: KPI, index: number) => (
          <div
            key={index}
            style={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
            }}
          >
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '10px'
            }}>
              <h3 style={{ 
                fontSize: '14px', 
                color: '#6b7280', 
                margin: 0,
                fontWeight: '500'
              }}>
                {kpi.name}
              </h3>
              <span style={{ 
                fontSize: '20px',
                color: kpi.status === 'good' ? '#16a34a' :
                       kpi.status === 'warning' ? '#d97706' : '#dc2626'
              }}>
                {kpi.status === 'good' ? '✅' :
                 kpi.status === 'warning' ? '⚠️' : '❌'}
              </span>
            </div>
            
            <div style={{ 
              fontSize: '24px', 
              fontWeight: 'bold',
              marginBottom: '5px'
            }}>
              {kpi.value} <span style={{ fontSize: '14px', fontWeight: 'normal', color: '#6b7280' }}>{kpi.unit}</span>
            </div>
            
            {kpi.target && (
              <p style={{ fontSize: '12px', color: '#6b7280', margin: 0 }}>
                Cél: {kpi.target}
              </p>
            )}
            
            <div style={{
              display: 'inline-block',
              padding: '4px 8px',
              borderRadius: '12px',
              fontSize: '12px',
              marginTop: '10px',
              backgroundColor: kpi.status === 'good' ? '#dcfce7' :
                              kpi.status === 'warning' ? '#fef3c7' : '#fee2e2',
              color: kpi.status === 'good' ? '#166534' :
                     kpi.status === 'warning' ? '#92400e' : '#991b1b'
            }}>
              {kpi.status === 'good' ? 'Megfelelő' :
               kpi.status === 'warning' ? 'Figyelem' : 'Kritikus'}
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '20px'
      }}>
        
        {/* Due Inspections Chart */}
        <div style={{
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>
              Lejáró ellenőrzések trendje
            </h3>
            <button
              onClick={() => handleExport('inspections')}
              style={{
                padding: '6px 12px',
                backgroundColor: '#f9fafb',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              📥 CSV
            </button>
          </div>
          
          <div style={{
            height: '200px',
            backgroundColor: '#f9fafb',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column'
          }}>
            <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
              📈 Vonalgrafikon
            </div>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>
              {charts.due_inspections.length} adatpont
            </div>
          </div>
        </div>

        {/* SLA Performance Chart */}
        <div style={{
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>
              SLA teljesítmény
            </h3>
            <button
              onClick={() => handleExport('sla')}
              style={{
                padding: '6px 12px',
                backgroundColor: '#f9fafb',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              📥 Excel
            </button>
          </div>
          
          <div style={{
            height: '200px',
            backgroundColor: '#f9fafb',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column'
          }}>
            <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
              📈 Vonalgrafikon
            </div>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>
              {charts.sla_performance.length} adatpont - SLA %
            </div>
          </div>
        </div>

        {/* Error Statistics Chart */}
        <div style={{
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>
              Hibastatisztika
            </h3>
            <button
              onClick={() => handleExport('errors')}
              style={{
                padding: '6px 12px',
                backgroundColor: '#f9fafb',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              📥 CSV
            </button>
          </div>
          
          <div style={{
            height: '200px',
            backgroundColor: '#f9fafb',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column'
          }}>
            <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
              📊 Oszlopdiagram
            </div>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>
              {charts.error_trends.length} adatpont - Hibaarány %
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default AnalyticsDashboard;