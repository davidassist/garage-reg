'use client'

import { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'
import { 
  ImportSession, 
  ImportRowData,
} from '@/lib/types/import'
import { 
  Play, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Loader,
  Clock,
  Database,
  Users
} from 'lucide-react'

interface ImportExecuteStepProps {
  session: ImportSession
  onComplete: (session: ImportSession) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

interface ImportProgress {
  current: number
  total: number
  startTime: Date
  successCount: number
  errorCount: number
  currentItem?: string
  phase: 'preparing' | 'importing' | 'completing' | 'finished'
}

export function ImportExecuteStep({ 
  session, 
  onComplete, 
  isLoading, 
  setIsLoading 
}: ImportExecuteStepProps) {
  const [progress, setProgress] = useState<ImportProgress>({
    current: 0,
    total: session.validRowsCount || 0,
    startTime: new Date(),
    successCount: 0,
    errorCount: 0,
    phase: 'preparing'
  })
  const [executionComplete, setExecutionComplete] = useState(false)
  const [executionErrors, setExecutionErrors] = useState<string[]>([])

  useEffect(() => {
    startImport()
  }, [])

  const startImport = async () => {
    setIsLoading(true)
    setExecutionComplete(false)
    setExecutionErrors([])
    
    const validRows = (session.validatedRows || []).filter(row => row.isValid)
    
    if (validRows.length === 0) {
      toast.error('Nincs importálható sor')
      setIsLoading(false)
      return
    }

    try {
      setProgress(prev => ({
        ...prev,
        phase: 'preparing',
        total: validRows.length,
        startTime: new Date()
      }))

      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate preparation

      // Import in batches
      const batchSize = 10
      const batches = []
      
      for (let i = 0; i < validRows.length; i += batchSize) {
        batches.push(validRows.slice(i, i + batchSize))
      }

      setProgress(prev => ({ ...prev, phase: 'importing' }))

      let totalSuccess = 0
      let totalErrors = 0
      const errors: string[] = []

      for (let batchIndex = 0; batchIndex < batches.length; batchIndex++) {
        const batch = batches[batchIndex]
        
        setProgress(prev => ({
          ...prev,
          current: batchIndex * batchSize,
          currentItem: `Batch ${batchIndex + 1}/${batches.length}`
        }))

        try {
          // Simulate API call to import batch
          const response = await importBatch(batch, session.entityType)
          
          totalSuccess += response.successCount
          totalErrors += response.errorCount
          
          if (response.errors.length > 0) {
            errors.push(...response.errors)
          }

          // Update progress
          setProgress(prev => ({
            ...prev,
            current: Math.min(prev.total, (batchIndex + 1) * batchSize),
            successCount: totalSuccess,
            errorCount: totalErrors
          }))

          // Small delay between batches
          await new Promise(resolve => setTimeout(resolve, 300))
          
        } catch (error) {
          console.error('Batch import error:', error)
          errors.push(`Batch ${batchIndex + 1} hiba: ${error}`)
          totalErrors += batch.length
        }
      }

      setProgress(prev => ({ ...prev, phase: 'completing' }))
      await new Promise(resolve => setTimeout(resolve, 500))

      setProgress(prev => ({
        ...prev,
        phase: 'finished',
        current: prev.total,
        successCount: totalSuccess,
        errorCount: totalErrors
      }))

      setExecutionErrors(errors)
      setExecutionComplete(true)

      if (totalSuccess > 0) {
        toast.success(`Import befejezve: ${totalSuccess} sor sikeresen importálva`)
      }
      
      if (totalErrors > 0) {
        toast.error(`${totalErrors} sor importálása sikertelen`)
      }

    } catch (error) {
      console.error('Import execution error:', error)
      toast.error(`Import hiba: ${error}`)
      setExecutionErrors([String(error)])
    } finally {
      setIsLoading(false)
    }
  }

  const importBatch = async (rows: ImportRowData[], entityType: string) => {
    // Simulate API call - replace with actual API integration
    const delay = Math.random() * 1000 + 500 // 0.5-1.5s delay
    
    return new Promise<{
      successCount: number
      errorCount: number  
      errors: string[]
    }>((resolve) => {
      setTimeout(() => {
        // Simulate some failures (10% failure rate)
        const successRate = 0.9
        const successCount = Math.floor(rows.length * successRate)
        const errorCount = rows.length - successCount
        
        const errors: string[] = []
        if (errorCount > 0) {
          errors.push(`${errorCount} sor importálása sikertelen a batch-ben`)
        }
        
        resolve({
          successCount,
          errorCount,
          errors
        })
      }, delay)
    })
  }

  const getProgressPercentage = () => {
    if (progress.total === 0) return 0
    return Math.round((progress.current / progress.total) * 100)
  }

  const getElapsedTime = () => {
    const now = new Date()
    const elapsed = Math.floor((now.getTime() - progress.startTime.getTime()) / 1000)
    return elapsed
  }

  const getEstimatedTimeRemaining = () => {
    const elapsed = getElapsedTime()
    const percentage = getProgressPercentage()
    
    if (percentage === 0 || percentage === 100) return 0
    
    const totalEstimated = (elapsed * 100) / percentage
    return Math.max(0, totalEstimated - elapsed)
  }

  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds}s`
    } else {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}m ${remainingSeconds}s`
    }
  }

  const handleContinue = () => {
    const updatedSession: ImportSession = {
      ...session,
      currentStep: 'results',
      importStats: {
        totalRows: progress.total,
        successCount: progress.successCount,
        errorCount: progress.errorCount,
        duration: getElapsedTime(),
        completedAt: new Date()
      },
      importErrors: executionErrors,
      updatedAt: new Date(),
    }

    onComplete(updatedSession)
  }

  const phaseLabels = {
    preparing: 'Előkészítés...',
    importing: 'Import folyamatban...',
    completing: 'Befejezés...',
    finished: 'Kész'
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">
          Import végrehajtása
        </h2>
        <p className="mt-2 text-gray-600">
          Az érvényes adatok importálása az adatbázisba
        </p>
      </div>

      {/* Progress Overview */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            {phaseLabels[progress.phase]}
          </h3>
          
          {progress.phase !== 'finished' ? (
            <div className="flex items-center text-gray-600">
              <Loader className="animate-spin h-5 w-5 mr-2" />
              <span className="text-sm">Folyamatban...</span>
            </div>
          ) : (
            <div className="flex items-center text-green-600">
              <CheckCircle className="h-5 w-5 mr-2" />
              <span className="text-sm">Befejezve</span>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>{progress.current} / {progress.total} sor</span>
            <span>{getProgressPercentage()}%</span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all duration-300 ${
                progress.phase === 'finished' 
                  ? 'bg-green-500'
                  : 'bg-blue-500'
              }`}
              style={{ width: `${getProgressPercentage()}%` }}
            />
          </div>
        </div>

        {/* Current Item */}
        {progress.currentItem && progress.phase !== 'finished' && (
          <div className="text-sm text-gray-600 mb-4">
            <span className="font-medium">Aktuális:</span> {progress.currentItem}
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{progress.total}</div>
            <div className="text-sm text-gray-500">Összes</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{progress.successCount}</div>
            <div className="text-sm text-gray-500">Sikeres</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{progress.errorCount}</div>
            <div className="text-sm text-gray-500">Hibás</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-600">{formatTime(getElapsedTime())}</div>
            <div className="text-sm text-gray-500">Eltelt idő</div>
          </div>
        </div>
      </div>

      {/* Time Information */}
      {progress.phase !== 'finished' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center">
              <Clock className="h-5 w-5 text-blue-600 mr-2" />
              <div>
                <p className="text-sm font-medium text-blue-900">Eltelt idő</p>
                <p className="text-lg font-semibold text-blue-700">
                  {formatTime(getElapsedTime())}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <div className="flex items-center">
              <Clock className="h-5 w-5 text-orange-600 mr-2" />
              <div>
                <p className="text-sm font-medium text-orange-900">Becsült hátralevő</p>
                <p className="text-lg font-semibold text-orange-700">
                  {formatTime(getEstimatedTimeRemaining())}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Errors */}
      {executionErrors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <XCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-900 mb-2">
                Import hibák
              </h3>
              <ul className="text-sm text-red-700 space-y-1">
                {executionErrors.map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Completion Status */}
      {executionComplete && (
        <div className={`border rounded-lg p-4 ${
          progress.errorCount === 0 
            ? 'bg-green-50 border-green-200'
            : progress.successCount > 0
              ? 'bg-yellow-50 border-yellow-200' 
              : 'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-start">
            {progress.errorCount === 0 ? (
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 mr-3" />
            ) : progress.successCount > 0 ? (
              <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 mr-3" />
            ) : (
              <XCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3" />
            )}
            
            <div>
              <h3 className={`text-sm font-medium mb-1 ${
                progress.errorCount === 0 
                  ? 'text-green-900'
                  : progress.successCount > 0
                    ? 'text-yellow-900'
                    : 'text-red-900'
              }`}>
                {progress.errorCount === 0 
                  ? 'Import sikeresen befejezve'
                  : progress.successCount > 0
                    ? 'Import részben sikeres'
                    : 'Import sikertelen'
                }
              </h3>
              
              <p className={`text-sm ${
                progress.errorCount === 0 
                  ? 'text-green-700'
                  : progress.successCount > 0
                    ? 'text-yellow-700'
                    : 'text-red-700'
              }`}>
                {progress.successCount} sor sikeresen importálva, 
                {progress.errorCount} sor sikertelen
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <div>
          {!executionComplete && (
            <button
              onClick={startImport}
              disabled={isLoading}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
            >
              <Play className="h-4 w-4 mr-2" />
              Újrakezdés
            </button>
          )}
        </div>

        <button
          onClick={handleContinue}
          disabled={!executionComplete || isLoading}
          className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          Eredmények megtekintése
        </button>
      </div>
    </div>
  )
}