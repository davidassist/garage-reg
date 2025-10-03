import { useState } from 'react'
import { useClients } from '@/hooks/api'
import { usePermissions } from '@/hooks/permissions'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { 
  Plus,
  Search,
  MoreHorizontal,
  Edit2,
  Trash2,
  Users,
  AlertTriangle
} from 'lucide-react'
import type { Client } from '@/types/api'

export function ClientsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const { canCreateClient, canEditClient, canDeleteClient } = usePermissions()
  const { data: clientsData, isLoading, error } = useClients(page, 20)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Hiba történt az ügyfelek betöltése során. Kérjük, próbálja újra később.
        </AlertDescription>
      </Alert>
    )
  }

  const clients = clientsData?.items || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Ügyfelek</h1>
          <p className="text-gray-600">
            Ügyfelek kezelése és adminisztrációja
          </p>
        </div>
        
        {canCreateClient() && (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Új ügyfél
          </Button>
        )}
      </div>

      {/* Search and filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Keresés ügyfelek között..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
            </div>
            <Button variant="outline">
              Szűrés
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Clients list */}
      <div className="grid gap-6">
        {clients.length > 0 ? (
          clients.map((client: Client) => (
            <Card key={client.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                      <Users className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">
                        {client.display_name || client.name}
                      </CardTitle>
                      <CardDescription>
                        ID: {client.id} • 
                        {client.contact_email && ` ${client.contact_email} • `}
                        {client.sites?.length || 0} telephely
                      </CardDescription>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Badge variant={client.is_active ? "default" : "secondary"}>
                      {client.is_active ? "Aktív" : "Inaktív"}
                    </Badge>
                    
                    <div className="flex items-center space-x-1">
                      {canEditClient() && (
                        <Button variant="ghost" size="icon">
                          <Edit2 className="h-4 w-4" />
                        </Button>
                      )}
                      
                      {canDeleteClient() && (
                        <Button variant="ghost" size="icon">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                      
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              {(client.address || client.contact_phone) && (
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                    {client.address && (
                      <div>
                        <span className="font-medium">Cím:</span> {client.address}
                      </div>
                    )}
                    {client.contact_phone && (
                      <div>
                        <span className="font-medium">Telefon:</span> {client.contact_phone}
                      </div>
                    )}
                  </div>
                </CardContent>
              )}
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Users className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Nincsenek ügyfelek
              </h3>
              <p className="text-gray-600 text-center mb-4">
                Még nincsenek ügyfelek regisztrálva a rendszerben.
              </p>
              {canCreateClient() && (
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Első ügyfél létrehozása
                </Button>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Pagination */}
      {clientsData && clientsData.pages > 1 && (
        <div className="flex items-center justify-center space-x-2">
          <Button
            variant="outline"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
          >
            Előző
          </Button>
          <span className="text-sm text-gray-600">
            {page} / {clientsData.pages} oldal
          </span>
          <Button
            variant="outline"
            disabled={page >= clientsData.pages}
            onClick={() => setPage(page + 1)}
          >
            Következő
          </Button>
        </div>
      )}
    </div>
  )
}