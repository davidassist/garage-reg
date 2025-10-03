export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  display_name?: string
  is_active: boolean
  created_at: string
  updated_at: string
  roles: Role[]
  permissions: Permission[]
}

export interface Role {
  id: number
  name: string
  display_name: string
  description?: string
  permissions: Permission[]
}

export interface Permission {
  id: number
  name: string
  resource: string
  action: string
  description?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Client {
  id: number
  name: string
  display_name?: string
  contact_email?: string
  contact_phone?: string
  address?: string
  is_active: boolean
  created_at: string
  updated_at: string
  sites: Site[]
}

export interface Site {
  id: number
  client_id: number
  name: string
  display_name?: string
  address?: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
  client?: Client
  buildings: Building[]
}

export interface Building {
  id: number
  site_id: number
  name: string
  display_name?: string
  description?: string
  floor_count?: number
  total_area?: number
  is_active: boolean
  created_at: string
  updated_at: string
  site?: Site
  gates: Gate[]
}

export interface Gate {
  id: number
  building_id: number
  name: string
  display_name?: string
  gate_type?: string
  manufacturer?: string
  model?: string
  serial_number?: string
  installation_date?: string
  warranty_expiry?: string
  location_description?: string
  is_active: boolean
  created_at: string
  updated_at: string
  building?: Building
  inspections: Inspection[]
  work_orders: WorkOrder[]
}

export interface Inspection {
  id: number
  gate_id: number
  inspector_id: number
  inspection_type: string
  inspection_date: string
  next_inspection_date?: string
  status: 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
  overall_result?: 'PASS' | 'FAIL' | 'CONDITIONAL'
  findings?: string
  recommendations?: string
  completion_percentage?: number
  duration_minutes?: number
  created_at: string
  updated_at: string
  gate?: Gate
  inspector?: User
}

export interface WorkOrder {
  id: number
  gate_id: number
  assigned_to?: number
  work_order_number: string
  title: string
  description: string
  work_type?: string
  work_category?: string
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  status: 'DRAFT' | 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
  scheduled_start?: string
  scheduled_end?: string
  actual_start?: string
  actual_end?: string
  estimated_hours?: number
  actual_hours?: number
  created_at: string
  updated_at: string
  gate?: Gate
  assignee?: User
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface ApiError {
  detail: string
  status_code: number
}

export interface DashboardStats {
  total_clients: number
  total_sites: number
  total_buildings: number
  total_gates: number
  pending_inspections: number
  overdue_inspections: number
  active_work_orders: number
  completed_this_month: number
}

export interface UpcomingInspection {
  id: number
  gate_name: string
  gate_location: string
  inspection_type: string
  due_date: string
  days_until_due: number
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  inspector_name?: string
}

// Form validation schemas
export interface LoginFormData {
  username: string
  password: string
}

export interface ClientFormData {
  name: string
  display_name?: string
  contact_email?: string
  contact_phone?: string
  address?: string
  is_active: boolean
}

export interface SiteFormData {
  client_id: number
  name: string
  display_name?: string
  address?: string
  description?: string
  is_active: boolean
}

export interface BuildingFormData {
  site_id: number
  name: string
  display_name?: string
  description?: string
  floor_count?: number
  total_area?: number
  is_active: boolean
}

export interface GateFormData {
  building_id: number
  name: string
  display_name?: string
  gate_type?: string
  manufacturer?: string
  model?: string
  serial_number?: string
  installation_date?: string
  warranty_expiry?: string
  location_description?: string
  is_active: boolean
}