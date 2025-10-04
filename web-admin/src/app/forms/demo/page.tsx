'use client'

import React, { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { FileText, Eye, Code, CheckCircle, AlertTriangle } from 'lucide-react'
import { DynamicFormEngine, createDefaultFormData, validateFormTemplate } from '@/components/forms/dynamic'

export default function DynamicFormDemo() {
  // Simple template that matches the current type definitions
  const sampleTemplate = {
    id: 'vehicle-inspection',
    name: 'Járműellenőrzési űrlap',  
    version: '1.0',
    fields: [
  vehicle: {
    id: 'vehicle-inspection',
    title: 'Járműellenőrzési űrlap',
    description: 'Teljes körű járműellenőrzési dokumentáció garázs regisztráció céljából.',
    fields: [
      {
        id: 'vehicle_operational',
        type: 'bool' as const,
        label: 'Jármű működőképes',
        description: 'A jármű alapvető működőképességének megítélése',
        required: true,
        readonly: false,
        visible: true,
        switchStyle: 'switch' as const,
        defaultValue: false
      },
      {
        id: 'vehicle_type',
        type: 'enum',
        label: 'Járműtípus',
        description: 'Válassza ki a jármű típusát',
        required: true,
        options: [
          { value: 'car', label: 'Személyautó' },
          { value: 'motorcycle', label: 'Motorkerékpár' },
          { value: 'truck', label: 'Teherautó' },
          { value: 'van', label: 'Kisteherautó' }
        ],
        displayMode: 'select',
        multiple: false
      },
      {
        id: 'engine_power',
        type: 'number',
        label: 'Motor teljesítmény (kW)',
        description: 'A motor névleges teljesítménye kW-ban',
        required: true,
        min: 1,
        max: 1000,
        step: 1,
        unit: 'kW',
        showSlider: true,
        conditionalVisibility: {
          dependsOn: 'vehicle_operational',
          condition: 'equals',
          expectedValue: true
        }
      },
      {
        id: 'damage_photos',
        type: 'photo',
        label: 'Károsodás fotók',
        description: 'Töltsön fel képeket a jármű károsodásairól',
        required: false,
        accept: ['image/jpeg', 'image/png'],
        multiple: true,
        maxFiles: 5,
        maxFileSize: 5 * 1024 * 1024, // 5MB
        conditionalVisibility: {
          dependsOn: 'vehicle_operational',
          condition: 'equals',
          expectedValue: false
        }
      },
      {
        id: 'inspection_notes',
        type: 'note',
        label: 'Ellenőrzési megjegyzések',
        description: 'Részletes megjegyzések az ellenőrzésről',
        required: true,
        minLength: 10,
        maxLength: 1000,
        rows: 4,
        allowMarkdown: true,
        showCharCount: true
      }
    ]
  },
  
  maintenance: {
    id: 'maintenance-checklist',
    title: 'Karbantartási ellenőrző lista',
    description: 'Periodikus karbantartási munkálatok dokumentálása.',
    fields: [
      {
        id: 'maintenance_type',
        type: 'enum',
        label: 'Karbantartás típusa',
        required: true,
        options: [
          { value: 'routine', label: 'Rendszeres karbantartás' },
          { value: 'repair', label: 'Javítás' },
          { value: 'upgrade', label: 'Fejlesztés' }
        ],
        displayMode: 'radio',
        multiple: false
      },
      {
        id: 'completed_tasks',
        type: 'enum',
        label: 'Elvégzett feladatok',
        required: true,
        options: [
          { value: 'oil_change', label: 'Olajcsere' },
          { value: 'filter_change', label: 'Szűrőcsere' },
          { value: 'brake_check', label: 'Fékrendszer ellenőrzés' },
          { value: 'tire_rotation', label: 'Kerékrotáció' },
          { value: 'battery_check', label: 'Akkumulátor ellenőrzés' }
        ],
        displayMode: 'checkbox',
        multiple: true
      },
      {
        id: 'hours_worked',
        type: 'number',
        label: 'Ledolgozott órák',
        required: true,
        min: 0.5,
        max: 24,
        step: 0.5,
        unit: 'óra',
        showSlider: false
      },
      {
        id: 'work_photos',
        type: 'photo',
        label: 'Munkafotók',
        description: 'Dokumentáció fotók az elvégzett munkálatokról',
        required: false,
        accept: ['image/jpeg', 'image/png'],
        multiple: true,
        maxFiles: 10
      },
      {
        id: 'next_maintenance_needed',
        type: 'boolean',
        label: 'Szükséges további karbantartás',
        required: true,
        displayMode: 'checkbox'
      },
      {
        id: 'maintenance_notes',
        type: 'note',
        label: 'Karbantartási jegyzet',
        required: false,
        maxLength: 500,
        rows: 3,
        allowMarkdown: false,
        showCharCount: true,
        conditionalVisibility: {
          dependsOn: 'next_maintenance_needed',
          condition: 'equals',
          expectedValue: true
        }
      }
    ]
  }
}

export default function DynamicFormDemo() {
  const [selectedTemplate, setSelectedTemplate] = useState<string>('vehicle')
  const [formData, setFormData] = useState<FormData>({})
  const [showJson, setShowJson] = useState(false)
  const [submittedData, setSubmittedData] = useState<FormData | null>(null)

  const currentTemplate = sampleTemplates[selectedTemplate]

  // Initialize form data when template changes
  React.useEffect(() => {
    if (currentTemplate) {
      const defaultData = createDefaultFormData(currentTemplate)
      setFormData(defaultData)
    }
  }, [currentTemplate])

  const handleSave = (data: FormData) => {
    console.log('Form saved:', data)
    setFormData(data)
  }

  const handleSubmit = async (data: FormData) => {
    console.log('Form submitted:', data)
    setSubmittedData(data)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
  }

  const handleCancel = () => {
    const defaultData = createDefaultFormData(currentTemplate)
    setFormData(defaultData)
  }

  const templateErrors = validateFormTemplate(currentTemplate)

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 space-y-8">
        
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Dinamikus űrlap-motor demonstráció
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            JSON sablonokból automatikusan generált űrlapok validációval, 
            feltételes láthatósággal és vizuális kényszerekkel.
          </p>
        </div>

        {/* Template Selector */}
        <Card className="p-6">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Sablon kiválasztása</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(sampleTemplates).map(([key, template]) => (
                <button
                  key={key}
                  onClick={() => setSelectedTemplate(key)}
                  className={`p-4 text-left border rounded-lg transition-colors ${
                    selectedTemplate === key
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <FileText className="w-5 h-5 mt-1 text-gray-400" />
                    <div>
                      <h4 className="font-medium text-gray-900">{template.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                      <div className="text-xs text-gray-500 mt-2">
                        {template.fields.length} mező
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </Card>

        {/* Template Validation */}
        {templateErrors.length > 0 && (
          <Card className="p-6 border-red-200 bg-red-50">
            <h3 className="text-lg font-semibold text-red-800 mb-2">
              Sablon validációs hibák
            </h3>
            <ul className="space-y-1">
              {templateErrors.map((error, index) => (
                <li key={index} className="text-sm text-red-700">• {error}</li>
              ))}
            </ul>
          </Card>
        )}

        {/* Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={() => setShowJson(!showJson)}
              className="flex items-center gap-2"
            >
              {showJson ? <Eye className="w-4 h-4" /> : <Code className="w-4 h-4" />}
              {showJson ? 'Űrlap megjelenítése' : 'JSON sablon megjelenítése'}
            </Button>
          </div>
          
          <div className="text-sm text-gray-500">
            Aktív sablon: <span className="font-medium">{currentTemplate.title}</span>
          </div>
        </div>

        {/* JSON Template Display */}
        {showJson && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">JSON sablon</h3>
            <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-auto max-h-96">
              {JSON.stringify(currentTemplate, null, 2)}
            </pre>
          </Card>
        )}

        {/* Dynamic Form Engine */}
        {!showJson && (
          <DynamicFormEngine
            template={currentTemplate}
            initialData={formData}
            onSave={handleSave}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            showProgress={true}
            autoSave={true}
            autoSaveDelay={3000}
          />
        )}

        {/* Submission Result */}
        {submittedData && (
          <Card className="p-6 border-green-200 bg-green-50">
            <h3 className="text-lg font-semibold text-green-800 mb-4">
              ✓ Űrlap sikeresen beküldve
            </h3>
            <details className="space-y-2">
              <summary className="cursor-pointer text-sm font-medium text-green-700">
                Beküldött adatok megtekintése
              </summary>
              <pre className="bg-white p-4 rounded text-sm overflow-auto max-h-64">
                {JSON.stringify(submittedData, null, 2)}
              </pre>
            </details>
          </Card>
        )}

        <Separator />

        {/* Feature Overview */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Megvalósított funkciók</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Komponensek</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>✓ BoolSwitchItem - kapcsoló/checkbox</li>
                <li>✓ EnumItem - select/radio/checkbox lista</li>
                <li>✓ NumberWithRange - szám csúszka támogatással</li>
                <li>✓ PhotoItem - fájl feltöltés drag&drop-pal</li>
                <li>✓ NoteItem - szövegterület markdown támogatással</li>
              </ul>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Funkciók</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>✓ Kötelező mezők vizuális kényszer</li>
                <li>✓ Feltételes láthatóság</li>
                <li>✓ Validáció és „nem fejezhető be" guard</li>
                <li>✓ Automatikus mentés</li>
                <li>✓ Haladásjelző</li>
                <li>✓ TypeScript + Zod típusbiztonság</li>
              </ul>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}