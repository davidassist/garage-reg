import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Download, TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from 'lucide-react';
import { useAnalytics } from '@/hooks/useAnalytics';
import { KPI } from '@/types/analytics';

// Simple chart placeholder components
const SimpleLineChart = ({ data, dataKey }: { data: any[], dataKey: string }) => (
  <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
    <div className="text-center">
      <div className="text-lg font-semibold mb-2">Vonalgrafikon</div>
      <div className="text-sm text-gray-600">
        {data.length} adatpont - {dataKey} metrika
      </div>
    </div>
  </div>
);

const SimpleBarChart = ({ data, dataKey }: { data: any[], dataKey: string }) => (
  <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
    <div className="text-center">
      <div className="text-lg font-semibold mb-2">Oszlopdiagram</div>
      <div className="text-sm text-gray-600">
        {data.length} adatpont - {dataKey} metrika
      </div>
    </div>
  </div>
);

interface AnalyticsDashboardProps {
  organizationId?: number;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ organizationId }) => {
  const [daysBack, setDaysBack] = useState(30);
  const { 
    dashboardData, 
    isLoading, 
    error, 
    exportDashboard,
    exportInspections,
    exportSLA,
    exportErrors 
  } = useAnalytics(organizationId, daysBack);

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

  const handleExport = async (type: 'dashboard' | 'inspections' | 'sla' | 'errors') => {
    try {
      let blob: Blob;
      let filename: string;
      
      switch (type) {
        case 'dashboard':
          blob = await exportDashboard(daysBack);
          filename = `dashboard_jelentes_${new Date().toISOString().split('T')[0]}.xlsx`;
          break;
        case 'inspections':
          blob = await exportInspections(30);
          filename = `lejaro_ellenorzesek_${new Date().toISOString().split('T')[0]}.csv`;
          break;
        case 'sla':
          blob = await exportSLA(daysBack);
          filename = `sla_jelentes_${new Date().toISOString().split('T')[0]}.xlsx`;
          break;
        case 'errors':
          blob = await exportErrors(daysBack);
          filename = `hibastatisztika_${new Date().toISOString().split('T')[0]}.csv`;
          break;
        default:
          return;
      }

      // Download file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Hiba a dashboard betöltésekor</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData) return null;

  const { kpis, charts, summaries } = dashboardData;

  return (
    <div className="space-y-6">
      {/* Header with controls */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Analitikai Dashboard</h2>
        
        <div className="flex items-center space-x-4">
          <select
            value={daysBack}
            onChange={(e) => setDaysBack(parseInt(e.target.value))}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            <option value={7}>Utolsó 7 nap</option>
            <option value={30}>Utolsó 30 nap</option>
            <option value={90}>Utolsó 90 nap</option>
          </select>
          
          <Button onClick={() => handleExport('dashboard')} variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Teljes jelentés letöltése
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {kpis.map((kpi: KPI, index: number) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {kpi.name}
              </CardTitle>
              {getStatusIcon(kpi.status)}
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline justify-between">
                <div className="text-2xl font-bold">
                  {kpi.value}
                  <span className="text-sm font-normal text-gray-500 ml-1">
                    {kpi.unit}
                  </span>
                </div>
                <div className="flex items-center">
                  {kpi.trend && getTrendIcon(kpi.trend)}
                </div>
              </div>
              {kpi.target && (
                <p className="text-xs text-gray-500 mt-1">
                  Cél: {kpi.target}
                </p>
              )}
              <Badge 
                variant={
                  kpi.status === 'good' ? 'default' : 
                  kpi.status === 'warning' ? 'secondary' : 
                  'destructive'
                }
                className="mt-2"
              >
                {kpi.status === 'good' ? 'Megfelelő' : 
                 kpi.status === 'warning' ? 'Figyelem' : 'Kritikus'}
              </Badge>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Due Inspections Chart */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Lejáró ellenőrzések trendje</CardTitle>
            <Button onClick={() => handleExport('inspections')} variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              CSV
            </Button>
          </CardHeader>
          <CardContent>
            <SimpleLineChart data={charts.due_inspections} dataKey="count" />
          </CardContent>
        </Card>

        {/* SLA Performance Chart */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>SLA teljesítmény</CardTitle>
            <Button onClick={() => handleExport('sla')} variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Excel
            </Button>
          </CardHeader>
          <CardContent>
            <SimpleLineChart data={charts.sla_performance} dataKey="percentage" />
          </CardContent>
        </Card>

        {/* Error Statistics Chart */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Hibastatisztika</CardTitle>
            <Button onClick={() => handleExport('errors')} variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              CSV
            </Button>
          </CardHeader>
          <CardContent>
            <SimpleBarChart data={charts.error_trends} dataKey="percentage" />
          </CardContent>
        </Card>

        {/* Summary Statistics */}
        <Card>
          <CardHeader>
            <CardTitle>Összefoglalók</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              
              {/* Due Inspections Summary */}
              {summaries.inspections && (
                <div>
                  <h4 className="font-medium text-sm text-gray-700 mb-2">Ellenőrzések</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Összes esedékes:</span>
                      <span className="font-medium ml-2">{summaries.inspections.total_due}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Lejárt:</span>
                      <span className="font-medium ml-2 text-red-600">{summaries.inspections.overdue}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* SLA Summary */}
              {summaries.sla && (
                <div>
                  <h4 className="font-medium text-sm text-gray-700 mb-2">SLA</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Átlagos megfelelés:</span>
                      <span className="font-medium ml-2">{summaries.sla.avg_compliance}%</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Cél teljesítés:</span>
                      <span className="font-medium ml-2">{summaries.sla.target_achievement}%</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Error Summary */}
              {summaries.errors && (
                <div>
                  <h4 className="font-medium text-sm text-gray-700 mb-2">Hibák</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Átlagos hibaarány:</span>
                      <span className="font-medium ml-2">{summaries.errors.avg_error_rate}%</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Legproblémásabb típus:</span>
                      <span className="font-medium ml-2">{summaries.errors.most_problematic}</span>
                    </div>
                  </div>
                </div>
              )}

            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
};

export default AnalyticsDashboard;