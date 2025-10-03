'use client'

import { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'
import { 
  ImportSession, 
  ColumnMapping,
} from '@/lib/types/import'
import { getTemplate, getRequiredFields, getOptionalFields } from '@/lib/import/templates'
import { 
  ArrowRight, 
  AlertTriangle, 
  Check, 
  X,
  Info,
  MapPin
} from 'lucide-react'

interface ColumnMappingStepProps {
  session: ImportSession
  onComplete: (session: ImportSession) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export function ColumnMappingStep({ 
  session, 
  onComplete, 
  isLoading, 
  setIsLoading 
}: ColumnMappingStepProps) {
  const [mappings, setMappings] = useState<ColumnMapping[]>([])
  const [sourceColumns, setSourceColumns] = useState<string[]>([])
  const [autoMappingApplied, setAutoMappingApplied] = useState(false)

  const template = getTemplate(session.entityType)
  const requiredFields = getRequiredFields(session.entityType)
  const optionalFields = getOptionalFields(session.entityType)

  useEffect(() => {
    // Load parsed data from session storage
    const storedData = sessionStorage.getItem(`import-data-${session.id}`)
    if (storedData) {
      const parsedData = JSON.parse(storedData)
      setSourceColumns(parsedData.headers || [])
    }
  }, [session.id])

  useEffect(() => {
    // Apply automatic mapping on first load
    if (sourceColumns.length > 0 && !autoMappingApplied) {
      applyAutoMapping()
      setAutoMappingApplied(true)
    }
  }, [sourceColumns, autoMappingApplied])

  const applyAutoMapping = () => {
    const autoMappings: ColumnMapping[] = []
    
    template.fields.forEach(field => {
      // Try to find exact match first
      let matchedColumn = sourceColumns.find(col => 
        col.toLowerCase() === field.name.toLowerCase() ||
        col.toLowerCase() === field.key.toLowerCase()
      )
      
      // Try partial matches
      if (!matchedColumn) {
        matchedColumn = sourceColumns.find(col => {
          const colLower = col.toLowerCase()
          const fieldNameLower = field.name.toLowerCase()
          const fieldKeyLower = field.key.toLowerCase()
          
          return colLower.includes(fieldNameLower) || 
                 colLower.includes(fieldKeyLower) ||
                 fieldNameLower.includes(colLower) ||
                 fieldKeyLower.includes(colLower)
        })
      }
      
      if (matchedColumn) {
        autoMappings.push({
          sourceColumn: matchedColumn,
          targetField: field.key,
          required: field.required,
        })
      }
    })
    
    setMappings(autoMappings)
    
    if (autoMappings.length > 0) {
      toast.success(`Automatikus hozzárendelés: ${autoMappings.length} mező`)
    }
  }

  const updateMapping = (targetField: string, sourceColumn: string) => {
    setMappings(prev => {
      const existing = prev.find(m => m.targetField === targetField)
      const field = template.fields.find(f => f.key === targetField)
      
      if (existing) {
        if (sourceColumn === '') {
          // Remove mapping
          return prev.filter(m => m.targetField !== targetField)
        } else {
          // Update mapping
          return prev.map(m => 
            m.targetField === targetField 
              ? { ...m, sourceColumn }
              : m
          )
        }
      } else if (sourceColumn !== '') {
        // Add new mapping
        return [
          ...prev,
          {
            sourceColumn,
            targetField,
            required: field?.required || false,
          }
        ]
      }
      
      return prev
    })
  }

  const getMappingForField = (targetField: string): string => {
    const mapping = mappings.find(m => m.targetField === targetField)
    return mapping?.sourceColumn || ''
  }

  const getUnmappedRequiredFields = (): string[] => {
    return requiredFields
      .filter(field => !mappings.some(m => m.targetField === field.key))
      .map(field => field.name)
  }

  const getUsedSourceColumns = (): string[] => {
    return mappings.map(m => m.sourceColumn)
  }

  const getUnusedSourceColumns = (): string[] => {
    const used = getUsedSourceColumns()
    return sourceColumns.filter(col => !used.includes(col))
  }

  const canContinue = (): boolean => {
    const unmappedRequired = getUnmappedRequiredFields()
    return unmappedRequired.length === 0
  }

  const handleContinue = () => {
    if (!canContinue()) {
      toast.error('Minden kötelező mező hozzárendelése szükséges')
      return
    }

    const updatedSession: ImportSession = {
      ...session,
      currentStep: 'validation',
      columnMappings: mappings,
      updatedAt: new Date(),
    }

    onComplete(updatedSession)
  }

  const resetMappings = () => {
    setMappings([])
    toast('Hozzárendelések törölve', { icon: 'ℹ️' })
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">
          Mezők hozzárendelése
        </h2>
        <p className="mt-2 text-gray-600">
          Rendelje hozzá a CSV/Excel oszlopokat a megfelelő adatmezőkhöz
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <MapPin className="h-5 w-5 text-blue-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-blue-900">Hozzárendelt</p>
              <p className="text-lg font-semibold text-blue-700">{mappings.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-yellow-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-yellow-900">Hiányzó kötelező</p>
              <p className="text-lg font-semibold text-yellow-700">
                {getUnmappedRequiredFields().length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-center">
            <Info className="h-5 w-5 text-gray-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-gray-900">Fel nem használt</p>
              <p className="text-lg font-semibold text-gray-700">
                {getUnusedSourceColumns().length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <Check className="h-5 w-5 text-green-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-green-900">Kész az importra</p>
              <p className="text-lg font-semibold text-green-700">
                {canContinue() ? 'Igen' : 'Nem'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center">
        <button
          onClick={applyAutoMapping}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-700 bg-blue-100 hover:bg-blue-200 rounded-md disabled:opacity-50"
        >
          Automatikus hozzárendelés
        </button>
        
        <button
          onClick={resetMappings}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md disabled:opacity-50"
        >
          <X className="h-4 w-4 mr-1" />
          Törlés
        </button>
      </div>

      {/* Required Fields */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
          Kötelező mezők
        </h3>
        
        <div className="space-y-3">
          {requiredFields.map(field => {
            const currentMapping = getMappingForField(field.key)
            const isMapped = currentMapping !== ''
            
            return (
              <div
                key={field.key}
                className={`
                  border rounded-lg p-4 transition-colors
                  ${isMapped 
                    ? 'border-green-200 bg-green-50' 
                    : 'border-red-200 bg-red-50'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <div>
                        <h4 className="font-medium text-gray-900">{field.name}</h4>
                        <p className="text-sm text-gray-600">{field.description}</p>
                        {field.example && (
                          <p className="text-xs text-gray-500">Példa: {field.example}</p>
                        )}
                      </div>
                      
                      <ArrowRight className="h-5 w-5 text-gray-400" />
                      
                      <div className="min-w-0 flex-1">
                        <select
                          value={currentMapping}
                          onChange={(e) => updateMapping(field.key, e.target.value)}
                          className={`
                            w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2
                            ${isMapped 
                              ? 'border-green-300 focus:ring-green-500 focus:border-transparent' 
                              : 'border-red-300 focus:ring-red-500 focus:border-transparent'
                            }
                          `}
                        >
                          <option value="">-- Válassz oszlopot --</option>
                          {sourceColumns.map(column => (
                            <option key={column} value={column}>
                              {column}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                  
                  <div className="ml-4">
                    {isMapped ? (
                      <Check className="h-5 w-5 text-green-500" />
                    ) : (
                      <X className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Optional Fields */}
      {optionalFields.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <Info className="h-5 w-5 text-blue-500 mr-2" />
            Opcionális mezők
          </h3>
          
          <div className="space-y-3">
            {optionalFields.map(field => {
              const currentMapping = getMappingForField(field.key)
              const isMapped = currentMapping !== ''
              
              return (
                <div
                  key={field.key}
                  className="border border-gray-200 rounded-lg p-4 bg-white"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <div>
                          <h4 className="font-medium text-gray-900">{field.name}</h4>
                          <p className="text-sm text-gray-600">{field.description}</p>
                          {field.example && (
                            <p className="text-xs text-gray-500">Példa: {field.example}</p>
                          )}
                        </div>
                        
                        <ArrowRight className="h-5 w-5 text-gray-400" />
                        
                        <div className="min-w-0 flex-1">
                          <select
                            value={currentMapping}
                            onChange={(e) => updateMapping(field.key, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="">-- Nincs hozzárendelve --</option>
                            {sourceColumns.map(column => (
                              <option key={column} value={column}>
                                {column}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>
                    
                    <div className="ml-4">
                      {isMapped ? (
                        <Check className="h-5 w-5 text-blue-500" />
                      ) : (
                        <div className="h-5 w-5" />
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Unused Columns Warning */}
      {getUnusedSourceColumns().length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-yellow-900">
                Fel nem használt oszlopok
              </h3>
              <p className="mt-1 text-sm text-yellow-700">
                A következő oszlopok nem lesznek importálva:
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                {getUnusedSourceColumns().map(column => (
                  <span
                    key={column}
                    className="inline-flex items-center px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded"
                  >
                    {column}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Missing Required Fields Warning */}
      {getUnmappedRequiredFields().length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <X className="h-5 w-5 text-red-600 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-900">
                Hiányzó kötelező mezők
              </h3>
              <p className="mt-1 text-sm text-red-700">
                A következő kötelező mezők még nincsenek hozzárendelve:
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                {getUnmappedRequiredFields().map(fieldName => (
                  <span
                    key={fieldName}
                    className="inline-flex items-center px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded"
                  >
                    {fieldName}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Continue Button */}
      <div className="flex justify-end">
        <button
          onClick={handleContinue}
          disabled={isLoading || !canContinue()}
          className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {canContinue() 
            ? 'Folytatás: Adatok ellenőrzése' 
            : `${getUnmappedRequiredFields().length} kötelező mező hiányzik`
          }
        </button>
      </div>
    </div>
  )
}