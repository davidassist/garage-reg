export type ImportType = 'gates' | 'sites' | 'users' | 'inspections'

export interface FieldMapping {
  csvField: string
  targetField: string | null
  isRequired: boolean
  dataType: 'string' | 'number' | 'date' | 'email' | 'phone' | 'enum'
  enumValues?: string[]
  sample?: string
}

export interface ValidationResult {
  isValid: boolean
  errors: ValidationError[]
  warnings: ValidationWarning[]
}

export interface ValidationError {
  row: number
  field: string
  message: string
  value: any
}

export interface ValidationWarning {
  row: number
  field: string
  message: string
  value: any
}

export interface ProcessedRow {
  rowIndex: number
  originalData: any
  processedData: any
  validation: ValidationResult
}

export interface Step {
  id: string
  title: string
  description: string
  status: 'pending' | 'current' | 'completed' | 'error'
}