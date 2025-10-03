// Dynamic form components
export { DynamicFormRenderer } from './DynamicFormRenderer'
export * from './fields'

// Re-export types and services for convenience
export type { 
  FormTemplate, 
  FormField, 
  BooleanSwitchField,
  EnumSelectField,
  NumberRangeField,
  PhotoUploadField,
  TextNoteField
} from '@/lib/types/dynamic-form'

export { DynamicFormEngine } from '@/lib/services/dynamic-form-engine'