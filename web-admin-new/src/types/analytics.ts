export interface KPI {
  name: string;
  value: number | string;
  unit: string;
  status: 'good' | 'warning' | 'critical';
  target?: number | string;
  trend?: 'up' | 'down' | 'stable';
}

export interface ChartData {
  date: string;
  count?: number;
  percentage?: number;
  value?: number;
  iso_date: string;
}

export interface DashboardData {
  kpis: KPI[];
  charts: {
    due_inspections: ChartData[];
    sla_performance: ChartData[];
    error_trends: ChartData[];
  };
  summaries: {
    inspections?: {
      total_due: number;
      overdue: number;
      completion_rate: number;
    };
    sla?: {
      avg_compliance: number;
      target_achievement: number;
      avg_resolution_time: number;
    };
    errors?: {
      avg_error_rate: number;
      most_problematic: string;
      trend_direction: string;
    };
  };
}

export interface AnalyticsResponse {
  status: string;
  data: DashboardData;
  generated_at: string;
}

export interface DueInspectionsAnalytics {
  kpis: KPI[];
  charts: {
    daily_trend: ChartData[];
    gate_types: Array<{
      gate_type: string;
      count: number;
      percentage: number;
    }>;
  };
  summary: {
    total_due: number;
    overdue: number;
    completion_rate: number;
    avg_days_overdue: number;
  };
}

export interface SLAAnalytics {
  kpis: KPI[];
  charts: {
    daily_performance: ChartData[];
    priority_breakdown: Array<{
      priority: string;
      compliance_rate: number;
      avg_resolution_time: number;
    }>;
  };
  summary: {
    overall_compliance: number;
    avg_resolution_time: number;
    target_achievement: number;
  };
}

export interface ErrorStatistics {
  kpis: KPI[];
  charts: {
    error_trends: ChartData[];
    error_types: Array<{
      error_type: string;
      count: number;
      percentage: number;
    }>;
  };
  summary: {
    total_errors: number;
    error_rate: number;
    most_common_error: string;
    trend_direction: string;
  };
}