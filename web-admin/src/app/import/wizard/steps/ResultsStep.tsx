'use client'

import { useState } from 'react'
import { ImportSession } from '@/lib/types/import'
import { ExportUtils } from '@/lib/import/utils'
import { 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Download,
  FileText,
  Clock,
  BarChart3,
  RefreshCw,
  Home,
  Upload
} from 'lucide-react'

interface ResultsStepProps {
  session: ImportSession
  onComplete: (session: ImportSession) => void
  onRestart: () => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export function ResultsStep({ 
  session, 
  onComplete, 
  onRestart,
  isLoading, 
  setIsLoading 
}: ResultsStepProps) {
  const [isDownloading, setIsDownloading] = useState(false)

  const stats = session.importStats
  const errors = session.importErrors || []
  const validatedRows = session.validatedRows || []

  if (!stats) {
    return (
      <div className="p-6">
        <div className="text-center text-red-600">
          <XCircle className="h-12 w-12 mx-auto mb-3" />
          <p>Nincs elérhető import statisztika</p>
        </div>
      </div>
    )
  }

  const successRate = stats.totalRows > 0 
    ? Math.round((stats.successCount / stats.totalRows) * 100) 
    : 0

  const handleDownloadErrorReport = async () => {
    if (errors.length === 0) {
      alert('Nincsenek hibák a jelentésben')
      return
    }

    try {
      setIsDownloading(true)
      
      const errorData = errors.map((error, index) => ({
        'Hiba sorszám': index + 1,
        'Hibaüzenet': error,
        'Időpont': new Date().toISOString()
      }))

      await ExportUtils.downloadAsCSV(errorData, 'import_hibajelentes')
      
    } catch (error) {
      console.error('Error downloading report:', error)
      alert('Hiba történt a letöltés során')
    } finally {
      setIsDownloading(false)
    }
  }

  const handleDownloadFailedRows = async () => {
    const failedRows = validatedRows.filter(row => !row.isValid)
    
    if (failedRows.length === 0) {
      alert('Nincsenek sikertelen sorok')
      return
    }

    try {
      setIsDownloading(true)
      
      const failedData = failedRows.map(row => ({
        'Sor száma': row.rowIndex + 1,
        'Hibák': row.errors.map(e => `${e.field}: ${e.message}`).join('; '),
        'Figyelmeztetések': row.warnings.map(w => `${w.field}: ${w.message}`).join('; '),
        ...row.data
      }))

      await ExportUtils.downloadAsCSV(failedData, 'sikertelen_sorok')
      
    } catch (error) {
      console.error('Error downloading failed rows:', error)
      alert('Hiba történt a letöltés során')
    } finally {
      setIsDownloading(false)
    }
  }

  const formatDuration = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds} másodperc`
    } else {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes} perc ${remainingSeconds} másodperc`
    }
  }

  const getStatusColor = () => {
    if (stats.errorCount === 0) return 'green'
    if (stats.successCount > 0) return 'yellow'
    return 'red'
  }

  const getStatusIcon = () => {
    const color = getStatusColor()
    const className = "h-8 w-8"
    
    if (color === 'green') return <CheckCircle className={`${className} text-green-600`} />
    if (color === 'yellow') return <AlertTriangle className={`${className} text-yellow-600`} />
    return <XCircle className={`${className} text-red-600`} />
  }

  const getStatusMessage = () => {
    if (stats.errorCount === 0) return 'Import sikeresen befejezve'
    if (stats.successCount > 0) return 'Import részben sikeres'
    return 'Import sikertelen'
  }

  const getStatusDescription = () => {
    if (stats.errorCount === 0) {
      return 'Minden sor sikeresen importálva lett az adatbázisba.'
    }
    if (stats.successCount > 0) {
      return `${stats.successCount} sor sikeresen importálva, ${stats.errorCount} sor importálása sikertelen.`
    }
    return 'Egyetlen sor sem lett sikeresen importálva. Kérjük, ellenőrizze az adatokat és próbálja újra.'
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">
          Import eredmények
        </h2>
        <p className="mt-2 text-gray-600">
          Az import művelet befejezve - részletes eredmények és statisztikák
        </p>
      </div>

      {/* Status Overview */}
      <div className={`border rounded-lg p-6 ${
        getStatusColor() === 'green' 
          ? 'bg-green-50 border-green-200'
          : getStatusColor() === 'yellow'
            ? 'bg-yellow-50 border-yellow-200'
            : 'bg-red-50 border-red-200'
      }`}>
        <div className="flex items-start">
          {getStatusIcon()}
          <div className="ml-4 flex-1">
            <h3 className={`text-lg font-medium ${
              getStatusColor() === 'green' 
                ? 'text-green-900'
                : getStatusColor() === 'yellow'
                  ? 'text-yellow-900'
                  : 'text-red-900'
            }`}>
              {getStatusMessage()}
            </h3>
            <p className={`text-sm mt-1 ${
              getStatusColor() === 'green' 
                ? 'text-green-700'
                : getStatusColor() === 'yellow'
                  ? 'text-yellow-700'
                  : 'text-red-700'
            }`}>
              {getStatusDescription()}
            </p>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <BarChart3 className="h-5 w-5 text-blue-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-blue-900">Összes sor</p>
              <p className="text-lg font-semibold text-blue-700">{stats.totalRows}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-green-900">Sikeres</p>
              <p className="text-lg font-semibold text-green-700">{stats.successCount}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <XCircle className="h-5 w-5 text-red-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-red-900">Sikertelen</p>
              <p className="text-lg font-semibold text-red-700">{stats.errorCount}</p>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-purple-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-purple-900">Időtartam</p>
              <p className="text-lg font-semibold text-purple-700">
                {formatDuration(stats.duration)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Import Details */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Import részletek</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Fájl név</dt>
              <dd className="text-sm text-gray-900">{session.fileName}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Entitás típus</dt>
              <dd className="text-sm text-gray-900">{session.entityType}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Fájl méret</dt>
              <dd className="text-sm text-gray-900">
                {(session.fileSize / 1024).toFixed(1)} KB
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Sikerességi arány</dt>
              <dd className="text-sm text-gray-900">{successRate}%</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Befejezve</dt>
              <dd className="text-sm text-gray-900">
                {new Date(stats.completedAt).toLocaleString('hu-HU')}
              </dd>
            </div>
          </dl>
        </div>

        {/* Performance Metrics */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Teljesítmény</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Sorok per másodperc</dt>
              <dd className="text-sm text-gray-900">
                {stats.duration > 0 
                  ? Math.round(stats.totalRows / stats.duration)
                  : 'N/A'
                }
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Átlagos feldolgozási idő</dt>
              <dd className="text-sm text-gray-900">
                {stats.totalRows > 0 
                  ? `${((stats.duration / stats.totalRows) * 1000).toFixed(1)}ms/sor`
                  : 'N/A'
                }
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Hibaarány</dt>
              <dd className="text-sm text-gray-900">
                {stats.totalRows > 0 
                  ? `${Math.round((stats.errorCount / stats.totalRows) * 100)}%`
                  : '0%'
                }
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Feldolgozási sebesség</dt>
              <dd className="text-sm text-gray-900">
                {stats.duration > 0 && session.fileSize > 0
                  ? `${Math.round((session.fileSize / 1024) / stats.duration)} KB/s`
                  : 'N/A'
                }
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Error Details */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-red-900 mb-4">Import hibák</h3>
          <div className="max-h-48 overflow-y-auto">
            <ul className="space-y-2">
              {errors.slice(0, 10).map((error, index) => (
                <li key={index} className="text-sm text-red-700">
                  • {error}
                </li>
              ))}
              {errors.length > 10 && (
                <li className="text-sm text-red-600 italic">
                  ... és {errors.length - 10} további hiba
                </li>
              )}
            </ul>
          </div>
        </div>
      )}

      {/* Download Options */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Letöltési lehetőségek</h3>
        
        <div className="flex flex-wrap gap-4">
          {errors.length > 0 && (
            <button
              onClick={handleDownloadErrorReport}
              disabled={isDownloading}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-red-700 bg-red-100 hover:bg-red-200 rounded-md disabled:opacity-50"
            >
              <Download className="h-4 w-4 mr-2" />
              Hibajelentés letöltése
            </button>
          )}

          {stats.errorCount > 0 && (
            <button
              onClick={handleDownloadFailedRows}
              disabled={isDownloading}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-orange-700 bg-orange-100 hover:bg-orange-200 rounded-md disabled:opacity-50"
            >
              <FileText className="h-4 w-4 mr-2" />
              Sikertelen sorok letöltése
            </button>
          )}

          <button
            onClick={() => {
              const report = {
                'Import ID': session.id,
                'Fájl név': session.fileName,
                'Entitás típus': session.entityType,
                'Összes sor': stats.totalRows,
                'Sikeres sorok': stats.successCount,
                'Sikertelen sorok': stats.errorCount,
                'Sikerességi arány': `${successRate}%`,
                'Időtartam': formatDuration(stats.duration),
                'Befejezve': new Date(stats.completedAt).toLocaleString('hu-HU')
              }
              
              ExportUtils.downloadAsCSV([report], 'import_osszesito')
            }}
            disabled={isDownloading}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-700 bg-blue-100 hover:bg-blue-200 rounded-md disabled:opacity-50"
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            Összesítő letöltése
          </button>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-between">
        <div className="flex space-x-4">
          <button
            onClick={onRestart}
            disabled={isLoading}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Új import
          </button>

          <button
            onClick={() => window.location.href = '/'}
            disabled={isLoading}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            <Home className="h-4 w-4 mr-2" />
            Főoldal
          </button>
        </div>

        <button
          onClick={() => onComplete(session)}
          disabled={isLoading}
          className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
        >
          <CheckCircle className="h-5 w-5 mr-2" />
          Befejezés
        </button>
      </div>
    </div>
  )
}