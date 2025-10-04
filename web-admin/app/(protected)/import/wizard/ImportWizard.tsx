'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { StepIndicator } from './StepIndicator'
import { FileUploadStep } from './FileUploadStep'
import { FieldMappingStep } from './FieldMappingStep'
import { ValidationStep } from './ValidationStep'
import { ImportStep } from './ImportStep'
import { ImportType, FieldMapping, ProcessedRow, Step } from './types'
import { ArrowLeft, FileSpreadsheet } from 'lucide-react'
import { cn } from '@/lib/utils'
import Link from 'next/link'

interface ImportWizardState {
  step: number
  importType: ImportType | null
  uploadedData: any[] | null
  fieldMappings: FieldMapping[]
  processedData: ProcessedRow[]
}

const steps: Step[] = [
  {
    id: 'upload',
    title: 'Fájl feltöltés',
    description: 'CSV vagy XLSX fájl feltöltése',
    status: 'current'
  },
  {
    id: 'mapping',
    title: 'Mezők hozzárendelése',
    description: 'Oszlopok hozzárendelése adatbázis mezőkhöz',
    status: 'pending'
  },
  {
    id: 'validation',
    title: 'Validáció',
    description: 'Adatok ellenőrzése és hibák javítása',
    status: 'pending'
  },
  {
    id: 'import',
    title: 'Import',
    description: 'Adatok importálása az adatbázisba',
    status: 'pending'
  }
]

export default function ImportWizard() {
  const [state, setState] = useState<ImportWizardState>({
    step: 0,
    importType: null,
    uploadedData: null,
    fieldMappings: [],
    processedData: []
  })

  // Create step status based on current progress
  const getStepStatus = (stepIndex: number): Step['status'] => {
    if (stepIndex < state.step) return 'completed'
    if (stepIndex === state.step) return 'current'
    return 'pending'
  }

  const currentSteps: Step[] = steps.map((step, index) => ({
    ...step,
    status: getStepStatus(index)
  }))

  const handleFileUpload = (type: ImportType, data: any[]) => {
    setState(prev => ({
      ...prev,
      step: 1,
      importType: type,
      uploadedData: data,
      fieldMappings: [],
      processedData: []
    }))
  }

  const handleFieldMapping = (mappings: FieldMapping[]) => {
    setState(prev => ({
      ...prev,
      step: 2,
      fieldMappings: mappings
    }))
  }

  const handleValidationComplete = (processedData: ProcessedRow[]) => {
    setState(prev => ({
      ...prev,
      step: 3,
      processedData
    }))
  }

  const handleImportComplete = () => {
    // Import is complete, user can navigate away
    // State remains for potential navigation back
  }

  const goToStep = (stepIndex: number) => {
    // Only allow going to previous steps
    if (stepIndex < state.step) {
      setState(prev => ({ ...prev, step: stepIndex }))
    }
  }

  const goToPreviousStep = () => {
    if (state.step > 0) {
      setState(prev => ({ ...prev, step: prev.step - 1 }))
    }
  }

  const resetWizard = () => {
    setState({
      step: 0,
      importType: null,
      uploadedData: null,
      fieldMappings: [],
      processedData: []
    })
  }

  const getStepTitle = () => {
    return currentSteps[state.step]?.title || 'Import Wizard'
  }

  const getStepDescription = () => {
    return currentSteps[state.step]?.description || 'Adatok importálása lépésről lépésre'
  }

  return (
    <div className="container mx-auto py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Link 
              href="/dashboard" 
              className="flex items-center text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="h-4 w-4 mr-1" />
              Dashboard
            </Link>
            <span className="text-muted-foreground">/</span>
            <span className="font-medium">Import Wizard</span>
          </div>
          <div className="flex items-center space-x-2">
            <FileSpreadsheet className="h-6 w-6" />
            <h1 className="text-3xl font-bold">{getStepTitle()}</h1>
          </div>
          <p className="text-muted-foreground">{getStepDescription()}</p>
        </div>

        {state.step > 0 && (
          <Button variant="outline" onClick={resetWizard}>
            Új import indítása
          </Button>
        )}
      </div>

      {/* Step Indicator */}
      <StepIndicator 
        steps={currentSteps} 
        onStepClick={goToStep}
        className="bg-card"
      />

      {/* Step Content */}
      <Card className="min-h-[600px]">
        <CardContent className="p-8">
          {state.step === 0 && (
            <FileUploadStep onNext={handleFileUpload} />
          )}

          {state.step === 1 && state.importType && state.uploadedData && (
            <FieldMappingStep
              importType={state.importType}
              uploadedData={state.uploadedData}
              onNext={handleFieldMapping}
              onBack={goToPreviousStep}
            />
          )}

          {state.step === 2 && state.importType && state.uploadedData && state.fieldMappings.length > 0 && (
            <ValidationStep
              importType={state.importType}
              uploadedData={state.uploadedData}
              fieldMappings={state.fieldMappings}
              onNext={handleValidationComplete}
              onBack={goToPreviousStep}
            />
          )}

          {state.step === 3 && state.importType && state.processedData.length > 0 && (
            <ImportStep
              importType={state.importType}
              processedData={state.processedData}
              onComplete={handleImportComplete}
              onBack={goToPreviousStep}
            />
          )}
        </CardContent>
      </Card>

      {/* Debug Info (remove in production) */}
      {process.env.NODE_ENV === 'development' && (
        <Card className="bg-muted/50">
          <CardHeader>
            <CardTitle className="text-sm">Debug Info</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-xs">
              {JSON.stringify({
                step: state.step,
                importType: state.importType,
                dataRows: state.uploadedData?.length || 0,
                mappings: state.fieldMappings.length,
                processedRows: state.processedData.length
              }, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  )
}