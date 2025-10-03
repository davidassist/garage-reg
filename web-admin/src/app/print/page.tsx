'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { LabelService } from '@/lib/services/label-service'
import { PrintJob } from '@/lib/types/labels'

export default function PrintPage() {
  const [printContent, setPrintContent] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const searchParams = useSearchParams()

  useEffect(() => {
    const generatePrintView = async () => {
      try {
        setIsLoading(true)
        setError('')

        // Get print job data from URL params or session storage
        const printJobData = searchParams.get('data')
        let printJob: PrintJob

        if (printJobData) {
          // From URL params (base64 encoded)
          try {
            printJob = JSON.parse(atob(printJobData))
          } catch {
            throw new Error('Érvénytelen nyomtatási adatok')
          }
        } else {
          // From session storage
          const storedData = sessionStorage.getItem('garagereg-print-job')
          if (!storedData) {
            throw new Error('Nincsenek nyomtatási adatok')
          }
          printJob = JSON.parse(storedData)
        }

        // Generate labels
        const result = await LabelService.generateLabels(printJob)
        
        if (result.success && result.printUrl) {
          // Fetch the generated HTML content
          const response = await fetch(result.printUrl)
          const html = await response.text()
          setPrintContent(html)
          
          // Auto-print after a short delay
          setTimeout(() => {
            window.print()
          }, 1000)
        } else {
          setError(result.error || 'Hiba a címkék generálásakor')
        }
      } catch (err) {
        console.error('Print generation error:', err)
        setError(err instanceof Error ? err.message : 'Ismeretlen hiba')
      } finally {
        setIsLoading(false)
      }
    }

    generatePrintView()
  }, [searchParams])

  // Clean up on unmount
  useEffect(() => {
    return () => {
      sessionStorage.removeItem('garagereg-print-job')
    }
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <div className="mt-4 text-lg font-medium text-gray-900">Címkék generálása...</div>
          <div className="mt-2 text-sm text-gray-600">Kérjük várjon</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <div className="text-6xl text-red-500 mb-4">⚠️</div>
          <h1 className="text-xl font-medium text-gray-900 mb-2">Hiba történt</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.close()}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
          >
            Ablak bezárása
          </button>
        </div>
      </div>
    )
  }

  return (
    <div 
      dangerouslySetInnerHTML={{ __html: printContent }}
      style={{
        // Print-specific styles
        width: '100%',
        height: '100%',
        margin: 0,
        padding: 0
      }}
    />
  )
}