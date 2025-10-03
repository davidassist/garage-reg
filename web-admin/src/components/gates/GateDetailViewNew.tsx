'use client'

import { useState, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'react-hot-toast'
import { 
  ArrowLeft, 
  Edit2, 
  Settings,
  ExternalLink,
  MoreVertical,
  Eye,
  Copy
} from 'lucide-react'
import { Gate } from '@/lib/types/api'
import { GateDetailTab } from '@/lib/types/gate-detail'
import { OverviewTab } from './tabs/OverviewTab'
import { ComponentsTab } from './tabs/ComponentsTab'
import { HistoryTab } from './tabs/HistoryTab'
import { DocumentsTab } from './tabs/DocumentsTab'
import { TemplatesTab } from './tabs/TemplatesTab'

interface GateDetailViewProps {
  gate: Gate
  onUpdate?: (updatedGate: Gate) => void
}

const tabs: Array<{
  id: GateDetailTab
  label: string
  icon: React.ComponentType<{ className?: string }>
}> = [
  { id: 'overview', label: 'Áttekintés', icon: Eye },
  { id: 'components', label: 'Komponensek', icon: Settings },
  { id: 'history', label: 'Előzmények', icon: Copy },
  { id: 'documents', label: 'Dokumentumok', icon: ExternalLink },
  { id: 'templates', label: 'Sablonok', icon: MoreVertical }
]

export function GateDetailView({ gate, onUpdate }: GateDetailViewProps) {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<GateDetailTab>('overview')
  const [isLoading, setIsLoading] = useState(false)

  const handleBack = useCallback(() => {
    router.back()
  }, [router])

  const handleEdit = useCallback(() => {
    router.push(`/gates/${gate.id}/edit`)
  }, [router, gate.id])

  const handleGateUpdate = useCallback((updatedGate: Gate) => {
    onUpdate?.(updatedGate)
    toast.success('Kapu sikeresen frissítve')
  }, [onUpdate])

  // Memoize tab content to prevent unnecessary re-renders
  const activeTabContent = useMemo(() => {
    switch (activeTab) {
      case 'overview':
        return (
          <OverviewTab 
            gate={gate} 
            onUpdate={handleGateUpdate}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )
      case 'components':
        return (
          <ComponentsTab 
            gateId={gate.id}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )
      case 'history':
        return (
          <HistoryTab 
            gateId={gate.id}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )
      case 'documents':
        return (
          <DocumentsTab 
            gateId={gate.id}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )
      case 'templates':
        return (
          <TemplatesTab 
            gateId={gate.id}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )
      default:
        return null
    }
  }, [activeTab, gate, handleGateUpdate, isLoading])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleBack}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 transition-colors"
                title="Vissza"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  {gate.name || `Kapu #${gate.id}`}
                </h1>
                <p className="text-sm text-gray-500">
                  {gate.type} • {gate.location || 'Helyszín nincs megadva'}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleEdit}
                disabled={isLoading}
                className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <Edit2 className="h-4 w-4 mr-2" />
                Szerkesztés
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex space-x-0 -mb-px">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  disabled={isLoading}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium border-b-2 transition-colors
                    ${isActive
                      ? 'border-blue-500 text-blue-600 bg-blue-50'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                    disabled:opacity-50
                  `}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  <span className="hidden sm:inline">{tab.label}</span>
                  <span className="sm:hidden">
                    {tab.label.split(' ')[0]}
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="transform transition-all duration-300 ease-in-out">
          {activeTabContent}
        </div>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <div>
                <div className="text-sm font-medium text-gray-900">Betöltés...</div>
                <div className="text-xs text-gray-500">Kérjük várjon</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}