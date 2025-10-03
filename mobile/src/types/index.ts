/**
 * Core Types for Mobile App
 */

// Auth Types
export interface User {
  id: string
  username: string
  email: string
  fullName: string
  roles: Role[]
  permissions: string[]
  lastLogin: string
}

export interface Role {
  id: string
  name: string
  permissions: string[]
}

export interface AuthCredentials {
  username: string
  password: string
}

export interface AuthResponse {
  user: User
  token: string
  refreshToken: string
  expiresIn: number
}

// Gate Types
export interface Gate {
  id: string
  name: string
  gateCode: string
  location: string
  buildingId: string
  buildingName: string
  siteId: string
  siteName: string
  clientId: string
  clientName: string
  gateType: GateType
  status: GateStatus
  manufacturer: string
  model: string
  serialNumber: string
  installationDate: string
  lastMaintenance?: string
  nextMaintenance: string
  qrCode: string
  coordinates?: {
    latitude: number
    longitude: number
  }
  metadata?: Record<string, any>
  syncStatus: SyncStatus
  lastSyncAt?: string
  createdAt: string
  updatedAt: string
  // Delta sync versioning fields
  rowVersion: number
  etag?: string
  localChanges?: DeltaOperation[]
  serverVersion: number
  conflictResolutionStrategy: ConflictResolutionStrategy
}

export type GateType = 'entry' | 'exit' | 'bidirectional' | 'emergency'
export type GateStatus = 'active' | 'inactive' | 'maintenance' | 'error'

// Inspection Types
export interface Inspection {
  id: string
  gateId: string
  templateId: string
  templateName: string
  inspectorId: string
  inspectorName: string
  status: InspectionStatus
  priority: InspectionPriority
  scheduledDate: string
  startedAt?: string
  completedAt?: string
  estimatedDuration: number // minutes
  actualDuration?: number
  location: string
  weather?: string
  notes?: string
  photos: InspectionPhoto[]
  checklist: ChecklistItem[]
  signature?: string
  syncStatus: SyncStatus
  createdAt: string
  updatedAt: string
  lastSyncAt?: string
}

export type InspectionStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'overdue'
export type InspectionPriority = 'low' | 'normal' | 'high' | 'urgent'

// Checklist Types
export interface ChecklistTemplate {
  id: string
  name: string
  description: string
  category: string
  version: string
  items: ChecklistTemplateItem[]
  estimatedDuration: number
  isActive: boolean
  createdAt: string
  updatedAt: string
  syncStatus: SyncStatus
}

export interface ChecklistTemplateItem {
  id: string
  title: string
  description?: string
  type: ChecklistItemType
  required: boolean
  order: number
  options?: ChecklistOption[]
  validationRules?: ValidationRule[]
}

export interface ChecklistItem {
  id: string
  templateItemId: string
  title: string
  type: ChecklistItemType
  required: boolean
  status: ChecklistItemStatus
  value?: any
  notes?: string
  photos: string[] // photo IDs
  completedAt?: string
  completedBy?: string
}

export type ChecklistItemType = 'boolean' | 'text' | 'number' | 'select' | 'multiselect' | 'photo' | 'signature'
export type ChecklistItemStatus = 'pending' | 'completed' | 'skipped' | 'failed'

export interface ChecklistOption {
  value: string
  label: string
  color?: string
  requiresNote?: boolean
}

export interface ValidationRule {
  type: 'required' | 'min' | 'max' | 'pattern'
  value?: any
  message: string
}

// Photo Types
export interface InspectionPhoto {
  id: string
  inspectionId: string
  checklistItemId?: string
  uri: string // local file path
  remoteUri?: string // server URL after upload
  fileName: string
  size: number
  mimeType: string
  timestamp: string
  description?: string
  location?: {
    latitude: number
    longitude: number
  }
  uploadStatus: UploadStatus
  attempts: number
  lastAttemptAt?: string
  errorMessage?: string
}

export type UploadStatus = 'pending' | 'uploading' | 'completed' | 'failed' | 'cancelled'

// Sync Types
export type SyncStatus = 'synced' | 'pending' | 'syncing' | 'conflict' | 'error'

export interface SyncConflict {
  id: string
  entityType: 'inspection' | 'photo' | 'gate'
  entityId: string
  field: string
  localValue: any
  remoteValue: any
  localTimestamp: string
  remoteTimestamp: string
  resolution?: ConflictResolution
  resolvedAt?: string
  resolvedBy?: string
}

export type ConflictResolution = 'use_local' | 'use_remote' | 'merge' | 'manual'

// Network Types
export interface NetworkState {
  isConnected: boolean
  connectionType: string
  isWifiEnabled: boolean
  strength: number
}

// Queue Types
export interface QueueItem {
  id: string
  type: QueueItemType
  entityId: string
  action: QueueAction
  data: any
  priority: number
  attempts: number
  maxAttempts: number
  createdAt: string
  scheduledAt: string
  lastAttemptAt?: string
  errorMessage?: string
  status: QueueItemStatus
}

export type QueueItemType = 'inspection' | 'photo' | 'gate_data'
export type QueueAction = 'create' | 'update' | 'delete' | 'upload'
export type QueueItemStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'

// App State Types
export interface AppState {
  isAuthenticated: boolean
  user: User | null
  networkState: NetworkState
  syncState: {
    lastSyncAt?: string
    isSyncing: boolean
    pendingItems: number
    conflicts: SyncConflict[]
  }
  settings: AppSettings
}

export interface AppSettings {
  theme: 'light' | 'dark'
  language: 'en' | 'hu'
  autoSync: boolean
  syncOnWifiOnly: boolean
  photoQuality: 'low' | 'medium' | 'high'
  cacheExpiration: number // hours
  maxOfflineDays: number
}

// ============================================================================
// DELTA SYNC TYPES
// ============================================================================

export interface DeltaOperation {
  id: string
  entityType: 'gate' | 'inspection' | 'photo' | 'template'
  entityId: string
  operationType: 'create' | 'update' | 'delete'
  fieldName?: string
  oldValue?: any
  newValue?: any
  rowVersion: number
  timestamp: string
  userId?: string
  syncStatus: 'pending' | 'synced' | 'conflicted'
  batchId?: string
}

export interface SyncBatch {
  id: string
  type: 'pull' | 'push'
  status: 'pending' | 'processing' | 'completed' | 'failed'
  startedAt?: string
  completedAt?: string
  totalOperations: number
  successfulOperations: number
  failedOperations: number
  lastSyncToken?: string
  nextSyncToken?: string
  retryCount: number
  errorMessage?: string
  operations?: DeltaOperation[]
}

export type ConflictResolutionStrategy = 'last_write_wins' | 'operational_transform' | 'manual_resolution' | 'field_level_merge'

export interface DeltaSyncResult {
  success: boolean
  batchId: string
  syncedOperations: number
  conflicts: DeltaConflict[]
  nextSyncToken?: string
  errors: string[]
}

export interface DeltaConflict {
  id: string
  entityType: string
  entityId: string
  fieldName?: string
  localOperation: DeltaOperation
  remoteOperation: DeltaOperation
  resolutionStrategy: ConflictResolutionStrategy
  resolvedValue?: any
  resolvedAt?: string
  resolvedBy?: string
}

export interface SyncPolicy {
  batchSize: number
  maxRetries: number
  retryDelayMs: number
  maxRetryDelayMs: number
  backoffMultiplier: number
  conflictResolution: ConflictResolutionStrategy
  enableOperationalTransform: boolean
}

// ============================================================================
// API AND AUTHENTICATION TYPES
// ============================================================================

export interface AuthToken {
  accessToken: string
  refreshToken: string
  expiresAt: string
  tokenType: string
}

export class APIError extends Error {
  public statusCode: number
  public response?: any

  constructor(message: string, statusCode: number, response?: any) {
    super(message)
    this.name = 'APIError'
    this.statusCode = statusCode
    this.response = response
  }
}