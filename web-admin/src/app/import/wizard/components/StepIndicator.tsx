import { ImportStep, ImportStepLabels } from '@/lib/types/import'
import { Check, Circle, Dot } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StepIndicatorProps {
  steps: ImportStep[]
  currentStep: ImportStep
  completedSteps: ImportStep[]
}

export function StepIndicator({ steps, currentStep, completedSteps }: StepIndicatorProps) {
  const getStepStatus = (step: ImportStep) => {
    if (completedSteps.includes(step)) return 'completed'
    if (step === currentStep) return 'current'
    return 'pending'
  }

  const getStepIcon = (step: ImportStep, status: string) => {
    switch (status) {
      case 'completed':
        return <Check className="h-4 w-4 text-white" />
      case 'current':
        return <Dot className="h-4 w-4 text-white" />
      default:
        return <Circle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStepStyles = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500 border-green-500'
      case 'current':
        return 'bg-blue-500 border-blue-500'
      default:
        return 'bg-white border-gray-300'
    }
  }

  const getConnectorStyles = (index: number) => {
    const currentIndex = steps.indexOf(currentStep)
    return index < currentIndex ? 'bg-green-500' : 'bg-gray-300'
  }

  return (
    <nav aria-label="Import lépések" className="flex items-center justify-center">
      <ol className="flex items-center space-x-8">
        {steps.map((step, index) => {
          const status = getStepStatus(step)
          
          return (
            <li key={step} className="flex items-center">
              {/* Step Circle */}
              <div className="relative">
                <div
                  className={cn(
                    'w-10 h-10 rounded-full border-2 flex items-center justify-center',
                    getStepStyles(status)
                  )}
                >
                  {getStepIcon(step, status)}
                </div>
                
                {/* Step Label */}
                <div className="absolute top-12 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
                  <span
                    className={cn(
                      'text-sm font-medium',
                      status === 'current' ? 'text-blue-600' : 
                      status === 'completed' ? 'text-green-600' : 'text-gray-500'
                    )}
                  >
                    {ImportStepLabels[step]}
                  </span>
                </div>
              </div>

              {/* Connector */}
              {index < steps.length - 1 && (
                <div className="flex-1 mx-4">
                  <div
                    className={cn(
                      'h-0.5 w-16 transition-colors duration-200',
                      getConnectorStyles(index)
                    )}
                  />
                </div>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}