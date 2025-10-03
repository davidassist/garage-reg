'use client'

import { useState } from 'react'
import { Gate } from '@/lib/types/gate'
import { 
  MapPin, 
  Calendar, 
  Settings, 
  Battery, 
  Wifi,
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  ChevronDown,
  ChevronRight
} from 'lucide-react'

interface OverviewTabProps {
  gate: Gate
  onUpdate: (gate: Gate) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

interface CollapsibleSectionProps {
  title: string
  icon: React.ReactNode
  children: React.ReactNode
  defaultExpanded?: boolean
}

function CollapsibleSection({ 
  title, 
  icon, 
  children, 
  defaultExpanded = true 
}: CollapsibleSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center space-x-3">
          {icon}
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
        </div>
        {isExpanded ? (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronRight className="h-5 w-5 text-gray-400" />
        )}
      </button>
      
      {isExpanded && (
        <div className="border-t border-gray-200 p-4 animate-fadeIn">
          {children}
        </div>
      )}
    </div>
  )
}

export function OverviewTab({ gate, onUpdate, isLoading, setIsLoading }: OverviewTabProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'inactive':
        return <XCircle className="h-5 w-5 text-red-600" />
      case 'maintenance':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />
      default:
        return <Clock className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'inactive':
        return 'bg-red-100 text-red-800'
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'Nincs megadva'
    return new Date(dateString).toLocaleDateString('hu-HU')
  }

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg text-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">{gate.name}</h2>
            <p className="text-blue-100 mt-1">{gate.code}</p>
          </div>
          <div className="flex items-center space-x-4">
            {getStatusIcon(gate.status)}
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(gate.status)}`}>
              {gate.status === 'active' ? 'Aktív' : 
               gate.status === 'inactive' ? 'Inaktív' : 
               gate.status === 'maintenance' ? 'Karbantartás alatt' : 'Ismeretlen'}
            </span>
          </div>
        </div>
      </div>

      {/* Basic Information */}
      <CollapsibleSection
        title="Alapadatok"
        icon={<Settings className="h-5 w-5 text-blue-600" />}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Típus</label>
              <p className="text-gray-900">{gate.type || 'Nincs megadva'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Helyszín</label>
              <div className="flex items-center space-x-2">
                <MapPin className="h-4 w-4 text-gray-400" />
                <p className="text-gray-900">{gate.location || 'Nincs megadva'}</p>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Leírás</label>
              <p className="text-gray-900">{gate.notes || 'Nincs leírás'}</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Telepítés dátuma</label>
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-gray-400" />
                <p className="text-gray-900">{formatDate(gate.installationDate)}</p>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Garancia lejárata</label>
              <div className="flex items-center space-x-2">
                <Shield className="h-4 w-4 text-gray-400" />
                <p className="text-gray-900">{formatDate(gate.warrantyExpiry)}</p>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Utolsó karbantartás</label>
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-gray-400" />
                <p className="text-gray-900">{formatDate(gate.lastMaintenance)}</p>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      {/* Technical Specifications */}
      <CollapsibleSection
        title="Műszaki specifikáció"
        icon={<Settings className="h-5 w-5 text-purple-600" />}
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900 border-b border-gray-200 pb-2">Motor</h4>
            <div>
              <label className="text-sm font-medium text-gray-500">Típus</label>
              <p className="text-gray-900">{gate.motorType || 'Nincs megadva'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Teljesítmény</label>
              <p className="text-gray-900">{gate.motorPower ? `${gate.motorPower} W` : 'Nincs megadva'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Sebesség</label>
              <p className="text-gray-900">{'Nincs megadva'}</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900 border-b border-gray-200 pb-2">Vezérlő</h4>
            <div>
              <label className="text-sm font-medium text-gray-500">Típus</label>
              <p className="text-gray-900">{gate.controllerType || 'Nincs megadva'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Feszültség</label>
              <p className="text-gray-900">{'Nincs megadva'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Frekvencia</label>
              <p className="text-gray-900">{'Nincs megadva'}</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900 border-b border-gray-200 pb-2">Méretek</h4>
            <div>
              <label className="text-sm font-medium text-gray-500">Szélesség</label>
              <p className="text-gray-900">{gate.width ? `${gate.width} mm` : 'Nincs megadva'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Magasság</label>
              <p className="text-gray-900">{gate.height ? `${gate.height} mm` : 'Nincs megadva'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Súly</label>
              <p className="text-gray-900">{gate.weight ? `${gate.weight} kg` : 'Nincs megadva'}</p>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      {/* Quick Stats */}
      <CollapsibleSection
        title="Gyors áttekintés"
        icon={<Battery className="h-5 w-5 text-green-600" />}
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              0
            </div>
            <div className="text-sm text-gray-600">Ciklusok</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              99.9%
            </div>
            <div className="text-sm text-gray-600">Üzemidő</div>
          </div>
          
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">
              85%
            </div>
            <div className="text-sm text-gray-600">Akkumulátor</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              <Wifi className="h-8 w-8 mx-auto" />
            </div>
            <div className="text-sm text-gray-600">
              Kapcsolódva
            </div>
          </div>
        </div>
      </CollapsibleSection>
    </div>
  )
}