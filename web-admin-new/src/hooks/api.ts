import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type {
  Client,
  Site,
  Building,
  Gate,
  Inspection,
  WorkOrder,
  DashboardStats,
  UpcomingInspection,
  ClientFormData,
  SiteFormData,
  BuildingFormData,
  GateFormData,
  PaginatedResponse,
} from '@/types/api'

// Query Keys
export const queryKeys = {
  // Dashboard
  dashboardStats: ['dashboard', 'stats'] as const,
  upcomingInspections: ['dashboard', 'upcoming-inspections'] as const,
  
  // Clients
  clients: (page?: number, perPage?: number) => ['clients', page, perPage] as const,
  client: (id: number) => ['clients', id] as const,
  
  // Sites
  sites: (clientId?: number, page?: number, perPage?: number) => ['sites', clientId, page, perPage] as const,
  site: (id: number) => ['sites', id] as const,
  
  // Buildings
  buildings: (siteId?: number, page?: number, perPage?: number) => ['buildings', siteId, page, perPage] as const,
  building: (id: number) => ['buildings', id] as const,
  
  // Gates
  gates: (buildingId?: number, page?: number, perPage?: number) => ['gates', buildingId, page, perPage] as const,
  gate: (id: number) => ['gates', id] as const,
  
  // Inspections
  inspections: (gateId?: number, page?: number, perPage?: number) => ['inspections', gateId, page, perPage] as const,
  
  // Work Orders
  workOrders: (gateId?: number, page?: number, perPage?: number) => ['work-orders', gateId, page, perPage] as const,
}

// Dashboard Hooks
export function useDashboardStats() {
  return useQuery({
    queryKey: queryKeys.dashboardStats,
    queryFn: () => apiClient.getDashboardStats(),
  })
}

export function useUpcomingInspections() {
  return useQuery({
    queryKey: queryKeys.upcomingInspections,
    queryFn: () => apiClient.getUpcomingInspections(),
  })
}

// Client Hooks
export function useClients(page = 1, perPage = 20) {
  return useQuery({
    queryKey: queryKeys.clients(page, perPage),
    queryFn: () => apiClient.getClients(page, perPage),
  })
}

export function useClient(id: number) {
  return useQuery({
    queryKey: queryKeys.client(id),
    queryFn: () => apiClient.getClient(id),
    enabled: !!id,
  })
}

export function useCreateClient() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: ClientFormData) => apiClient.createClient(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] })
    },
  })
}

export function useUpdateClient() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ClientFormData> }) =>
      apiClient.updateClient(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['clients'] })
      queryClient.invalidateQueries({ queryKey: queryKeys.client(id) })
    },
  })
}

export function useDeleteClient() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => apiClient.deleteClient(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] })
    },
  })
}

// Site Hooks
export function useSites(clientId?: number, page = 1, perPage = 20) {
  return useQuery({
    queryKey: queryKeys.sites(clientId, page, perPage),
    queryFn: () => apiClient.getSites(clientId, page, perPage),
  })
}

export function useSite(id: number) {
  return useQuery({
    queryKey: queryKeys.site(id),
    queryFn: () => apiClient.getSite(id),
    enabled: !!id,
  })
}

export function useCreateSite() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: SiteFormData) => apiClient.createSite(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sites'] })
    },
  })
}

export function useUpdateSite() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<SiteFormData> }) =>
      apiClient.updateSite(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['sites'] })
      queryClient.invalidateQueries({ queryKey: queryKeys.site(id) })
    },
  })
}

export function useDeleteSite() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => apiClient.deleteSite(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sites'] })
    },
  })
}

// Building Hooks
export function useBuildings(siteId?: number, page = 1, perPage = 20) {
  return useQuery({
    queryKey: queryKeys.buildings(siteId, page, perPage),
    queryFn: () => apiClient.getBuildings(siteId, page, perPage),
  })
}

export function useBuilding(id: number) {
  return useQuery({
    queryKey: queryKeys.building(id),
    queryFn: () => apiClient.getBuilding(id),
    enabled: !!id,
  })
}

export function useCreateBuilding() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: BuildingFormData) => apiClient.createBuilding(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['buildings'] })
    },
  })
}

export function useUpdateBuilding() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<BuildingFormData> }) =>
      apiClient.updateBuilding(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['buildings'] })
      queryClient.invalidateQueries({ queryKey: queryKeys.building(id) })
    },
  })
}

export function useDeleteBuilding() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => apiClient.deleteBuilding(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['buildings'] })
    },
  })
}

// Gate Hooks
export function useGates(buildingId?: number, page = 1, perPage = 20) {
  return useQuery({
    queryKey: queryKeys.gates(buildingId, page, perPage),
    queryFn: () => apiClient.getGates(buildingId, page, perPage),
  })
}

export function useGate(id: number) {
  return useQuery({
    queryKey: queryKeys.gate(id),
    queryFn: () => apiClient.getGate(id),
    enabled: !!id,
  })
}

export function useCreateGate() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: GateFormData) => apiClient.createGate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gates'] })
    },
  })
}

export function useUpdateGate() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<GateFormData> }) =>
      apiClient.updateGate(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['gates'] })
      queryClient.invalidateQueries({ queryKey: queryKeys.gate(id) })
    },
  })
}

export function useDeleteGate() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => apiClient.deleteGate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gates'] })
    },
  })
}

// Inspection Hooks
export function useInspections(gateId?: number, page = 1, perPage = 20) {
  return useQuery({
    queryKey: queryKeys.inspections(gateId, page, perPage),
    queryFn: () => apiClient.getInspections(gateId, page, perPage),
  })
}

// Work Order Hooks
export function useWorkOrders(gateId?: number, page = 1, perPage = 20) {
  return useQuery({
    queryKey: queryKeys.workOrders(gateId, page, perPage),
    queryFn: () => apiClient.getWorkOrders(gateId, page, perPage),
  })
}