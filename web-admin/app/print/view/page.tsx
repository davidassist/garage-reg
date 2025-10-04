'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { LabelService } from '@/lib/services/label-service'
import { PrintJob, LABEL_FORMATS } from '@/lib/types/labels'

export default function PrintViewPage() {
  const [printContent, setPrintContent] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const searchParams = useSearchParams()

  useEffect(() => {
    const generatePrintView = async () => {
      try {
        setIsLoading(true)
        setError('')

        // Get print job from session storage
        const storedData = sessionStorage.getItem('garagereg-print-preview')
        if (!storedData) {
          throw new Error('Nincsenek nyomtatási adatok')
        }

        const printJob: PrintJob = JSON.parse(storedData)
        
        // Validate print job
        const validation = LabelService.validateLabelData(printJob.labels)
        if (!validation.valid) {
          throw new Error(validation.errors[0])
        }

        // Generate labels
        const result = await LabelService.generateLabels(printJob)
        
        if (result.success && result.printUrl) {
          // Fetch the generated HTML content
          const response = await fetch(result.printUrl)
          const html = await response.text()
          setPrintContent(html)

          // Check if PDF mode
          const mode = searchParams.get('mode')
          if (mode === 'pdf') {
            // Auto-open print dialog after content loads
            setTimeout(() => {
              window.print()
            }, 1500)
          }
        } else {
          setError(result.error || 'Hiba a címkék generálásakor')
        }
      } catch (err) {
        console.error('Print view generation error:', err)
        setError(err instanceof Error ? err.message : 'Ismeretlen hiba')
      } finally {
        setIsLoading(false)
      }
    }

    generatePrintView()
  }, [searchParams])

  // Add print styles
  useEffect(() => {
    if (printContent) {
      // Add print-specific styles to document
      const printStyles = document.createElement('style')
      printStyles.textContent = `
        @media print {
          @page {
            margin: 0;
            size: A4;
          }
          
          body {
            margin: 0 !important;
            padding: 0 !important;
            background: white !important;
            -webkit-print-color-adjust: exact !important;
            color-adjust: exact !important;
          }
          
          * {
            visibility: visible !important;
            background: transparent !important;
            box-shadow: none !important;
          }
          
          .no-print {
            display: none !important;
          }
          
          .print-page {
            page-break-after: always;
            page-break-inside: avoid;
          }
          
          .print-page:last-child {
            page-break-after: auto;
          }
          
          .label-grid {
            break-inside: avoid;
          }
          
          .label-cell {
            break-inside: avoid;
            page-break-inside: avoid;
          }
        }
        
        @media screen {
          body {
            background: #f5f5f5;
            padding: 20px;
          }
          
          .print-container {
            background: white;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin: 0 auto;
            max-width: 210mm;
          }
        }
      `
      document.head.appendChild(printStyles)
      
      return () => {
        document.head.removeChild(printStyles)
      }
    }
  }, [printContent])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <div className="mt-6 text-xl font-medium text-gray-900">Címkék generálása...</div>
          <div className="mt-2 text-sm text-gray-600">
            Optimalizálás Chrome/Edge nyomtatáshoz
          </div>
          <div className="mt-4 max-w-md text-xs text-gray-500">
            <p>🖨️ Margó nélküli nyomtatáshoz:</p>
            <p>Chrome: Beállítások → Több → Margók → Egyéni (0mm)</p>
            <p>Edge: Beállítások → Margók → Egyéni (0mm)</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <div className="text-6xl text-red-500 mb-4">⚠️</div>
          <h1 className="text-2xl font-medium text-gray-900 mb-2">Hiba történt</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="space-y-2">
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 mr-2"
            >
              Újrapróbálkozás
            </button>
            <button
              onClick={() => window.close()}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
            >
              Ablak bezárása
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      {/* Print Controls - Hidden in print mode */}
      <div className="no-print fixed top-4 right-4 z-50 bg-white rounded-lg shadow-lg border p-3 space-y-2">
        <h3 className="font-medium text-sm">Nyomtatási vezérlők</h3>
        <div className="space-y-2">
          <button
            onClick={() => window.print()}
            className="w-full px-3 py-1.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            🖨️ Nyomtatás
          </button>
          <button
            onClick={() => window.close()}
            className="w-full px-3 py-1.5 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            ✕ Bezárás
          </button>
        </div>
        <div className="border-t pt-2">
          <p className="text-xs text-gray-600 leading-tight">
            <strong>Margó nélküli nyomtatás:</strong><br />
            Chrome/Edge → Beállítások → Margók → Egyéni (0mm minden oldalon)
          </p>
        </div>
      </div>

      {/* Print Content */}
      <div className="print-container">
        <div 
          dangerouslySetInnerHTML={{ __html: printContent }}
          style={{
            width: '100%',
            minHeight: '297mm', // A4 height
            margin: 0,
            padding: 0
          }}
        />
      </div>

      {/* Print Instructions - Hidden in print mode */}
      <div className="no-print mt-8 max-w-4xl mx-auto bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">📋 Nyomtatási útmutató</h4>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800">
          <div>
            <h5 className="font-medium mb-1">Chrome beállítások:</h5>
            <ol className="list-decimal list-inside space-y-1 text-xs">
              <li>Ctrl+P (nyomtatás)</li>
              <li>Célállomás: nyomtató kiválasztása</li>
              <li>Oldalak: Összes</li>
              <li>Másolatok: 1 (többszörözés a címke beállításokban)</li>
              <li>Elrendezés: Álló</li>
              <li>Margók: Egyéni → minden oldal 0mm</li>
              <li>Beállítások: Háttérszínek és képek be</li>
            </ol>
          </div>
          <div>
            <h5 className="font-medium mb-1">Nyomtatási tippek:</h5>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>A4-es fehér öntapadó címkelapot használj</li>
              <li>Ellenőrizd a címkeméret egyezést</li>
              <li>Próbanyomtatás normál papírra első alkalommal</li>
              <li>QR kódokat teszteld beolvasással</li>
              <li>Lézernyomtató ajánlott (éles QR kódokért)</li>
              <li>Inkjet esetén slow/fine minőség</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-4 pt-3 border-t border-blue-200">
          <p className="text-xs text-blue-700">
            <strong>Hibaelhárítás:</strong> Ha a címkék nem illeszkednek, ellenőrizd a nyomtató papírbeállításait és a margókat. 
            A böngésző nagyítása legyen 100%. Különböző nyomtatók eltérő kalibrálást igényelhetnek.
          </p>
        </div>
      </div>
    </>
  )
}