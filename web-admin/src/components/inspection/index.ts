// Inspection System Components
export { InspectionManager } from './InspectionManager'
export { StartInspectionDialog } from './StartInspectionDialog'
export { InspectionFormRenderer } from './InspectionFormRenderer'
export { InspectionSummary } from './InspectionSummary'
export { UnsavedChangesWarning, UnsavedChangesWithBackup, useUnsavedChanges } from './UnsavedChangesWarning'

// Re-export types and services for convenience
export type {
  InspectionInstance,
  InspectionTemplate,
  InspectionStatus,
  InspectionPriority,
  FieldValue,
  StartInspectionRequest,
  InspectionFormState,
  AutoSaveState,
  UnsavedChangesState
} from '@/lib/types/inspection'

export { 
  INSPECTION_CATEGORIES,
  FIELD_TYPE_CONFIGS,
  STATUS_CONFIGS,
  PRIORITY_CONFIGS
} from '@/lib/types/inspection'

export { autoSaveService, useAutoSave } from '@/lib/services/inspection-autosave'