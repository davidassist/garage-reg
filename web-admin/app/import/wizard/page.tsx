'use client'

import { useState } from 'react'
import ImportWizard from './ImportWizard'
import { ImportEntityType, ImportResult } from '@/lib/types/import'
import { Upload, FileSpreadsheet, Database } from 'lucide-react'

export default function ImportWizardPage() {
  const [selectedEntityType, setSelectedEntityType] = useState<ImportEntityType | null>(null)
  const [showWizard, setShowWizard] = useState(false)

  const handleEntitySelect = (entityType: ImportEntityType) => {
    setSelectedEntityType(entityType)
    setShowWizard(true)
  }

  const handleWizardClose = () => {
    setShowWizard(false)
    setSelectedEntityType(null)
  }

  const handleWizardComplete = (result: ImportResult) => {
    console.log('Import completed:', result)
    // Handle completion - maybe redirect or show success page
    setShowWizard(false)
    setSelectedEntityType(null)
  }

  if (showWizard && selectedEntityType) {
    return (
      <ImportWizard
        entityType={selectedEntityType}
        onClose={handleWizardClose}
        onComplete={handleWizardComplete}
      />
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-blue-100 rounded-full">
              <Upload className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Import Wizard
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Válassza ki az entitás típusát, majd importálja a CSV vagy Excel fájlokat 
            lépésről lépésre validációval és hibaellenőrzéssel
          </p>
        </div>

        {/* Entity Type Selection */}
        <div className="max-w-4xl mx-auto">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">
            Válasszon entitás típust
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Gates */}
            <div
              onClick={() => handleEntitySelect('gates')}
              className="bg-white rounded-lg border border-gray-200 p-6 cursor-pointer hover:border-blue-500 hover:shadow-md transition-all group"
            >
              <div className="flex items-center mb-4">
                <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                  <Database className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 ml-3">Kapuk</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Kapu entitások importálása névvel, típussal, kapcsolatok és műszaki adatok
              </p>
              <div className="flex items-center text-sm text-blue-600">
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                <span>CSV, Excel támogatva</span>
              </div>
            </div>

            {/* Future entity types can be added here */}
            <div className="bg-gray-100 rounded-lg border border-gray-200 p-6 cursor-not-allowed opacity-50">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-gray-200 rounded-lg">
                  <Database className="h-6 w-6 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-500 ml-3">Egyéb entitások</h3>
              </div>
              <p className="text-sm text-gray-500 mb-4">
                További entitás típusok hamarosan elérhetők lesznek
              </p>
              <div className="flex items-center text-sm text-gray-400">
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                <span>Fejlesztés alatt</span>
              </div>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="max-w-4xl mx-auto mt-12">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">
            Import funkciók
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="flex justify-center mb-3">
                <div className="p-2 bg-green-100 rounded-full">
                  <Upload className="h-6 w-6 text-green-600" />
                </div>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Fájl feltöltés
              </h3>
              <p className="text-sm text-gray-600">
                Húzza be a CSV vagy Excel fájlt, vagy böngésszen a fájlrendszerben
              </p>
            </div>

            <div className="text-center">
              <div className="flex justify-center mb-3">
                <div className="p-2 bg-yellow-100 rounded-full">
                  <FileSpreadsheet className="h-6 w-6 text-yellow-600" />
                </div>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Oszlop térképezés
              </h3>
              <p className="text-sm text-gray-600">
                Automatikus mezőfelismerés és manuális oszlop hozzárendelés
              </p>
            </div>

            <div className="text-center">
              <div className="flex justify-center mb-3">
                <div className="p-2 bg-blue-100 rounded-full">
                  <Database className="h-6 w-6 text-blue-600" />
                </div>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Validáció & Import
              </h3>
              <p className="text-sm text-gray-600">
                Üzleti szabályok ellenőrzése és sikeres import részletes jelentéssel
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}