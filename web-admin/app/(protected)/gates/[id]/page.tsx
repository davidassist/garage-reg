'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  ArrowLeft, 
  Edit, 
  Settings, 
  History, 
  FileText, 
  CheckSquare,
  MapPin,
  Calendar,
  User,
  Wrench,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react'
import Link from 'next/link'
import { GateOverview } from './components/GateOverview'
import { GateComponents } from './components/GateComponents'
import { GateHistory } from './components/GateHistory'
import { GateDocuments } from './components/GateDocuments'
import { InspectionTemplates } from './components/InspectionTemplates'
import { toast } from '@/components/ui/use-toast'

// Mock data - replace with API calls
const mockGate = {
  id: '1',
  name: 'Főbejárat Kapu #1',
  type: 'entrance',
  status: 'active',
  siteId: 'site-001',
  siteName: 'Budapest Központi Telephely',
  manufacturer: 'CAME',
  model: 'BX-243',
  serialNumber: 'CAME2024001',
  installationDate: '2024-01-15',
  lastMaintenance: '2024-09-15',
  nextMaintenance: '2024-12-15',
  dimensions: {
    width: 4.5,
    height: 2.1,
    weight: 150
  },
  motor: {
    type: 'hydraulic',
    power: 230,
    manufacturer: 'CAME',
    model: 'BZ-25'
  },
  location: {
    address: '1052 Budapest, Váci utca 45.',
    coordinates: '47.4979° N, 19.0402° E'
  },
  warranty: {
    startDate: '2024-01-15',
    endDate: '2026-01-15',
    provider: 'CAME Magyarország Kft.'
  },
  technicalSpecs: {
    maxWeight: 500,
    operationTemperature: '-20°C to +60°C',
    powerSupply: '230V AC, 50Hz',
    openingTime: '12s',
    closingTime: '12s',
    remoteFrequency: '433.92 MHz'
  }
}

const statusConfig = {
  active: { label: 'Aktív', color: 'bg-green-500', textColor: 'text-green-700' },
  maintenance: { label: 'Karbantartás alatt', color: 'bg-yellow-500', textColor: 'text-yellow-700' },
  inactive: { label: 'Inaktív', color: 'bg-gray-500', textColor: 'text-gray-700' },
  error: { label: 'Hiba', color: 'bg-red-500', textColor: 'text-red-700' }
}

export default function GateDetailPage({ 
  params 
}: { 
  params: { id: string } 
}) {
  const router = useRouter()
  const [gate, setGate] = useState(mockGate)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    // Load gate data
    setLoading(true)
    // Simulate API call
    setTimeout(() => {
      setGate({ ...mockGate, id: params.id })
      setLoading(false)
    }, 500)
  }, [params.id])

  const handleEdit = () => {
    router.push(`/gates/${params.id}/edit`)
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  const statusInfo = statusConfig[gate.status as keyof typeof statusConfig]

  return (
    <div className="container mx-auto py-8 space-y-6">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center space-x-2 text-sm text-muted-foreground">
        <Link 
          href="/gates" 
          className="flex items-center hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Kapuk
        </Link>
        <span>/</span>
        <span className="font-medium text-foreground">{gate.name}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between space-y-4 lg:space-y-0">
        <div className="space-y-2">
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-bold">{gate.name}</h1>
            <Badge 
              variant="secondary" 
              className={`${statusInfo.color} text-white`}
            >
              {statusInfo.label}
            </Badge>
          </div>
          
          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
            <div className="flex items-center">
              <MapPin className="h-4 w-4 mr-1" />
              {gate.siteName}
            </div>
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-1" />
              Telepítve: {new Date(gate.installationDate).toLocaleDateString('hu-HU')}
            </div>
            <div className="flex items-center">
              <User className="h-4 w-4 mr-1" />
              {gate.manufacturer} {gate.model}
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <Button onClick={handleEdit} variant="default">
            <Edit className="h-4 w-4 mr-2" />
            Szerkesztés
          </Button>
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Beállítások
          </Button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center justify-center w-10 h-10 bg-green-100 rounded-full mr-4">
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Állapot</p>
              <p className="text-2xl font-bold">{statusInfo.label}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-full mr-4">
              <Wrench className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Utolsó karbantartás</p>
              <p className="text-lg font-semibold">
                {new Date(gate.lastMaintenance).toLocaleDateString('hu-HU')}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center justify-center w-10 h-10 bg-orange-100 rounded-full mr-4">
              <Clock className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Következő karbantartás</p>
              <p className="text-lg font-semibold">
                {new Date(gate.nextMaintenance).toLocaleDateString('hu-HU')}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center justify-center w-10 h-10 bg-purple-100 rounded-full mr-4">
              <AlertTriangle className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Garancia</p>
              <p className="text-lg font-semibold">
                {new Date(gate.warranty.endDate) > new Date() ? 'Érvényes' : 'Lejárt'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs Section */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-2 lg:grid-cols-5">
          <TabsTrigger value="overview" className="flex items-center">
            <CheckCircle className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">Áttekintés</span>
          </TabsTrigger>
          <TabsTrigger value="components" className="flex items-center">
            <Settings className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">Komponensek</span>
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center">
            <History className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">Előzmények</span>
          </TabsTrigger>
          <TabsTrigger value="documents" className="flex items-center">
            <FileText className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">Dokumentumok</span>
          </TabsTrigger>
          <TabsTrigger value="templates" className="flex items-center">
            <CheckSquare className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">Sablonok</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <GateOverview gate={gate} />
        </TabsContent>

        <TabsContent value="components" className="space-y-6">
          <GateComponents gateId={gate.id} />
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <GateHistory gateId={gate.id} />
        </TabsContent>

        <TabsContent value="documents" className="space-y-6">
          <GateDocuments gateId={gate.id} />
        </TabsContent>

        <TabsContent value="templates" className="space-y-6">
          <InspectionTemplates gateId={gate.id} />
        </TabsContent>
      </Tabs>
    </div>
  )
}