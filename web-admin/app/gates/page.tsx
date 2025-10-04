'use client'

import { useState } from 'react'
import { toast } from 'react-hot-toast'
import { Trash2 } from 'lucide-react'

import { 
  Gate, 
  CreateGateRequest, 
  UpdateGateRequest,
  GateStatus,
  GateType,
  ControllerType,
  MotorType,
} from '@/lib/types/gate'
import GateTable from '@/components/gates/GateTable'
import GateForm from '@/components/gates/GateForm'
import GateDetailView from '@/components/gates/GateDetailView'

// Mock data for demonstration
const mockGates: Gate[] = [
  {
    id: '1',
    name: 'Főbejárat kapu',
    code: 'GATE-001',
    type: GateType.SWING,
    size: 'medium',
    status: GateStatus.ACTIVE,
    serialNumber: 'SN123456789',
    manufacturer: 'CAME',
    model: 'ATI 3000',
    yearOfManufacture: 2022,
    width: 3.5,
    height: 2.0,
    weight: 150,
    controllerType: ControllerType.REMOTE,
    controllerModel: 'ZA3P',
    remoteControls: 2,
    motorType: MotorType.AC,
    motorPower: 550,
    motorModel: 'BX-243',
    gearboxRatio: '1:20',
    springs: {
      type: 'Torziós',
      count: 2,
      tension: 'Közepes',
    },
    rails: {
      type: 'Acél',
      length: 4.0,
      material: 'Galvanizált acél',
    },
    photocells: {
      count: 2,
      type: 'Infravörös',
      range: 10,
    },
    edgeProtection: {
      type: 'Gumiszalag',
      location: 'Alsó él',
      sensitivity: 'Magas',
    },
    manualRelease: {
      type: 'Kulcsos',
      location: 'Belső oldal',
      keyType: 'Háromszög',
    },
    location: 'Főépület bejárat',
    installationDate: '2022-05-15T00:00:00Z',
    installerCompany: 'TechGate Kft.',
    lastMaintenance: '2024-08-15T00:00:00Z',
    nextMaintenance: '2025-02-15T00:00:00Z',
    maintenanceInterval: 180,
    notes: 'Rendszeres karbantartás szükséges. Télen különös figyelmet kell fordítani a fagyás elleni védelemre.',
    manualUrl: 'https://came.com/manuals/ati3000.pdf',
    warrantyExpiry: '2025-05-15T00:00:00Z',
    createdAt: '2022-05-15T10:30:00Z',
    updatedAt: '2024-08-15T14:20:00Z',
    createdBy: 'admin@garagereg.hu',
    updatedBy: 'technician@garagereg.hu',
  },
  {
    id: '2',
    name: 'Teherkapu',
    code: 'GATE-002',
    type: GateType.SLIDING,
    size: 'large',
    status: GateStatus.MAINTENANCE,
    serialNumber: 'SN987654321',
    manufacturer: 'BFT',
    model: 'ICARO N',
    yearOfManufacture: 2021,
    width: 8.0,
    height: 2.5,
    weight: 800,
    controllerType: ControllerType.AUTOMATIC,
    controllerModel: 'CLONIX 2E',
    remoteControls: 5,
    motorType: MotorType.DC,
    motorPower: 1200,
    motorModel: 'PEGASO',
    photocells: {
      count: 4,
      type: 'Dual-beam',
    },
    edgeProtection: {
      type: 'Pneumatikus',
      location: 'Teljes él',
    },
    manualRelease: {
      type: 'Bowdenes',
      location: 'Kaputól 5m',
    },
    location: 'Rakodó terület',
    installationDate: '2021-09-20T00:00:00Z',
    installerCompany: 'AutoGate Solutions',
    lastMaintenance: '2024-09-01T00:00:00Z',
    nextMaintenance: '2024-12-01T00:00:00Z',
    maintenanceInterval: 90,
    notes: 'Nehéz használat miatt gyakoribb karbantartás szükséges.',
    createdAt: '2021-09-20T08:15:00Z',
    updatedAt: '2024-09-01T11:45:00Z',
    createdBy: 'admin@garagereg.hu',
    updatedBy: 'maintenance@garagereg.hu',
  },
  {
    id: '3',
    name: 'Parkoló sorompó',
    code: 'GATE-003',
    type: GateType.BARRIER,
    size: 'small',
    status: GateStatus.ACTIVE,
    serialNumber: 'SN555666777',
    manufacturer: 'Nice',
    model: 'WIDE M',
    yearOfManufacture: 2023,
    width: 4.0,
    controllerType: ControllerType.CARD_READER,
    controllerModel: 'MC824H',
    motorType: MotorType.DC,
    motorPower: 130,
    photocells: {
      count: 2,
      type: 'Safety',
    },
    location: 'Alkalmazotti parkoló',
    installationDate: '2023-03-10T00:00:00Z',
    installerCompany: 'SmartAccess Bt.',
    lastMaintenance: '2024-09-10T00:00:00Z',
    nextMaintenance: '2025-03-10T00:00:00Z',
    maintenanceInterval: 180,
    createdAt: '2023-03-10T13:20:00Z',
    updatedAt: '2024-09-10T09:30:00Z',
    createdBy: 'admin@garagereg.hu',
  },
]

interface DeleteConfirmDialogProps {
  isOpen: boolean
  gate: Gate | null
  onConfirm: () => void
  onCancel: () => void
}

function DeleteConfirmDialog({ isOpen, gate, onConfirm, onCancel }: DeleteConfirmDialogProps) {
  if (!isOpen || !gate) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="p-6">
          <div className="flex items-center mb-4">
            <div className="flex-shrink-0 w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <Trash2 className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">
                Kapu törlése
              </h3>
              <p className="text-sm text-gray-500">
                Ez a művelet nem vonható vissza.
              </p>
            </div>
          </div>
          
          <div className="mb-4">
            <p className="text-gray-700">
              Biztosan törölni szeretné a <strong>{gate.name}</strong> ({gate.code}) kaput?
            </p>
          </div>

          <div className="flex items-center justify-end space-x-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Mégse
            </button>
            <button
              onClick={onConfirm}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Törlés
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function GatesPage() {
  const [gates, setGates] = useState<Gate[]>(mockGates)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isDetailViewOpen, setIsDetailViewOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedGate, setSelectedGate] = useState<Gate | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleCreateNew = () => {
    setSelectedGate(null)
    setIsFormOpen(true)
  }

  const handleEdit = (gate: Gate) => {
    setSelectedGate(gate)
    setIsFormOpen(true)
  }

  const handleView = (gate: Gate) => {
    setSelectedGate(gate)
    setIsDetailViewOpen(true)
  }

  const handleDelete = (gate: Gate) => {
    setSelectedGate(gate)
    setIsDeleteDialogOpen(true)
  }

  const handleFormSubmit = async (data: CreateGateRequest | UpdateGateRequest) => {
    setIsSubmitting(true)
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      if (selectedGate) {
        // Update existing gate
        const updatedGate: Gate = {
          ...selectedGate,
          ...data,
          updatedAt: new Date().toISOString(),
          updatedBy: 'current-user@garagereg.hu', // This would come from auth context
        }
        
        setGates(prev => prev.map(gate => 
          gate.id === selectedGate.id ? updatedGate : gate
        ))
        
        toast.success('Kapu sikeresen frissítve!')
      } else {
        // Create new gate
        const newGate: Gate = {
          id: Math.random().toString(36).substr(2, 9),
          ...data as CreateGateRequest,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          createdBy: 'current-user@garagereg.hu', // This would come from auth context
        }
        
        setGates(prev => [newGate, ...prev])
        toast.success('Új kapu sikeresen létrehozva!')
      }
      
      setIsFormOpen(false)
      setSelectedGate(null)
    } catch (error) {
      toast.error('Hiba történt a kapu mentése során.')
      console.error('Gate save error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteConfirm = async () => {
    if (!selectedGate) return
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      setGates(prev => prev.filter(gate => gate.id !== selectedGate.id))
      toast.success('Kapu sikeresen törölve!')
      
      setIsDeleteDialogOpen(false)
      setSelectedGate(null)
    } catch (error) {
      toast.error('Hiba történt a kapu törlése során.')
      console.error('Gate delete error:', error)
    }
  }

  const handleDetailEdit = () => {
    setIsDetailViewOpen(false)
    setIsFormOpen(true)
  }

  const handleDetailDelete = () => {
    setIsDetailViewOpen(false)
    setIsDeleteDialogOpen(true)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Kapuk kezelése</h1>
        <p className="mt-1 text-sm text-gray-600">
          Itt kezelheti a garázs kapuit, szerkesztheti az adataikat és követheti a karbantartási ciklusokat.
        </p>
      </div>

      <GateTable
        gates={gates}
        onEdit={handleEdit}
        onView={handleView}
        onDelete={handleDelete}
        onCreateNew={handleCreateNew}
      />

      <GateForm
        gate={selectedGate}
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false)
          setSelectedGate(null)
        }}
        onSubmit={handleFormSubmit}
        isSubmitting={isSubmitting}
      />

      {selectedGate && (
        <GateDetailView
          gate={selectedGate}
          isOpen={isDetailViewOpen}
          onClose={() => {
            setIsDetailViewOpen(false)
            setSelectedGate(null)
          }}
          onEdit={handleDetailEdit}
          onDelete={handleDetailDelete}
        />
      )}

      <DeleteConfirmDialog
        isOpen={isDeleteDialogOpen}
        gate={selectedGate}
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setIsDeleteDialogOpen(false)
          setSelectedGate(null)
        }}
      />
    </div>
  )
}