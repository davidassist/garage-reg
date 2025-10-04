'use client'

import { useState, useMemo } from 'react'
import { 
  ImportSession, 
  ImportRowData,
} from '@/lib/types/import'
import { ExportUtils } from '@/lib/import/utils'
import { 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Download,
  Eye,
  FileText,
  Filter,
  BarChart3
} from 'lucide-react'

interface PreviewStepProps {
  session: ImportSession
  onComplete: (session: ImportSession) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export function PreviewStep({ 
  session, 
  onComplete, 
  isLoading, 
  setIsLoading 
}: PreviewStepProps) {
  const [showOnlyValid, setShowOnlyValid] = useState(true)
  const [previewLimit] = useState(10)

  const validatedRows = session.validatedRows || []

  const stats = useMemo(() => {
    const total = validatedRows.length
    const valid = validatedRows.filter(row => row.isValid).length
    const invalid = validatedRows.filter(row => !row.isValid).length
    const withWarnings = validatedRows.filter(row => row.warnings.length > 0).length
    
    return { total, valid, invalid, withWarnings }
  }, [validatedRows])

  const previewRows = useMemo(() => {
    const filtered = showOnlyValid 
      ? validatedRows.filter(row => row.isValid)
      : validatedRows
    
    return filtered.slice(0, previewLimit)
  }, [validatedRows, showOnlyValid, previewLimit])

  const getFieldNames = () => {
    if (previewRows.length === 0) return []
    return Object.keys(previewRows[0].data)
  }

  const handleDownloadErrorReport = async () => {
    try {
      setIsLoading(true)
      
      const errorRows = validatedRows.filter(row => !row.isValid)
      
      if (errorRows.length === 0) {
        alert('Nincsenek hibás sorok az exportáláshoz')
        return
      }

      // Prepare data for export with error details
      const exportData = errorRows.map(row => ({
        'Sor száma': row.rowIndex + 1,
        'Hibák': row.errors.map(e => `${e.field}: ${e.message}`).join('; '),
        'Figyelmeztetések': row.warnings.map(w => `${w.field}: ${w.message}`).join('; '),
        ...row.data
      }))

      await ExportUtils.downloadAsCSV(exportData, 'hibas_sorok_jelentes')
      
    } catch (error) {
      console.error('Error exporting error report:', error)
      alert('Hiba történt az exportálás során')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownloadValidData = async () => {
    try {
      setIsLoading(true)
      
      const validRows = validatedRows.filter(row => row.isValid)
      
      if (validRows.length === 0) {
        alert('Nincsenek érvényes sorok az exportáláshoz')
        return
      }

      const exportData = validRows.map(row => row.data)
      await ExportUtils.downloadAsCSV(exportData, 'ervenyesitett_adatok')
      
    } catch (error) {
      console.error('Error exporting valid data:', error)
      alert('Hiba történt az exportálás során')
    } finally {
      setIsLoading(false)
    }
  }

  const handleContinue = () => {
    const updatedSession: ImportSession = {
      ...session,
      currentStep: 'execute',
      updatedAt: new Date(),
    }

    onComplete(updatedSession)
  }

  const fieldNames = getFieldNames()

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">
          Import előnézet
        </h2>
        <p className="mt-2 text-gray-600">
          Ellenőrizze az importálandó adatok mintáját és a statisztikákat
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <BarChart3 className="h-5 w-5 text-blue-600 mr-2" />
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
              <p className="text-sm font-medium text-green-900">Importálható</p>
              <p className="text-lg font-semibold text-green-700">{stats.valid}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <XCircle className="h-5 w-5 text-red-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-red-900">Kihagyott</p>
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

      {/* Import Summary */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Import összesítő</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Import beállítások</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li><strong>Entitás típus:</strong> {session.entityType}</li>
              <li><strong>Fájl típus:</strong> {session.fileType}</li>
              <li><strong>Fájl név:</strong> {session.fileName}</li>
              <li><strong>Mezők száma:</strong> {session.columnMappings.length}</li>
              <li><strong>Létrehozva:</strong> {new Date(session.createdAt).toLocaleString('hu-HU')}</li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Validáció eredménye</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li><strong>Összes sor:</strong> {stats.total}</li>
              <li className="text-green-600"><strong>Sikeres sorok:</strong> {stats.valid}</li>
              <li className="text-red-600"><strong>Hibás sorok:</strong> {stats.invalid}</li>
              <li className="text-yellow-600"><strong>Figyelmeztetések:</strong> {stats.withWarnings}</li>
              <li><strong>Sikeres arány:</strong> {stats.total > 0 ? Math.round((stats.valid / stats.total) * 100) : 0}%</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Preview Controls */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Előnézet:</span>
          </div>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={showOnlyValid}
              onChange={(e) => setShowOnlyValid(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="ml-2 text-sm text-gray-700">
              Csak érvényes sorok ({stats.valid} db)
            </span>
          </label>
        </div>

        <div className="flex space-x-2">
          {stats.invalid > 0 && (
            <button
              onClick={handleDownloadErrorReport}
              disabled={isLoading}
              className="inline-flex items-center px-3 py-2 text-sm font-medium text-red-700 bg-red-100 hover:bg-red-200 rounded-md disabled:opacity-50"
            >
              <Download className="h-4 w-4 mr-2" />
              Hibás sorok letöltése
            </button>
          )}
          
          {stats.valid > 0 && (
            <button
              onClick={handleDownloadValidData}
              disabled={isLoading}
              className="inline-flex items-center px-3 py-2 text-sm font-medium text-green-700 bg-green-100 hover:bg-green-200 rounded-md disabled:opacity-50"
            >
              <Download className="h-4 w-4 mr-2" />
              Érvényes adatok letöltése
            </button>
          )}
        </div>
      </div>

      {/* Data Preview Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <h3 className="text-sm font-medium text-gray-900 flex items-center">
            <Eye className="h-4 w-4 mr-2" />
            Adatok előnézete (első {previewLimit} sor)
          </h3>
        </div>

        {previewRows.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>Nincsenek megjeleníthető sorok</p>
            {showOnlyValid && stats.valid === 0 && (
              <p className="text-sm mt-1">Próbálja ki az összes sor megjelenítését</p>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    #
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Állapot
                  </th>
                  {fieldNames.map((field) => (
                    <th 
                      key={field}
                      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {field}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {previewRows.map((row) => (
                  <tr 
                    key={row.rowIndex}
                    className={`
                      ${!row.isValid ? 'bg-red-50' : row.warnings.length > 0 ? 'bg-yellow-50' : 'bg-white'}
                    `}
                  >
                    <td className="px-4 py-3 text-sm text-gray-900 font-mono">
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
                          OK
                        </span>
                      )}
                    </td>
                    {fieldNames.map((field) => (
                      <td 
                        key={field} 
                        className="px-4 py-3 text-sm text-gray-900"
                      >
                        <div className="max-w-xs truncate" title={String(row.data[field] || '')}>
                          {String(row.data[field] || '')}
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Warnings */}
      {stats.valid === 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <XCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-red-900">
                Nincs importálható sor
              </h3>
              <p className="text-sm text-red-700 mt-1">
                Minden sor hibát tartalmazott. Kérjük, javítsa ki a hibákat és próbálja újra.
              </p>
            </div>
          </div>
        </div>
      )}

      {stats.invalid > stats.valid && stats.valid > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-yellow-900">
                Sok hibás sor található
              </h3>
              <p className="text-sm text-yellow-700 mt-1">
                A sorok több mint fele hibás ({stats.invalid}/{stats.total}). 
                Érdemes lehet javítani az adatokat importálás előtt.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <button
          onClick={() => {
            const updatedSession: ImportSession = {
              ...session,
              currentStep: 'validation',
            }
            onComplete(updatedSession)
          }}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
        >
          Vissza a validációhoz
        </button>

        <button
          onClick={handleContinue}
          disabled={isLoading || stats.valid === 0}
          className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          Import indítása ({stats.valid} sor)
        </button>
      </div>
    </div>
  )
}