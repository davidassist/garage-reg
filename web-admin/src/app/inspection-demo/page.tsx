'use client'

import { useState, useEffect } from 'react'
import { InspectionManager } from '@/components/inspection'
import { 
  InspectionTemplate, 
  InspectionInstance, 
  StartInspectionRequest,
  INSPECTION_CATEGORIES
} from '@/lib/types/inspection'

// Mock data
const mockTemplates: InspectionTemplate[] = [
  {
    id: 'safety-001',
    name: 'Biztonsági Ellenőrzés',
    description: 'Alapvető biztonsági szempontok és kockázatok felmérése',
    category: 'safety',
    estimatedDuration: 30,
    fields: [
      {
        id: 'safety-lighting',
        type: 'boolean',
        label: 'Világítás működőképes',
        description: 'Ellenőrizze, hogy minden világítótest működik-e',
        required: true
      },
      {
        id: 'safety-emergency',
        type: 'select',
        label: 'Vészhelyzeti felszerelés',
        description: 'Tűzoltó készülék és elsősegély doboz állapota',
        required: true,
        options: ['Megfelelő', 'Javítandó', 'Hiányzik', 'Lejárt']
      },
      {
        id: 'safety-access',
        type: 'multiselect',
        label: 'Akadálymentesítés',
        description: 'Jelölje meg az elérhető akadálymentesített funkciókat',
        options: ['Rámpa', 'Lift', 'Széles ajtók', 'Taktilis vezetők', 'Hangos jelzés'],
        required: false
      },
      {
        id: 'safety-temperature',
        type: 'number',
        label: 'Hőmérséklet (°C)',
        description: 'Mért hőmérséklet a főbejáratnál',
        required: true,
        validation: { min: -10, max: 50 }
      },
      {
        id: 'safety-notes',
        type: 'note',
        label: 'Biztonsági megjegyzések',
        description: 'Írjon le minden biztonsággal kapcsolatos észrevételt',
        required: false,
        validation: { maxLength: 1000 }
      },
      {
        id: 'safety-photos',
        type: 'photo',
        label: 'Dokumentációs képek',
        description: 'Készítsen képeket a biztonsági problémákról',
        required: false
      },
      {
        id: 'inspector-signature',
        type: 'signature',
        label: 'Ellenőr aláírása',
        description: 'Digitális aláírás a vizsgálat lezárásához',
        required: true
      }
    ],
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-02-20'),
    version: '2.1.0',
    isActive: true
  },
  {
    id: 'maintenance-001',
    name: 'Havi Karbantartás',
    description: 'Rendszeres havi karbantartási feladatok ellenőrzése',
    category: 'maintenance',
    estimatedDuration: 45,
    fields: [
      {
        id: 'maint-gate-operation',
        type: 'select',
        label: 'Kapu működése',
        required: true,
        options: ['Hibátlan', 'Lassú', 'Akadozik', 'Nem működik']
      },
      {
        id: 'maint-motor-sound',
        type: 'boolean',
        label: 'Motor hangja normális',
        required: true
      },
      {
        id: 'maint-lubrication',
        type: 'select',
        label: 'Kenés állapota',
        required: true,
        options: ['Megfelelő', 'Szükséges', 'Túlzott', 'Hiányzik']
      },
      {
        id: 'maint-wear-level',
        type: 'number',
        label: 'Kopás mértéke (1-10)',
        required: true,
        validation: { min: 1, max: 10 }
      },
      {
        id: 'maint-completed-tasks',
        type: 'multiselect',
        label: 'Elvégzett feladatok',
        required: true,
        options: ['Tisztítás', 'Kenés', 'Beállítás', 'Alkatrész csere', 'Elektromos ellenőrzés']
      },
      {
        id: 'maint-next-service',
        type: 'text',
        label: 'Következő szerviz dátuma',
        required: false,
        validation: { pattern: '^\\d{4}-\\d{2}-\\d{2}$' }
      }
    ],
    createdAt: new Date('2024-01-20'),
    updatedAt: new Date('2024-03-01'),
    version: '1.5.0',
    isActive: true
  },
  {
    id: 'quality-001',
    name: 'Minőségi Auditálás',
    description: 'Szolgáltatás minőségének és ügyfél-elégedettségének értékelése',
    category: 'quality',
    estimatedDuration: 60,
    fields: [
      {
        id: 'quality-cleanliness',
        type: 'number',
        label: 'Tisztaság (1-5)',
        required: true,
        validation: { min: 1, max: 5 }
      },
      {
        id: 'quality-signage',
        type: 'boolean',
        label: 'Jelzések olvashatók',
        required: true
      },
      {
        id: 'quality-customer-feedback',
        type: 'select',
        label: 'Ügyfél visszajelzések',
        required: false,
        options: ['Kiváló', 'Jó', 'Megfelelő', 'Gyenge', 'Nincs adat']
      },
      {
        id: 'quality-improvement-areas',
        type: 'multiselect',
        label: 'Fejlesztendő területek',
        required: false,
        options: ['Sebesség', 'Megbízhatóság', 'Kényelem', 'Biztonság', 'Kommunikáció']
      },
      {
        id: 'quality-notes',
        type: 'note',
        label: 'Minőségi észrevételek',
        required: false,
        validation: { maxLength: 2000 }
      }
    ],
    createdAt: new Date('2024-02-01'),
    updatedAt: new Date('2024-02-15'),
    version: '1.0.0',
    isActive: true
  }
]

const mockGates = [
  { id: 'gate-001', name: 'Főbejárat A', location: 'Északi szárny' },
  { id: 'gate-002', name: 'Hátsó kapu B', location: 'Déli szárny' },
  { id: 'gate-003', name: 'Szerviz kapu C', location: 'Kelet oldal' }
]

const mockGarages = [
  { id: 'garage-001', name: 'Garazs Complex A', address: '1111 Budapest, Teszt utca 1.' },
  { id: 'garage-002', name: 'Garazs Complex B', address: '1111 Budapest, Teszt utca 2.' }
]

const mockUsers = [
  { id: 'user-001', name: 'Kovács János', role: 'Technikus' },
  { id: 'user-002', name: 'Nagy Anna', role: 'Ellenőr' },
  { id: 'user-003', name: 'Szabó Péter', role: 'Manager' }
]

export default function InspectionDemo() {
  const [inspections, setInspections] = useState<InspectionInstance[]>([])
  const [currentInspection, setCurrentInspection] = useState<InspectionInstance | null>(null)

  // Load saved inspections from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('demo-inspections')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        setInspections(parsed.map((inspection: any) => ({
          ...inspection,
          createdAt: new Date(inspection.createdAt),
          updatedAt: new Date(inspection.updatedAt),
          startedAt: inspection.startedAt ? new Date(inspection.startedAt) : undefined,
          completedAt: inspection.completedAt ? new Date(inspection.completedAt) : undefined,
          submittedAt: inspection.submittedAt ? new Date(inspection.submittedAt) : undefined,
          dueDate: inspection.dueDate ? new Date(inspection.dueDate) : undefined,
          lastSavedAt: inspection.lastSavedAt ? new Date(inspection.lastSavedAt) : undefined,
          fieldValues: inspection.fieldValues.map((fv: any) => ({
            ...fv,
            timestamp: fv.timestamp ? new Date(fv.timestamp) : undefined
          })),
          comments: inspection.comments.map((c: any) => ({
            ...c,
            timestamp: new Date(c.timestamp)
          }))
        })))
      } catch (error) {
        console.error('Failed to load inspections:', error)
      }
    }
  }, [])

  // Save inspections to localStorage
  useEffect(() => {
    localStorage.setItem('demo-inspections', JSON.stringify(inspections))
  }, [inspections])

  const handleStartInspection = async (request: StartInspectionRequest): Promise<InspectionInstance> => {
    const template = mockTemplates.find(t => t.id === request.templateId)
    if (!template) {
      throw new Error('Template not found')
    }

    const newInspection: InspectionInstance = {
      id: `inspection-${Date.now()}`,
      templateId: request.templateId,
      title: request.title,
      description: request.description,
      status: 'in_progress',
      priority: request.priority,
      assignedTo: request.assignedTo,
      assignedBy: 'current-user',
      assignedAt: new Date(),
      gateId: request.gateId,
      garageId: request.garageId,
      fieldValues: [],
      completedFields: [],
      totalFields: template.fields.length,
      progressPercentage: 0,
      startedAt: new Date(),
      dueDate: request.dueDate,
      hasUnsavedChanges: false,
      autoSaveEnabled: request.autoSaveEnabled,
      comments: [],
      criticalIssues: 0,
      minorIssues: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
      createdBy: 'current-user',
      version: 1
    }

    setInspections(prev => [...prev, newInspection])
    setCurrentInspection(newInspection)
    
    return newInspection
  }

  const handleSaveInspection = async (inspection: InspectionInstance) => {
    setInspections(prev => 
      prev.map(i => i.id === inspection.id ? inspection : i)
    )
    setCurrentInspection(inspection)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
  }

  const handleSubmitInspection = async (inspectionId: string) => {
    setInspections(prev =>
      prev.map(i => 
        i.id === inspectionId 
          ? { ...i, status: 'submitted', submittedAt: new Date() }
          : i
      )
    )
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))
  }

  const handleStatusChange = async (inspectionId: string, status: string) => {
    const now = new Date()
    setInspections(prev =>
      prev.map(i => 
        i.id === inspectionId 
          ? { 
              ...i, 
              status: status as any,
              ...(status === 'completed' && { completedAt: now }),
              updatedAt: now
            }
          : i
      )
    )
    
    // Update current inspection if it's the one being changed
    if (currentInspection?.id === inspectionId) {
      setCurrentInspection(prev => prev ? {
        ...prev,
        status: status as any,
        ...(status === 'completed' && { completedAt: now }),
        updatedAt: now
      } : null)
    }
  }

  const handleFieldChange = (inspectionId: string, fieldId: string, value: any) => {
    // This is handled automatically by the form renderer via onSaveInspection
    console.log('Field changed:', { inspectionId, fieldId, value })
  }

  // Create some sample data if none exists
  useEffect(() => {
    if (inspections.length === 0) {
      const sampleInspection: InspectionInstance = {
        id: 'sample-001',
        templateId: 'safety-001',
        title: 'Minta Biztonsági Ellenőrzés - Március 2024',
        description: 'Havi rendszeres biztonsági ellenőrzés',
        status: 'completed',
        priority: 'normal',
        assignedTo: 'user-001',
        assignedBy: 'user-003',
        assignedAt: new Date('2024-03-01'),
        gateId: 'gate-001',
        garageId: 'garage-001',
        fieldValues: [
          { fieldId: 'safety-lighting', value: true, timestamp: new Date('2024-03-01T10:00:00') },
          { fieldId: 'safety-emergency', value: 'Megfelelő', timestamp: new Date('2024-03-01T10:05:00') },
          { fieldId: 'safety-access', value: ['Rámpa', 'Széles ajtók'], timestamp: new Date('2024-03-01T10:10:00') },
          { fieldId: 'safety-temperature', value: 22, timestamp: new Date('2024-03-01T10:15:00') },
          { fieldId: 'safety-notes', value: 'Minden rendben, kisebb kopás az ajtó keretén.', timestamp: new Date('2024-03-01T10:20:00') }
        ],
        completedFields: ['safety-lighting', 'safety-emergency', 'safety-access', 'safety-temperature', 'safety-notes'],
        totalFields: 7,
        progressPercentage: 71,
        startedAt: new Date('2024-03-01T09:30:00'),
        completedAt: new Date('2024-03-01T10:25:00'),
        submittedAt: new Date('2024-03-01T10:30:00'),
        autoSaveEnabled: true,
        overallResult: 'pass',
        score: 92,
        criticalIssues: 0,
        minorIssues: 1,
        comments: [
          {
            id: 'comment-001',
            userId: 'user-001',
            userName: 'Kovács János',
            message: 'Ellenőrzés befejezve, minden fő biztonsági elem megfelelő.',
            timestamp: new Date('2024-03-01T10:25:00'),
            type: 'note'
          }
        ],
        createdAt: new Date('2024-03-01T09:00:00'),
        updatedAt: new Date('2024-03-01T10:30:00'),
        createdBy: 'user-003',
        version: 2,
        lastSavedAt: new Date('2024-03-01T10:25:00'),
        hasUnsavedChanges: false
      }
      
      setInspections([sampleInspection])
    }
  }, [inspections.length])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            🔍 Ellenőrzési Rendszer Demo
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Teljes ellenőrzési folyamat: indítás → kitöltés → lezárás. 
            Élő mentés, állapot helyreállítás, unsaved changes figyelmeztetés.
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="font-semibold text-gray-900 mb-2">🚀 Start Dialógus</h3>
            <p className="text-sm text-gray-600">
              Sablon választó kategóriákkal, szűrésekkel, becsült időtartammal. 
              Részletek megadása és automatikus címgenerálás.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="font-semibold text-gray-900 mb-2">💾 Élő Mentés</h3>
            <p className="text-sm text-gray-600">
              5 másodperces auto-save, lokális backup, offline működés. 
              Progress tracking és resumable sessions.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="font-semibold text-gray-900 mb-2">⚠️ Unsaved Changes</h3>
            <p className="text-sm text-gray-600">
              Kilépéskor figyelmeztetés, állapot helyreállítás visszatéréskor. 
              Browser beforeunload és navigation intercepting.
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Rendszer Statisztikák</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Sablonok:</span>
              <span className="ml-2 font-medium">{mockTemplates.length}</span>
            </div>
            <div>
              <span className="text-gray-600">Ellenőrzések:</span>
              <span className="ml-2 font-medium">{inspections.length}</span>
            </div>
            <div>
              <span className="text-gray-600">Befejezett:</span>
              <span className="ml-2 font-medium">
                {inspections.filter(i => i.status === 'completed' || i.status === 'submitted').length}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Folyamatban:</span>
              <span className="ml-2 font-medium">
                {inspections.filter(i => i.status === 'in_progress').length}
              </span>
            </div>
          </div>
        </div>

        {/* Available Templates Preview */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Elérhető Sablonok</h3>
          <div className="grid md:grid-cols-3 gap-4">
            {mockTemplates.map(template => {
              const category = INSPECTION_CATEGORIES[template.category]
              return (
                <div key={template.id} className="border rounded-lg p-4">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className={`w-10 h-10 bg-${category.color}-100 rounded-lg flex items-center justify-center text-lg`}>
                      {category.icon}
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{template.name}</h4>
                      <p className="text-xs text-gray-500">{category.label}</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>⏱️ ~{template.estimatedDuration} perc</span>
                    <span>📝 {template.fields.length} mező</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Main Inspection Manager */}
        <InspectionManager
          templates={mockTemplates}
          inspections={inspections}
          currentInspection={currentInspection}
          gates={mockGates}
          garages={mockGarages}
          users={mockUsers}
          onStartInspection={handleStartInspection}
          onSaveInspection={handleSaveInspection}
          onSubmitInspection={handleSubmitInspection}
          onFieldChange={handleFieldChange}
          onStatusChange={handleStatusChange}
          className="bg-white rounded-lg shadow-sm"
        />

        {/* Technical Info */}
        <div className="mt-8 bg-gray-900 text-white rounded-lg p-6">
          <h3 className="text-lg font-medium mb-4">🔧 Technikai Megvalósítás</h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div>
              <h4 className="font-medium text-gray-300 mb-2">Funkciók:</h4>
              <ul className="space-y-1 text-gray-400">
                <li>• Template-based ellenőrzési rendszer</li>
                <li>• 8 különböző mező típus (text, number, boolean, select, stb.)</li>
                <li>• Conditional logic mezők között</li>
                <li>• Real-time progress tracking</li>
                <li>• Auto-save 5 másodpercenként</li>
                <li>• localStorage backup és restore</li>
                <li>• Unsaved changes warning</li>
                <li>• Navigation intercepting</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-300 mb-2">Állapot Kezelés:</h4>
              <ul className="space-y-1 text-gray-400">
                <li>• Draft → In Progress → Completed → Submitted</li>
                <li>• Pause/Resume funkció</li>
                <li>• Validation minden lépésben</li>
                <li>• CRUD műveletek mock API-val</li>
                <li>• Type-safe Zod sémák</li>
                <li>• Comprehensive error handling</li>
                <li>• Offline működés támogatás</li>
                <li>• State persistence localStorage-ban</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}