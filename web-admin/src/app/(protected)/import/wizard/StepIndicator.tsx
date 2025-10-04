'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { CheckCircle, AlertCircle, Circle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Step } from './types'

interface StepIndicatorProps {
  steps: Step[]
  currentStep?: string
  onStepClick?: (stepIndex: number) => void
  className?: string
}

export function StepIndicator({ 
  steps, 
  currentStep, 
  onStepClick, 
  className 
}: StepIndicatorProps) {
  const currentIndex = currentStep ? steps.findIndex(step => step.id === currentStep) : 
    steps.findIndex(step => step.status === 'current')
  const progress = ((currentIndex + 1) / steps.length) * 100

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Import folyamat</span>
          <span className="text-sm text-muted-foreground">
            {currentIndex + 1} / {steps.length}
          </span>
        </CardTitle>
        <Progress value={progress} className="w-full" />
      </CardHeader>
      <CardContent>
        <nav aria-label="Import lépések">
          <ol className="space-y-4">
            {steps.map((step, index) => {
              const isCurrent = step.status === 'current'
              const isCompleted = step.status === 'completed'
              const isError = step.status === 'error'
              const isClickable = onStepClick && (isCompleted || index < currentIndex)
              
              return (
                <li key={step.id} className="flex items-start">
                  <button
                    className={cn(
                      "flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full border-2 transition-colors",
                      isClickable && "hover:bg-muted cursor-pointer",
                      !isClickable && "cursor-default"
                    )}
                    onClick={() => isClickable && onStepClick?.(index)}
                    disabled={!isClickable}
                  >
                    {isError ? (
                      <AlertCircle className="w-5 h-5 text-destructive" />
                    ) : isCompleted ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : isCurrent ? (
                      <Circle className="w-5 h-5 text-primary fill-current" />
                    ) : (
                      <Circle className="w-5 h-5 text-muted-foreground" />
                    )}
                  </button>
                  <div className="ml-3 flex-1">
                    <h3 className={cn(
                      "text-sm font-medium",
                      isCurrent && "text-primary",
                      isCompleted && "text-green-600",
                      isError && "text-destructive",
                      !isCurrent && !isCompleted && !isError && "text-muted-foreground"
                    )}>
                      {step.title}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {step.description}
                    </p>
                  </div>
                </li>
              )
            })}
          </ol>
        </nav>
      </CardContent>
    </Card>
  )
}