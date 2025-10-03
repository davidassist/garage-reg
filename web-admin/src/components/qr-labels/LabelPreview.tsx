'use client'

import { useState } from 'react'
import { 
  Eye, 
  Download, 
  Printer, 
  QrCode, 
  Tag,
  X
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

interface Gate {
  id: string
  name: string
  buildingName: string
  siteName: string
  clientName: string
  gateType: string
  location: string
  serialNumber: string
}

interface LabelPreviewProps {
  gates: Gate[]
  labelsPerRow?: number
}

// Sample QR code SVG (placeholder)
const SampleQRCode = () => (
  <svg width="60" height="60" viewBox="0 0 60 60" className="border">
    <rect width="60" height="60" fill="white"/>
    <rect x="0" y="0" width="6" height="6" fill="black"/>
    <rect x="12" y="0" width="6" height="6" fill="black"/>
    <rect x="24" y="0" width="6" height="6" fill="black"/>
    <rect x="36" y="0" width="6" height="6" fill="black"/>
    <rect x="48" y="0" width="12" height="6" fill="black"/>
    <rect x="0" y="12" width="6" height="6" fill="black"/>
    <rect x="18" y="12" width="6" height="6" fill="black"/>
    <rect x="30" y="12" width="6" height="6" fill="black"/>
    <rect x="42" y="12" width="6" height="6" fill="black"/>
    <rect x="54" y="12" width="6" height="6" fill="black"/>
    <rect x="6" y="24" width="6" height="6" fill="black"/>
    <rect x="18" y="24" width="6" height="6" fill="black"/>
    <rect x="36" y="24" width="6" height="6" fill="black"/>
    <rect x="48" y="24" width="12" height="6" fill="black"/>
    <rect x="0" y="36" width="6" height="6" fill="black"/>
    <rect x="12" y="36" width="6" height="6" fill="black"/>
    <rect x="30" y="36" width="6" height="6" fill="black"/>
    <rect x="54" y="36" width="6" height="6" fill="black"/>
    <rect x="6" y="48" width="6" height="6" fill="black"/>
    <rect x="24" y="48" width="6" height="6" fill="black"/>
    <rect x="42" y="48" width="12" height="6" fill="black"/>
  </svg>
)

export function LabelPreview({ gates, labelsPerRow = 3 }: LabelPreviewProps) {
  const [isOpen, setIsOpen] = useState(false)

  const handlePrint = () => {
    window.print()
  }

  const handleDownloadPDF = () => {
    // In real implementation, this would trigger PDF generation
    const blob = new Blob(['Sample PDF content'], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `qr_labels_${gates.length}_gates.pdf`
    document.body.appendChild(a)
    a.click()
    URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Eye className="h-4 w-4 mr-2" />
          Minta előnézet
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Tag className="h-5 w-5" />
            QR címkék előnézete
          </DialogTitle>
          <DialogDescription>
            {gates.length} kapu címkéjének előnézete ({labelsPerRow} oszlop)
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Toolbar */}
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600">
              Formátum: A4, {labelsPerRow} oszlop × {Math.ceil(gates.length / labelsPerRow)} sor
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handlePrint}>
                <Printer className="h-4 w-4 mr-2" />
                Nyomtatás
              </Button>
              <Button variant="outline" size="sm" onClick={handleDownloadPDF}>
                <Download className="h-4 w-4 mr-2" />
                PDF letöltés
              </Button>
            </div>
          </div>

          {/* Label Preview */}
          <div className="bg-white p-8 shadow-lg rounded-lg print:shadow-none print:p-0">
            {/* Header */}
            <div className="text-center mb-8 print:mb-4">
              <h1 className="text-2xl font-bold text-gray-800 print:text-lg">
                QR Címkék - {gates.length} kapu
              </h1>
              <p className="text-gray-600 text-sm mt-2 print:text-xs">
                Generálva: {new Date().toLocaleDateString('hu-HU')}
              </p>
            </div>

            {/* Labels Grid */}
            <div 
              className="grid gap-6 print:gap-3"
              style={{ 
                gridTemplateColumns: `repeat(${labelsPerRow}, 1fr)`,
              }}
            >
              {gates.map((gate, index) => (
                <div 
                  key={gate.id}
                  className="border-2 border-gray-300 border-dashed p-4 print:p-2 print:border-solid print:border-gray-400 bg-white"
                  style={{ 
                    minHeight: '120px',
                    pageBreakInside: 'avoid'
                  }}
                >
                  <div className="flex flex-col items-center space-y-2 print:space-y-1">
                    {/* QR Code */}
                    <div className="flex justify-center">
                      <SampleQRCode />
                    </div>

                    {/* Gate Info */}
                    <div className="text-center space-y-1 print:space-y-0">
                      <div className="font-bold text-sm print:text-xs truncate max-w-full">
                        {gate.name}
                      </div>
                      <div className="text-xs text-gray-600 print:text-[10px] truncate">
                        {gate.buildingName}
                      </div>
                      <div className="text-xs text-gray-500 print:text-[9px] truncate">
                        S/N: {gate.serialNumber}
                      </div>
                    </div>

                    {/* QR URL (for reference) */}
                    <div className="text-[10px] text-gray-400 print:text-[8px] text-center">
                      gate.garagereg.app/{gate.id}
                    </div>
                  </div>
                </div>
              ))}

              {/* Fill remaining slots if needed */}
              {Array.from({ 
                length: (Math.ceil(gates.length / labelsPerRow) * labelsPerRow) - gates.length 
              }, (_, i) => (
                <div key={`empty-${i}`} className="border-2 border-gray-200 border-dashed p-4 print:p-2 bg-gray-50 print:bg-transparent" />
              ))}
            </div>

            {/* Info Table */}
            <div className="mt-12 print:mt-8 print:break-before-page">
              <h2 className="text-lg font-bold mb-4 print:text-base">Kapu információk</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse border border-gray-300 print:text-xs">
                  <thead>
                    <tr className="bg-gray-100 print:bg-gray-200">
                      <th className="border border-gray-300 px-3 py-2 text-left print:px-2 print:py-1">Kapu név</th>
                      <th className="border border-gray-300 px-3 py-2 text-left print:px-2 print:py-1">Épület</th>
                      <th className="border border-gray-300 px-3 py-2 text-left print:px-2 print:py-1">Telephely</th>
                      <th className="border border-gray-300 px-3 py-2 text-left print:px-2 print:py-1">Típus</th>
                      <th className="border border-gray-300 px-3 py-2 text-left print:px-2 print:py-1">QR URL</th>
                    </tr>
                  </thead>
                  <tbody>
                    {gates.map((gate) => (
                      <tr key={gate.id} className="hover:bg-gray-50 print:hover:bg-transparent">
                        <td className="border border-gray-300 px-3 py-2 print:px-2 print:py-1 font-medium">
                          {gate.name}
                        </td>
                        <td className="border border-gray-300 px-3 py-2 print:px-2 print:py-1">
                          {gate.buildingName}
                        </td>
                        <td className="border border-gray-300 px-3 py-2 print:px-2 print:py-1">
                          {gate.siteName}
                        </td>
                        <td className="border border-gray-300 px-3 py-2 print:px-2 print:py-1">
                          {gate.gateType}
                        </td>
                        <td className="border border-gray-300 px-3 py-2 print:px-2 print:py-1 font-mono text-xs print:text-[10px]">
                          gate.garagereg.app/{gate.id}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Close Button */}
          <div className="flex justify-end print:hidden">
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Bezárás
            </Button>
          </div>
        </div>

        {/* Print Styles */}
        <style jsx global>{`
          @media print {
            body { 
              margin: 0;
              padding: 15mm;
              font-size: 12px;
            }
            .print\\:hidden { display: none !important; }
            .print\\:block { display: block !important; }
            .print\\:text-xs { font-size: 0.75rem !important; }
            .print\\:text-\\[10px\\] { font-size: 10px !important; }
            .print\\:text-\\[9px\\] { font-size: 9px !important; }
            .print\\:text-\\[8px\\] { font-size: 8px !important; }
            .print\\:p-0 { padding: 0 !important; }
            .print\\:p-1 { padding: 0.25rem !important; }
            .print\\:p-2 { padding: 0.5rem !important; }
            .print\\:px-2 { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
            .print\\:py-1 { padding-top: 0.25rem !important; padding-bottom: 0.25rem !important; }
            .print\\:mb-4 { margin-bottom: 1rem !important; }
            .print\\:mt-8 { margin-top: 2rem !important; }
            .print\\:gap-3 { gap: 0.75rem !important; }
            .print\\:space-y-0 > * + * { margin-top: 0 !important; }
            .print\\:space-y-1 > * + * { margin-top: 0.25rem !important; }
            .print\\:shadow-none { box-shadow: none !important; }
            .print\\:border-solid { border-style: solid !important; }
            .print\\:border-gray-400 { border-color: #9ca3af !important; }
            .print\\:bg-gray-200 { background-color: #e5e7eb !important; }
            .print\\:bg-transparent { background-color: transparent !important; }
            .print\\:text-base { font-size: 1rem !important; }
            .print\\:text-lg { font-size: 1.125rem !important; }
            .print\\:hover\\:bg-transparent:hover { background-color: transparent !important; }
            .print\\:break-before-page { break-before: page !important; }
            
            @page {
              margin: 15mm;
              size: A4;
            }
          }
        `}</style>
      </DialogContent>
    </Dialog>
  )
}