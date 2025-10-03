'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  Download, 
  Printer, 
  Settings, 
  Eye, 
  QrCode, 
  FileText, 
  AlertCircle,
  CheckCircle2,
  Upload,
  X
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Checkbox } from '@/components/ui/checkbox'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { QRLabelsAPI, BulkLabelRequest as APIBulkLabelRequest } from '@/lib/services/qr-labels-api'

// Temporary toast implementation
const toast = ({ title, description, variant }: { title: string, description?: string, variant?: 'default' | 'destructive' }) => {
  console.log(`${variant === 'destructive' ? 'ERROR' : 'INFO'}: ${title}${description ? ` - ${description}` : ''}`)
  alert(`${title}${description ? `: ${description}` : ''}`)
}

interface Gate {
  id: string
  name: string
  buildingName: string
  siteName: string
  clientName: string
  gateType: string
  location: string
  serialNumber: string
  status: string
  factoryQR?: string
}

interface BulkLabelRequest {
  gateIds?: string[]
  buildingIds?: string[]
  siteIds?: string[]
  clientIds?: string[]
  includeInactive?: boolean
  labelsPerRow?: number
  labelsPerPage?: number
}

interface LabelConfig {
  labelsPerRow: number
  labelsPerPage: number
  includeQR: boolean
  includeBarcode: boolean
  includeInfo: boolean
  paperSize: 'A4' | 'A5' | 'LETTER'
}

interface BulkLabelGeneratorProps {
  selectedGates?: Gate[]
  onClose?: () => void
}

export function BulkLabelGenerator({ selectedGates = [], onClose }: BulkLabelGeneratorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [config, setConfig] = useState<LabelConfig>({
    labelsPerRow: 3,
    labelsPerPage: 9,
    includeQR: true,
    includeBarcode: false,
    includeInfo: true,
    paperSize: 'A4'
  })
  const [filterType, setFilterType] = useState<'selected' | 'building' | 'site' | 'client'>('selected')
  const [selectedEntityId, setSelectedEntityId] = useState('')

  // Mock data for entities
  const buildings = [
    { id: '1', name: 'A épület', siteName: 'Központi telephely' },
    { id: '2', name: 'B épület', siteName: 'Központi telephely' },
    { id: '3', name: 'Gyártócsarnok', siteName: 'Ipari park' }
  ]

  const sites = [
    { id: '1', name: 'Központi telephely', clientName: 'Budapest Parkolás Kft.' },
    { id: '2', name: 'Ipari park', clientName: 'LogiCenter Zrt.' },
    { id: '3', name: 'Bevásárlóközpont', clientName: 'RetailHub Ltd.' }
  ]

  const clients = [
    { id: '1', name: 'Budapest Parkolás Kft.' },
    { id: '2', name: 'LogiCenter Zrt.' },
    { id: '3', name: 'RetailHub Ltd.' }
  ]

  const handleGenerate = async () => {
    setIsGenerating(true)
    
    try {
      const request: APIBulkLabelRequest = {
        labelsPerRow: config.labelsPerRow,
        labelsPerPage: config.labelsPerPage,
        includeInactive: false
      }

      // Set filter based on selection
      switch (filterType) {
        case 'selected':
          request.gateIds = selectedGates.map(g => g.id)
          break
        case 'building':
          request.buildingIds = selectedEntityId ? [selectedEntityId] : []
          break
        case 'site':
          request.siteIds = selectedEntityId ? [selectedEntityId] : []
          break
        case 'client':
          request.clientIds = selectedEntityId ? [selectedEntityId] : []
          break
      }

      // Use real API
      await QRLabelsAPI.downloadBulkLabels(request, `qr_labels_${getGateCount()}_gates.pdf`)

      toast({
        title: 'PDF generálva',
        description: 'A QR címkék PDF-je sikeresen letöltődött'
      })

    } catch (error) {
      console.error('PDF generation failed:', error)
      toast({
        title: 'Hiba történt',
        description: 'A PDF generálása sikertelen volt',
        variant: 'destructive'
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handlePreview = async () => {
    // Generate sample preview
    toast({
      title: 'Előnézet',
      description: 'A címkék előnézete új ablakban nyílik meg'
    })
  }

  const getGateCount = (): number => {
    switch (filterType) {
      case 'selected':
        return selectedGates.length
      case 'building':
        return selectedEntityId ? 5 : 0 // Mock count
      case 'site':
        return selectedEntityId ? 12 : 0 // Mock count
      case 'client':
        return selectedEntityId ? 25 : 0 // Mock count
      default:
        return 0
    }
  }

  const handleClose = () => {
    setIsOpen(false)
    onClose?.()
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <QrCode className="h-4 w-4 mr-2" />
          Tömeges címke
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <QrCode className="h-5 w-5" />
            QR címkék tömeges generálása
          </DialogTitle>
          <DialogDescription>
            Válassza ki a címkézendő kapukat és állítsa be a formátumot
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Kapu kiválasztás */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Kapuk kiválasztása</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Szűrő típusa</Label>
                  <Select value={filterType} onValueChange={(value: any) => setFilterType(value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="selected">Kiválasztott kapuk ({selectedGates.length})</SelectItem>
                      <SelectItem value="building">Épület szerint</SelectItem>
                      <SelectItem value="site">Telephely szerint</SelectItem>
                      <SelectItem value="client">Ügyfél szerint</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {filterType !== 'selected' && (
                  <div className="space-y-2">
                    <Label>
                      {filterType === 'building' && 'Épület'}
                      {filterType === 'site' && 'Telephely'}
                      {filterType === 'client' && 'Ügyfél'}
                    </Label>
                    <Select value={selectedEntityId} onValueChange={setSelectedEntityId}>
                      <SelectTrigger>
                        <SelectValue placeholder="Válasszon..." />
                      </SelectTrigger>
                      <SelectContent>
                        {filterType === 'building' && buildings.map(building => (
                          <SelectItem key={building.id} value={building.id}>
                            {building.name} ({building.siteName})
                          </SelectItem>
                        ))}
                        {filterType === 'site' && sites.map(site => (
                          <SelectItem key={site.id} value={site.id}>
                            {site.name} ({site.clientName})
                          </SelectItem>
                        ))}
                        {filterType === 'client' && clients.map(client => (
                          <SelectItem key={client.id} value={client.id}>
                            {client.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>

              {getGateCount() > 0 && (
                <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-md">
                  <CheckCircle2 className="h-4 w-4 text-blue-600" />
                  <span className="text-sm text-blue-800">
                    {getGateCount()} kapu lesz címkézve
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Címke beállítások */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Címke formátum</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Papír méret</Label>
                  <Select value={config.paperSize} onValueChange={(value: any) => setConfig(prev => ({ ...prev, paperSize: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="A4">A4</SelectItem>
                      <SelectItem value="A5">A5</SelectItem>
                      <SelectItem value="LETTER">Letter</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Címkék/sor</Label>
                  <Select 
                    value={config.labelsPerRow.toString()} 
                    onValueChange={(value: string) => setConfig(prev => ({ ...prev, labelsPerRow: parseInt(value) }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="2">2</SelectItem>
                      <SelectItem value="3">3</SelectItem>
                      <SelectItem value="4">4</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Címkék/oldal</Label>
                  <Input
                    type="number"
                    min="1"
                    max="20"
                    value={config.labelsPerPage}
                    onChange={(e) => setConfig(prev => ({ ...prev, labelsPerPage: parseInt(e.target.value) || 9 }))}
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-3">
                <Label>Címke tartalma</Label>
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="includeQR"
                      checked={config.includeQR}
                      onCheckedChange={(checked: boolean) => setConfig(prev => ({ ...prev, includeQR: checked }))}
                    />
                    <Label htmlFor="includeQR">QR kód</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="includeBarcode"
                      checked={config.includeBarcode}
                      onCheckedChange={(checked: boolean) => setConfig(prev => ({ ...prev, includeBarcode: checked }))}
                    />
                    <Label htmlFor="includeBarcode">Vonalkód</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="includeInfo"
                      checked={config.includeInfo}
                      onCheckedChange={(checked: boolean) => setConfig(prev => ({ ...prev, includeInfo: checked }))}
                    />
                    <Label htmlFor="includeInfo">Kapu információk</Label>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Műveletek */}
          <div className="flex justify-between">
            <div className="flex gap-2">
              <Button variant="outline" onClick={handlePreview}>
                <Eye className="h-4 w-4 mr-2" />
                Előnézet
              </Button>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" onClick={handleClose}>
                Mégse
              </Button>
              <Button 
                onClick={handleGenerate} 
                disabled={isGenerating || getGateCount() === 0}
                className="min-w-[120px]"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Generálás...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4 mr-2" />
                    PDF letöltés
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}