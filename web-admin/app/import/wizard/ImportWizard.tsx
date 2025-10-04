'use client'

import { useState, useCallback } from 'react'
import { toast } from 'react-hot-toast'
import { 
  ImportStep, 
  ImportSession, 
  ImportEntityType, 
  ImportResult,
  ImportStepLabels 
} from '@/lib/types/import'
import { FileUploadStep } from './steps/FileUploadStep'
import { ColumnMappingStep } from './steps/ColumnMappingStep'
import { ValidationStep } from './steps/ValidationStep'
import { PreviewStep } from './steps/PreviewStep'
import { ImportExecuteStep } from './steps/ImportExecuteStep'
import { ResultsStep } from './steps/ResultsStep'
import { StepIndicator } from './StepIndicator'
import { ArrowLeft, X } from 'lucide-react'

interface ImportWizardProps {
  entityType: ImportEntityType
  onClose?: () => void
  onComplete?: (result: ImportResult) => void
}

export default function ImportWizard({ 
  entityType, 
  onClose, 
  onComplete 
}: ImportWizardProps) {
  const [session, setSession] = useState<ImportSession | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const steps: ImportStep[] = ['upload', 'mapping', 'validation', 'preview', 'execute', 'results']
  const currentStepIndex = session ? steps.indexOf(session.currentStep) : 0

  const handleStepComplete = useCallback((updatedSession: ImportSession) => {
    setSession(updatedSession)
  }, [])

  const handlePreviousStep = useCallback(() => {
    if (!session || currentStepIndex === 0) return
    
    const previousStep = steps[currentStepIndex - 1]
    setSession(prev => prev ? { ...prev, currentStep: previousStep } : null)
  }, [session, currentStepIndex, steps])

  const handleReset = useCallback(() => {
    setSession(null)
  }, [])

  const handleComplete = useCallback((completedSession: ImportSession) => {
    const result: ImportResult = {
      success: (completedSession.importStats?.successCount || 0) > 0,
      importedIds: [], // TODO: Add actual imported IDs from API response
      message: completedSession.importStats ? 
        `${completedSession.importStats.successCount} sor sikeresen importálva ${completedSession.importStats.totalRows}-ből` :
        'Import befejezve',
      statistics: completedSession.importStats ? {
        totalRows: completedSession.importStats.totalRows,
        validRows: completedSession.importStats.successCount,
        invalidRows: completedSession.importStats.errorCount,
        warnings: completedSession.warningsCount || 0,
        imported: completedSession.importStats.successCount,
        skipped: completedSession.importStats.errorCount,
        duplicates: 0,
        processingTime: completedSession.importStats.duration
      } : {
        totalRows: 0,
        validRows: 0,
        invalidRows: 0,
        warnings: 0,
        imported: 0,
        skipped: 0,
        duplicates: 0,
        processingTime: 0
      }
    }
    
    if (result.success) {
      toast.success('Import sikeresen befejezve!')
    } else {
      toast.error('Import nem volt sikeres')
    }
    
    onComplete?.(result)
  }, [onComplete])

  const renderCurrentStep = () => {
    if (!session) {
      return (
        <FileUploadStep
          entityType={entityType}
          onComplete={handleStepComplete}
          isLoading={isLoading}
          setIsLoading={setIsLoading}
        />
      )
    }

    switch (session.currentStep) {
      case 'upload':
        return (
          <FileUploadStep
            entityType={entityType}
            session={session}
            onComplete={handleStepComplete}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )
      case 'mapping':
        return (
          <ColumnMappingStep
            session={session}
            onComplete={handleStepComplete}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )
      case 'validation':
        return (
          <ValidationStep
            session={session}
            onComplete={handleStepComplete}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )
      case 'preview':
        return (
          <PreviewStep
            session={session}
            onComplete={handleStepComplete}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )
      case 'execute':
        return (
          <ImportExecuteStep
            session={session}
            onComplete={handleStepComplete}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )
      case 'results':
        return (
          <ResultsStep
            session={session}
            onComplete={handleComplete}
            onRestart={handleReset}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              {session && currentStepIndex > 0 && (
                <button
                  onClick={handlePreviousStep}
                  disabled={isLoading}
                  className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                  title="Előző lépés"
                >
                  <ArrowLeft className="h-5 w-5" />
                </button>
              )}
              <h1 className="text-xl font-semibold text-gray-900">
                Import Wizard - {ImportStepLabels[session?.currentStep || 'upload']}
              </h1>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                disabled={isLoading}
                className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                title="Bezárás"
              >
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Step Indicator */}
      {session && (
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <StepIndicator
              steps={steps}
              currentStep={session.currentStep}
              completedSteps={steps.slice(0, currentStepIndex)}
            />
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm">
          {renderCurrentStep()}
        </div>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <div>
                <div className="text-sm font-medium text-gray-900">Feldolgozás...</div>
                <div className="text-xs text-gray-500">Kérjük várjon</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}