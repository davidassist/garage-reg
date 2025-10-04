// Dynamic Form Engine Components
export { DynamicFormEngine, createDefaultFormData, validateFormTemplate } from './DynamicFormEngine'

// Individual Field Components
export { BoolSwitchItem } from './BoolSwitchItem'
export { EnumItem } from './EnumItem'
export { NumberWithRange } from './NumberWithRange'
export { PhotoItem } from './PhotoItem'
export { NoteItem } from './NoteItem'

// Type definitions (re-export from types)
export type {
  FormTemplate,
  DynamicField,
  FormData,
  ValidationResult,
  BoolField,
  EnumField,
  NumberField,
  PhotoField,
  NoteField,
  FieldComponentProps
} from '@/lib/types/dynamic-forms'

// Import components for registry
import { BoolSwitchItem } from './BoolSwitchItem'
import { EnumItem } from './EnumItem'
import { NumberWithRange } from './NumberWithRange'
import { PhotoItem } from './PhotoItem'
import { NoteItem } from './NoteItem'

// Field component registry for extensibility
export const FIELD_COMPONENTS = {
  boolean: {
    component: BoolSwitchItem,
    getDefaultValue: BoolSwitchItem.getDefaultValue,
    validate: BoolSwitchItem.validate
  },
  enum: {
    component: EnumItem,
    getDefaultValue: EnumItem.getDefaultValue,
    validate: EnumItem.validate
  },
  number: {
    component: NumberWithRange,
    getDefaultValue: NumberWithRange.getDefaultValue,
    validate: NumberWithRange.validate
  },
  photo: {
    component: PhotoItem,
    getDefaultValue: PhotoItem.getDefaultValue,
    validate: PhotoItem.validate
  },
  note: {
    component: NoteItem,
    getDefaultValue: NoteItem.getDefaultValue,
    validate: NoteItem.validate
  }
} as const

export type FieldType = keyof typeof FIELD_COMPONENTS