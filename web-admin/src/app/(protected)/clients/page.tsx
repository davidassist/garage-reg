'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
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
  Upload
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { withAuth } from '@/lib/auth/with-auth'
import { PermissionResource, PermissionAction } from '@/lib/auth/types'
// Temporary toast implementation
const toast = ({ title, description, variant }: { title: string, description: string, variant?: string }) => {
  console.log(`${variant === 'destructive' ? 'ERROR' : 'INFO'}: ${title} - ${description}`)
  alert(`${title}: ${description}`)
}
import { cn } from '@/lib/utils'
// ClientForm will be imported later

interface Client {
  id: string
  name: string
  email: string
  phone: string
  address: string
  contactPerson: string
  taxNumber: string
  status: 'active' | 'inactive' | 'suspended'
  sitesCount: number
  buildingsCount: number
  gatesCount: number
  createdAt: string
  updatedAt: string
}

const mockClients: Client[] = [
  {
    id: '1',
    name: 'Budapesti Városkapu Kft.',
    email: 'info@varoskapu.hu',
    phone: '+36 1 234 5678',
    address: '1011 Budapest, Fő utca 1.',
    contactPerson: 'Nagy Péter',
    taxNumber: '12345678-2-41',
    status: 'active',
    sitesCount: 12,
    buildingsCount: 45,
    gatesCount: 89,
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-10-01T14:30:00Z'
  },
  {
    id: '2', 
    name: 'Debreceni Lakópark Zrt.',
    email: 'kapcsolat@debrecenilakopark.hu',
    phone: '+36 52 123 456',
    address: '4032 Debrecen, Egyetem sugárút 15.',
    contactPerson: 'Kovács Anna',
    taxNumber: '87654321-2-09',
    status: 'active',
    sitesCount: 8,
    buildingsCount: 24,
    gatesCount: 48,
    createdAt: '2024-02-20T09:15:00Z',
    updatedAt: '2024-09-28T16:45:00Z'
  },
  {
    id: '3',
    name: 'Szegedi Otthon Bt.',
    email: 'admin@szegediotthon.hu', 
    phone: '+36 62 789 012',
    address: '6720 Szeged, Tisza Lajos krt. 103.',
    contactPerson: 'Tóth László',
    taxNumber: '34567890-1-27',
    status: 'inactive',
    sitesCount: 3,
    buildingsCount: 8,
    gatesCount: 16,
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
  suspended: { 
    label: 'Felfüggesztve', 
    className: 'bg-red-100 text-red-800 border-red-200' 
  }
}

function ClientsPageContent() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedClient, setSelectedClient] = useState<Client | null>(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  
  const router = useRouter()
  const queryClient = useQueryClient()

  // Mock query for clients data
  const { data: clients = mockClients, isLoading } = useQuery({
    queryKey: ['clients', searchTerm],
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      if (searchTerm) {
        return mockClients.filter(client => 
          client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          client.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
          client.contactPerson.toLowerCase().includes(searchTerm.toLowerCase())
        )
      }
      
      return mockClients
    }
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      console.log('Deleting client:', id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] })
      toast({
        title: "Ügyfél törölve",
        description: "Az ügyfél sikeresen törölve lett."
      })
    },
    onError: () => {
      toast({
        title: "Hiba",
        description: "Az ügyfél törlése sikertelen.",
        variant: "destructive"
      })
    }
  })

  const handleEditClient = (client: Client) => {
    setSelectedClient(client)
    setIsEditDialogOpen(true)
  }

  const handleDeleteClient = (client: Client) => {
    if (confirm(`Biztosan törölni szeretné a következő ügyfelet: ${client.name}?`)) {
      deleteMutation.mutate(client.id)
    }
  }

  const handleViewSites = (client: Client) => {
    router.push(`/sites?client=${client.id}`)
  }

  const filteredClients = clients

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ügyfelek</h1>
          <p className="text-muted-foreground">
            Ügyfelek kezelése és információik megtekintése
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
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Új ügyfél
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Új ügyfél hozzáadása</DialogTitle>
                <DialogDescription>
                  Adja meg az új ügyfél adatait.
                </DialogDescription>
              </DialogHeader>
              {/* <ClientForm 
                onSubmit={() => setIsCreateDialogOpen(false)}
                onCancel={() => setIsCreateDialogOpen(false)}
              /> */}
              <div>Form coming soon...</div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Filters & Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Keresés név, email vagy kapcsolattartó alapján..."
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
            <CardTitle className="text-sm font-medium">Összes ügyfél</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{clients.length}</div>
            <p className="text-xs text-muted-foreground">
              {clients.filter(c => c.status === 'active').length} aktív
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Telephelyek</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {clients.reduce((sum, client) => sum + client.sitesCount, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Összesen
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
              {clients.reduce((sum, client) => sum + client.buildingsCount, 0)}
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
              {clients.reduce((sum, client) => sum + client.gatesCount, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Összesen
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Clients Table */}
      <Card>
        <CardHeader>
          <CardTitle>Ügyfél lista</CardTitle>
          <CardDescription>
            Az összes regisztrált ügyfél áttekintése
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Név</TableHead>
                  <TableHead>Kapcsolattartó</TableHead>
                  <TableHead>Elérhetőség</TableHead>
                  <TableHead>Státusz</TableHead>
                  <TableHead>Telephelyek</TableHead>
                  <TableHead>Épületek</TableHead>
                  <TableHead>Kapuk</TableHead>
                  <TableHead className="text-right">Műveletek</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredClients.map((client) => (
                  <TableRow key={client.id} className="hover:bg-muted/50">
                    <TableCell>
                      <div>
                        <div className="font-medium">{client.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {client.taxNumber}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{client.contactPerson}</div>
                        <div className="text-sm text-muted-foreground">
                          {client.address}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center text-sm">
                          <Mail className="mr-2 h-4 w-4 text-muted-foreground" />
                          {client.email}
                        </div>
                        <div className="flex items-center text-sm">
                          <Phone className="mr-2 h-4 w-4 text-muted-foreground" />
                          {client.phone}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={statusConfig[client.status].className}
                      >
                        {statusConfig[client.status].label}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-center">
                      <Button
                        variant="link"
                        className="h-auto p-0 text-primary"
                        onClick={() => handleViewSites(client)}
                      >
                        {client.sitesCount}
                      </Button>
                    </TableCell>
                    <TableCell className="text-center">{client.buildingsCount}</TableCell>
                    <TableCell className="text-center">{client.gatesCount}</TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" className="h-8 w-8 p-0">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Műveletek</DropdownMenuLabel>
                          <DropdownMenuItem onClick={() => handleViewSites(client)}>
                            <MapPin className="mr-2 h-4 w-4" />
                            Telephelyek megtekintése
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem onClick={() => handleEditClient(client)}>
                            <Edit className="mr-2 h-4 w-4" />
                            Szerkesztés
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={() => handleDeleteClient(client)}
                            className="text-red-600"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Törlés
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          
          {!isLoading && filteredClients.length === 0 && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Nincsenek ügyfelek a keresési feltételeknek megfelelően.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Ügyfél szerkesztése</DialogTitle>
            <DialogDescription>
              Módosítsa az ügyfél adatait.
            </DialogDescription>
          </DialogHeader>
          {selectedClient && (
            /* <ClientForm 
              client={selectedClient}
              onSubmit={() => setIsEditDialogOpen(false)}
              onCancel={() => setIsEditDialogOpen(false)}
            /> */
            <div>Edit form coming soon...</div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default withAuth(ClientsPageContent, {
  requireAuth: true,
  requiredPermission: { resource: PermissionResource.CLIENTS, action: PermissionAction.READ }
})