import { useAuthStore } from '@/stores/auth'
import type { User, Permission } from '@/types/api'

export type Resource = 
  | 'clients' 
  | 'sites' 
  | 'buildings' 
  | 'gates' 
  | 'inspections' 
  | 'work_orders' 
  | 'users' 
  | 'reports'

export type Action = 
  | 'create' 
  | 'read' 
  | 'update' 
  | 'delete' 
  | 'list' 
  | 'view_all'

export interface PermissionCheck {
  resource: Resource
  action: Action
}

export function hasPermission(
  user: User | null, 
  resource: Resource, 
  action: Action
): boolean {
  if (!user || !user.permissions) {
    return false
  }

  // Super admin has all permissions
  const hasAdminRole = user.roles?.some(role => role.name === 'admin')
  if (hasAdminRole) {
    return true
  }

  // Check specific permission
  return user.permissions.some(permission => 
    permission.resource === resource && permission.action === action
  )
}

export function hasAnyPermission(
  user: User | null, 
  checks: PermissionCheck[]
): boolean {
  if (!user) {
    return false
  }

  return checks.some(check => 
    hasPermission(user, check.resource, check.action)
  )
}

export function hasAllPermissions(
  user: User | null, 
  checks: PermissionCheck[]
): boolean {
  if (!user) {
    return false
  }

  return checks.every(check => 
    hasPermission(user, check.resource, check.action)
  )
}

export function usePermissions() {
  const { user } = useAuthStore()

  return {
    hasPermission: (resource: Resource, action: Action) => 
      hasPermission(user, resource, action),
    
    hasAnyPermission: (checks: PermissionCheck[]) => 
      hasAnyPermission(user, checks),
    
    hasAllPermissions: (checks: PermissionCheck[]) => 
      hasAllPermissions(user, checks),

    canCreateClient: () => hasPermission(user, 'clients', 'create'),
    canEditClient: () => hasPermission(user, 'clients', 'update'),
    canDeleteClient: () => hasPermission(user, 'clients', 'delete'),
    canViewClients: () => hasPermission(user, 'clients', 'read'),

    canCreateSite: () => hasPermission(user, 'sites', 'create'),
    canEditSite: () => hasPermission(user, 'sites', 'update'),
    canDeleteSite: () => hasPermission(user, 'sites', 'delete'),
    canViewSites: () => hasPermission(user, 'sites', 'read'),

    canCreateBuilding: () => hasPermission(user, 'buildings', 'create'),
    canEditBuilding: () => hasPermission(user, 'buildings', 'update'),
    canDeleteBuilding: () => hasPermission(user, 'buildings', 'delete'),
    canViewBuildings: () => hasPermission(user, 'buildings', 'read'),

    canCreateGate: () => hasPermission(user, 'gates', 'create'),
    canEditGate: () => hasPermission(user, 'gates', 'update'),
    canDeleteGate: () => hasPermission(user, 'gates', 'delete'),
    canViewGates: () => hasPermission(user, 'gates', 'read'),

    canViewInspections: () => hasPermission(user, 'inspections', 'read'),
    canViewWorkOrders: () => hasPermission(user, 'work_orders', 'read'),

    canViewReports: () => hasPermission(user, 'reports', 'read'),

    isAdmin: () => user?.roles?.some(role => role.name === 'admin') ?? false,
  }
}