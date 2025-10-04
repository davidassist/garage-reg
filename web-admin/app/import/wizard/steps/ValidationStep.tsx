'use client'

import { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'
import { 
  ImportSession, 
  ImportRowData,
} from '@/lib/types/import'
import { DataValidator } from '@/lib/import/utils'
import { 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Eye,
  Download,
  Filter,
  Search
} from 'lucide-react'

interface ValidationStepProps {
  session: ImportSession
  onComplete: (session: ImportSession) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export function ValidationStep({ 
  session, 
  onComplete, 
  isLoading, 
  setIsLoading 
}: ValidationStepProps) {
  const [validatedRows, setValidatedRows] = useState<ImportRowData[]>([])
  const [validationComplete, setValidationComplete] = useState(false)
  const [filter, setFilter] = useState<'all' | 'valid' | 'invalid' | 'warnings'>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(20)

  useEffect(() => {
    performValidation()
  }, [session])

  const performValidation = async () => {
    setIsLoading(true)
    setValidationComplete(false)

    try {
      // Load parsed data from session storage
      const storedData = sessionStorage.getItem(`import-data-${session.id}`)
      if (!storedData) {
        throw new Error('Nem található importálandó adat')
      }

      const parsedData = JSON.parse(storedData)
      
      // Apply column mappings to transform data
      const mappedData = parsedData.data.map((row: any) => {
        const mappedRow: Record<string, any> = {}
        
        session.columnMappings.forEach(mapping => {
          mappedRow[mapping.targetField] = row[mapping.sourceColumn] || ''
        })
        
        return mappedRow
      })

      // Validate all rows
      const validated = DataValidator.validateAllRows(mappedData, session.entityType)
      
      setValidatedRows(validated)
      setValidationComplete(true)
      
      const validCount = validated.filter(row => row.isValid).length
      const invalidCount = validated.filter(row => !row.isValid).length
      const warningsCount = validated.reduce((sum, row) => sum + row.warnings.length, 0)
      
      toast.success(`Validáció kész: ${validCount} érvényes, ${invalidCount} hibás, ${warningsCount} figyelmeztetés`)
      
    } catch (error) {
      toast.error(`Validációs hiba: ${error}`)
      console.error('Validation error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getFilteredRows = () => {
    let filtered = validatedRows

    // Apply status filter
    switch (filter) {
      case 'valid':
        filtered = filtered.filter(row => row.isValid)
        break
      case 'invalid':
        filtered = filtered.filter(row => !row.isValid)
        break
      case 'warnings':
        filtered = filtered.filter(row => row.warnings.length > 0)
        break
    }

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(row => {
        const rowValues = Object.values(row.data).join(' ').toLowerCase()
        const errorMessages = row.errors.map(e => e.message).join(' ').toLowerCase()
        const warningMessages = row.warnings.map(w => w.message).join(' ').toLowerCase()
        
        return rowValues.includes(term) || 
               errorMessages.includes(term) || 
               warningMessages.includes(term)
      })
    }

    return filtered
  }

  const getPaginatedRows = () => {
    const filtered = getFilteredRows()
    const startIndex = (currentPage - 1) * pageSize
    return filtered.slice(startIndex, startIndex + pageSize)
  }

  const getTotalPages = () => {
    return Math.ceil(getFilteredRows().length / pageSize)
  }

  const getStatistics = () => {
    const total = validatedRows.length
    const valid = validatedRows.filter(row => row.isValid).length
    const invalid = validatedRows.filter(row => !row.isValid).length
    const withWarnings = validatedRows.filter(row => row.warnings.length > 0).length
    
    return { total, valid, invalid, withWarnings }
  }

  const handleContinue = () => {
    const stats = getStatistics()
    
    const updatedSession: ImportSession = {
      ...session,
      currentStep: 'preview',
      validatedRows,
      validRowsCount: stats.valid,
      invalidRowsCount: stats.invalid,
      warningsCount: validatedRows.reduce((sum, row) => sum + row.warnings.length, 0),
      updatedAt: new Date(),
    }

    onComplete(updatedSession)
  }

  const stats = getStatistics()
  const filteredRows = getPaginatedRows()

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">
          Adatok ellenőrzése
        </h2>
        <p className="mt-2 text-gray-600">
          Minden sor validálásra kerül az üzleti szabályok szerint
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <Eye className="h-5 w-5 text-blue-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-blue-900">Összes sor</p>
              <p className="text-lg font-semibold text-blue-700">{stats.total}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-green-900">Érvényes</p>
              <p className="text-lg font-semibold text-green-700">{stats.valid}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <XCircle className="h-5 w-5 text-red-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-red-900">Hibás</p>
              <p className="text-lg font-semibold text-red-700">{stats.invalid}</p>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-yellow-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-yellow-900">Figyelmeztetés</p>
              <p className="text-lg font-semibold text-yellow-700">{stats.withWarnings}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Validation Progress */}
      {!validationComplete && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            <div>
              <p className="text-sm font-medium text-blue-900">Validáció folyamatban...</p>
              <p className="text-sm text-blue-700">Sorok ellenőrzése az üzleti szabályok szerint</p>
            </div>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      {validationComplete && (
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Szűrés:</span>
            </div>
            
            <select
              value={filter}
              onChange={(e) => {
                setFilter(e.target.value as any)
                setCurrentPage(1)
              }}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Minden sor ({stats.total})</option>
              <option value="valid">Érvényes ({stats.valid})</option>
              <option value="invalid">Hibás ({stats.invalid})</option>
              <option value="warnings">Figyelmeztetéssel ({stats.withWarnings})</option>
            </select>
          </div>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Keresés..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
                setCurrentPage(1)
              }}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      )}

      {/* Data Table */}
      {validationComplete && (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sor
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Állapot
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Adatok (részlet)
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Hibák / Figyelmeztetések
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredRows.map((row) => (
                  <tr
                    key={row.rowIndex}
                    className={`
                      ${!row.isValid ? 'bg-red-50' : row.warnings.length > 0 ? 'bg-yellow-50' : 'bg-white'}
                    `}
                  >
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {row.rowIndex + 1}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {!row.isValid ? (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
                          <XCircle className="h-3 w-3 mr-1" />
                          Hibás
                        </span>
                      ) : row.warnings.length > 0 ? (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                          <AlertTriangle className="h-3 w-3 mr-1" />
                          Figyelmeztetés
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Érvényes
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      <div className="max-w-xs truncate">
                        {Object.entries(row.data)
                          .slice(0, 3)
                          .map(([key, value]) => `${key}: ${value}`)
                          .join(', ')
                        }
                        {Object.keys(row.data).length > 3 && '...'}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="space-y-1 max-w-md">
                        {row.errors.map((error, idx) => (
                          <div key={idx} className="text-red-700 text-xs">
                            <strong>{error.field}:</strong> {error.message}
                          </div>
                        ))}
                        {row.warnings.map((warning, idx) => (
                          <div key={idx} className="text-yellow-700 text-xs">
                            <strong>{warning.field}:</strong> {warning.message}
                          </div>
                        ))}
                        {row.errors.length === 0 && row.warnings.length === 0 && (
                          <span className="text-green-600 text-xs">Hibátlan</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {getTotalPages() > 1 && (
            <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Oldalak: {currentPage} / {getTotalPages()} 
                ({getFilteredRows().length} sor)
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50 hover:bg-gray-50"
                >
                  Előző
                </button>
                <button
                  onClick={() => setCurrentPage(Math.min(getTotalPages(), currentPage + 1))}
                  disabled={currentPage === getTotalPages()}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50 hover:bg-gray-50"
                >
                  Következő
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      {validationComplete && (
        <div className="flex justify-between">
          <div>
            {stats.invalid > 0 && (
              <button
                onClick={performValidation}
                disabled={isLoading}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-700 bg-blue-100 hover:bg-blue-200 rounded-md disabled:opacity-50"
              >
                Újra validálás
              </button>
            )}
          </div>

          <button
            onClick={handleContinue}
            disabled={isLoading}
            className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            Folytatás: Előnézet
          </button>
        </div>
      )}
    </div>
  )
}