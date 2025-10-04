'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useRouter, useSearchParams } from 'next/navigation'
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Building2, 
  Phone, 
  Mail,
  MapPin,
  Users,
  MoreHorizontal,
  Filter,
  Download,
  Upload,
  ArrowLeft
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { withAuth } from '@/lib/auth/with-auth'
import { PermissionResource, PermissionAction } from '@/lib/auth/types'
import { cn } from '@/lib/utils'

// Temporary toast implementation
const toast = ({ title, description, variant }: { title: string, description: string, variant?: string }) => {
  console.log(`${variant === 'destructive' ? 'ERROR' : 'INFO'}: ${title} - ${description}`)
  alert(`${title}: ${description}`)
}

interface Site {
  id: string
  name: string
  clientId: string
  clientName: string
  address: string
  city: string
  postalCode: string
  contactPerson: string
  contactPhone: string
  contactEmail: string
  status: 'active' | 'inactive' | 'maintenance'
  buildingsCount: number
  gatesCount: number
  createdAt: string
  updatedAt: string
}

const mockSites: Site[] = [
  {
    id: '1',
    name: 'Buda Castle Business Center',
    clientId: '1',
    clientName: 'Budapesti Városkapu Kft.',
    address: 'Várhegy út 15.',
    city: 'Budapest',
    postalCode: '1014',
    contactPerson: 'Nagy Péter',
    contactPhone: '+36 1 234 5678',
    contactEmail: 'nagy.peter@varoskapu.hu',
    status: 'active',
    buildingsCount: 8,
    gatesCount: 24,
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-10-01T14:30:00Z'
  },
  {
    id: '2',
    name: 'Pest Central Office Complex',
    clientId: '1',
    clientName: 'Budapesti Városkapu Kft.',
    address: 'Váci út 130.',
    city: 'Budapest', 
    postalCode: '1138',
    contactPerson: 'Kovács Anna',
    contactPhone: '+36 1 345 6789',
    contactEmail: 'kovacs.anna@varoskapu.hu',
    status: 'active',
    buildingsCount: 12,
    gatesCount: 36,
    createdAt: '2024-02-20T09:15:00Z',
    updatedAt: '2024-09-28T16:45:00Z'
  },
  {
    id: '3',
    name: 'Debrecen Industrial Park',
    clientId: '2',
    clientName: 'Debreceni Lakópark Zrt.',
    address: 'Ipari park út 5.',
    city: 'Debrecen',
    postalCode: '4031',
    contactPerson: 'Szabó László',
    contactPhone: '+36 52 123 456',
    contactEmail: 'szabo.laszlo@debrecenilakopark.hu',
    status: 'maintenance',
    buildingsCount: 6,
    gatesCount: 18,
    createdAt: '2024-03-10T11:30:00Z',
    updatedAt: '2024-08-15T13:20:00Z'
  }
]

const statusConfig = {
  active: { 
    label: 'Aktív', 
    className: 'bg-green-100 text-green-800 border-green-200' 
  },
  inactive: { 
    label: 'Inaktív', 
    className: 'bg-gray-100 text-gray-800 border-gray-200' 
  },
  maintenance: { 
    label: 'Karbantartás', 
    className: 'bg-yellow-100 text-yellow-800 border-yellow-200' 
  }
}

function SitesPageContent() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSite, setSelectedSite] = useState<Site | null>(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  
  const router = useRouter()
  const searchParams = useSearchParams()
  const clientFilter = searchParams.get('client')

  // Mock query for sites data
  const { data: sites = mockSites, isLoading } = useQuery({
    queryKey: ['sites', searchTerm, clientFilter],
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      let filteredSites = mockSites

      // Filter by client if specified
      if (clientFilter) {
        filteredSites = filteredSites.filter(site => site.clientId === clientFilter)
      }

      // Filter by search term
      if (searchTerm) {
        filteredSites = filteredSites.filter(site => 
          site.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          site.clientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
          site.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
          site.contactPerson.toLowerCase().includes(searchTerm.toLowerCase())
        )
      }
      
      return filteredSites
    }
  })

  const handleEditSite = (site: Site) => {
    setSelectedSite(site)
    setIsEditDialogOpen(true)
  }

  const handleDeleteSite = (site: Site) => {
    if (confirm(`Biztosan törölni szeretné a következő telephelyet: ${site.name}?`)) {
      toast({
        title: "Telephely törölve",
        description: "A telephely sikeresen törölve lett."
      })
    }
  }

  const handleViewBuildings = (site: Site) => {
    router.push(`/buildings?site=${site.id}`)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            {clientFilter && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => router.push('/clients')}
                className="p-0 h-auto"
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Vissza az ügyfelekhez
              </Button>
            )}
          </div>
          <h1 className="text-3xl font-bold tracking-tight">
            Telephelyek
            {clientFilter && sites.length > 0 && (
              <span className="text-xl font-normal text-muted-foreground ml-2">
                - {sites[0].clientName}
              </span>
            )}
          </h1>
          <p className="text-muted-foreground">
            Telephelyek kezelése és információik megtekintése
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Upload className="mr-2 h-4 w-4" />
            Import
          </Button>
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button onClick={() => setIsCreateDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Új telephely
          </Button>
        </div>
      </div>

      {/* Filters & Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Keresés név, ügyfél, város vagy kapcsolattartó alapján..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" size="sm">
              <Filter className="mr-2 h-4 w-4" />
              Szűrők
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Összes telephely</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sites.length}</div>
            <p className="text-xs text-muted-foreground">
              {sites.filter(s => s.status === 'active').length} aktív
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Épületek</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sites.reduce((sum, site) => sum + site.buildingsCount, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Összesen
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Kapuk</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sites.reduce((sum, site) => sum + site.gatesCount, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Összesen
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Karbantartás</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sites.filter(s => s.status === 'maintenance').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Telephely
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Sites Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          Array.from({ length: 6 }, (_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : sites.length > 0 ? (
          sites.map((site) => (
            <Card key={site.id} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-lg">{site.name}</CardTitle>
                    <CardDescription className="text-sm">
                      {site.clientName}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={cn(
                      "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
                      statusConfig[site.status].className
                    )}>
                      {statusConfig[site.status].label}
                    </div>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <MapPin className="mr-2 h-4 w-4" />
                    {site.address}, {site.city}
                  </div>
                  
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Users className="mr-2 h-4 w-4" />
                    {site.contactPerson}
                  </div>

                  <div className="flex items-center text-sm text-muted-foreground">
                    <Phone className="mr-2 h-4 w-4" />
                    {site.contactPhone}
                  </div>

                  <div className="grid grid-cols-2 gap-4 mt-4 pt-3 border-t">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">
                        {site.buildingsCount}
                      </div>
                      <div className="text-xs text-muted-foreground">Épület</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">
                        {site.gatesCount}
                      </div>
                      <div className="text-xs text-muted-foreground">Kapu</div>
                    </div>
                  </div>

                  <div className="flex gap-2 pt-3">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1"
                      onClick={() => handleViewBuildings(site)}
                    >
                      <Building2 className="mr-2 h-4 w-4" />
                      Épületek
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleEditSite(site)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleDeleteSite(site)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <MapPin className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nincsenek telephelyek</h3>
            <p className="mt-1 text-sm text-gray-500">
              {clientFilter 
                ? "Ez az ügyfél még nem rendelkezik telephelyekkel."
                : "Kezdje el az első telephely hozzáadásával."
              }
            </p>
            <div className="mt-6">
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Új telephely
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default withAuth(SitesPageContent, {
  requireAuth: true,
  requiredPermission: { resource: PermissionResource.SITES, action: PermissionAction.READ }
})