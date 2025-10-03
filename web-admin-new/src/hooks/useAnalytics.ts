import { useState, useEffect } from 'react';
import { DashboardData } from '@/types/analytics';

const API_BASE = '/api';

interface UseAnalyticsReturn {
  dashboardData: DashboardData | null;
  isLoading: boolean;
  error: string | null;
  exportDashboard: (daysBack: number) => Promise<Blob>;
  exportInspections: (daysAhead: number) => Promise<Blob>;
  exportSLA: (daysBack: number) => Promise<Blob>;
  exportErrors: (daysBack: number) => Promise<Blob>;
}

export const useAnalytics = (
  organizationId?: number,
  daysBack: number = 30
): UseAnalyticsReturn => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
    const token = localStorage.getItem('token');
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response;
  };

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params = new URLSearchParams({
        days_back: daysBack.toString(),
      });

      if (organizationId) {
        params.append('organization_id', organizationId.toString());
      }

      const response = await fetchWithAuth(`${API_BASE}/analytics/dashboard?${params}`);
      const result = await response.json();

      if (result.status === 'success') {
        setDashboardData(result.data);
      } else {
        throw new Error('API returned error status');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Analytics fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const exportDashboard = async (exportDaysBack: number): Promise<Blob> => {
    const params = new URLSearchParams({
      days_back: exportDaysBack.toString(),
    });

    if (organizationId) {
      params.append('organization_id', organizationId.toString());
    }

    const response = await fetchWithAuth(`${API_BASE}/analytics/export/dashboard/excel?${params}`);
    return response.blob();
  };

  const exportInspections = async (daysAhead: number): Promise<Blob> => {
    const params = new URLSearchParams({
      days_ahead: daysAhead.toString(),
    });

    if (organizationId) {
      params.append('organization_id', organizationId.toString());
    }

    const response = await fetchWithAuth(`${API_BASE}/analytics/export/inspections/csv?${params}`);
    return response.blob();
  };

  const exportSLA = async (exportDaysBack: number): Promise<Blob> => {
    const params = new URLSearchParams({
      days_back: exportDaysBack.toString(),
    });

    if (organizationId) {
      params.append('organization_id', organizationId.toString());
    }

    const response = await fetchWithAuth(`${API_BASE}/analytics/export/sla/excel?${params}`);
    return response.blob();
  };

  const exportErrors = async (exportDaysBack: number): Promise<Blob> => {
    const params = new URLSearchParams({
      days_back: exportDaysBack.toString(),
    });

    if (organizationId) {
      params.append('organization_id', organizationId.toString());
    }

    const response = await fetchWithAuth(`${API_BASE}/analytics/export/errors/csv?${params}`);
    return response.blob();
  };

  useEffect(() => {
    fetchDashboardData();
  }, [organizationId, daysBack]);

  return {
    dashboardData,
    isLoading,
    error,
    exportDashboard,
    exportInspections,
    exportSLA,
    exportErrors,
  };
};