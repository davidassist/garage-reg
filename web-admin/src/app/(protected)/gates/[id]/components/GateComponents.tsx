'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { 
  Plus, 
  Edit2, 
  Trash2, 
  Check, 
  X, 
  Settings, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Save,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { toast } from '@/components/ui/use-toast'

interface GateComponentsProps {
  gateId: string
}

const mockComponents = [
  {
    id: '1',
    name: 'Meghajtó motor',
    type: 'motor',
    manufacturer: 'CAME',
    model: 'BZ-25',
    serialNumber: 'MOTOR001',
    status: 'active',
    installDate: '2024-01-15',
    warrantyEnd: '2026-01-15',
    lastMaintenance: '2024-09-01',
    nextMaintenance: '2024-12-01',
    description: 'Főmotor a kapu meghajtásához'
  },
  {
    id: '2',
    name: 'Vezérlőegység',
    type: 'controller',
    manufacturer: 'CAME',
    model: 'ZBX-74',
    serialNumber: 'CTRL001',
    status: 'active',
    installDate: '2024-01-15',
    warrantyEnd: '2026-01-15',
    lastMaintenance: '2024-08-15',
    nextMaintenance: '2024-11-15',
    description: 'Központi vezérlőegység'
  },
  {
    id: '3',
    name: 'Biztonsági fotocella',
    type: 'safety',
    manufacturer: 'CAME',
    model: 'DIR10',
    serialNumber: 'SAFE001',
    status: 'warning',
    installDate: '2024-01-15',
    warrantyEnd: '2026-01-15',
    lastMaintenance: '2024-07-01',
    nextMaintenance: '2024-10-01',
    description: 'Biztonsági érzékelő a kapu útjában'
  }
]

const componentTypes = {
  motor: 'Motor',
  controller: 'Vezérlő',
  safety: 'Biztonsági',
  sensor: 'Érzékelő',
  remote: 'Távirányító',
  power: 'Tápegység',
  other: 'Egyéb'
}

const statusConfig = {
  active: { label: 'Aktív', color: 'bg-green-500', icon: CheckCircle },
  warning: { label: 'Figyelmeztetés', color: 'bg-yellow-500', icon: AlertTriangle },
  error: { label: 'Hiba', color: 'bg-red-500', icon: AlertTriangle },
  maintenance: { label: 'Karbantartás', color: 'bg-blue-500', icon: Clock }
}

export function GateComponents({ gateId }: GateComponentsProps) {
  const [components, setComponents] = useState(mockComponents)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [addingNew, setAddingNew] = useState(false)
  const [componentsOpen, setComponentsOpen] = useState(true)
  const [newComponent, setNewComponent] = useState({
    name: '',
    type: '',
    manufacturer: '',
    model: '',
    serialNumber: '',
    description: ''
  })

  const handleEdit = (id: string) => {
    setEditingId(id)
    setAddingNew(false)
  }

  const handleSave = (id: string, updatedData: any) => {
    setComponents(prev => prev.map(comp => 
      comp.id === id ? { ...comp, ...updatedData } : comp
    ))
    setEditingId(null)
    toast({
      title: "Komponens frissítve",
      description: "A komponens adatai sikeresen mentésre kerültek.",
    })
  }

  const handleDelete = (id: string) => {
    setComponents(prev => prev.filter(comp => comp.id !== id))
    toast({
      title: "Komponens törölve",
      description: "A komponens sikeresen eltávolításra került.",
    })
  }

  const handleAddNew = () => {
    const newId = Date.now().toString()
    const component = {
      id: newId,
      ...newComponent,
      status: 'active' as const,
      installDate: new Date().toISOString().split('T')[0],
      warrantyEnd: new Date(Date.now() + 2 * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      lastMaintenance: new Date().toISOString().split('T')[0],
      nextMaintenance: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    }
    
    setComponents(prev => [...prev, component])
    setNewComponent({ name: '', type: '', manufacturer: '', model: '', serialNumber: '', description: '' })
    setAddingNew(false)
    toast({
      title: "Új komponens hozzáadva",
      description: "A komponens sikeresen hozzáadásra került.",
    })
  }

  return (
    <div className="space-y-6">
      <Collapsible open={componentsOpen} onOpenChange={setComponentsOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <Settings className="h-5 w-5 mr-2" />
                  Kapu komponensek ({components.length})
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <Button
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      setAddingNew(true)
                      setEditingId(null)
                    }}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Új komponens
                  </Button>
                  {componentsOpen ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </div>
              </div>
              <CardDescription>
                A kapuhoz tartozó összes komponens kezelése és karbantartása
              </CardDescription>
            </CardHeader>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent>
              <div className="space-y-4">
                {/* Add new component form */}
                {addingNew && (
                  <Card className="bg-muted/20 border-dashed">
                    <CardContent className="p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div>
                          <Label htmlFor="new-name">Komponens neve *</Label>
                          <Input
                            id="new-name"
                            value={newComponent.name}
                            onChange={(e) => setNewComponent(prev => ({ ...prev, name: e.target.value }))}
                            placeholder="pl. Meghajtó motor"
                          />
                        </div>
                        <div>
                          <Label htmlFor="new-type">Típus *</Label>
                          <Select
                            value={newComponent.type}
                            onValueChange={(value) => setNewComponent(prev => ({ ...prev, type: value }))}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Válassz típust" />
                            </SelectTrigger>
                            <SelectContent>
                              {Object.entries(componentTypes).map(([key, label]) => (
                                <SelectItem key={key} value={key}>{label}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="new-manufacturer">Gyártó</Label>
                          <Input
                            id="new-manufacturer"
                            value={newComponent.manufacturer}
                            onChange={(e) => setNewComponent(prev => ({ ...prev, manufacturer: e.target.value }))}
                            placeholder="pl. CAME"
                          />
                        </div>
                        <div>
                          <Label htmlFor="new-model">Modell</Label>
                          <Input
                            id="new-model"
                            value={newComponent.model}
                            onChange={(e) => setNewComponent(prev => ({ ...prev, model: e.target.value }))}
                            placeholder="pl. BZ-25"
                          />
                        </div>
                        <div>
                          <Label htmlFor="new-serial">Sorozatszám</Label>
                          <Input
                            id="new-serial"
                            value={newComponent.serialNumber}
                            onChange={(e) => setNewComponent(prev => ({ ...prev, serialNumber: e.target.value }))}
                            placeholder="pl. MOTOR001"
                          />
                        </div>
                        <div className="md:col-span-2 lg:col-span-1">
                          <Label htmlFor="new-description">Leírás</Label>
                          <Input
                            id="new-description"
                            value={newComponent.description}
                            onChange={(e) => setNewComponent(prev => ({ ...prev, description: e.target.value }))}
                            placeholder="Rövid leírás"
                          />
                        </div>
                      </div>
                      <div className="flex justify-end space-x-2 mt-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setAddingNew(false)}
                        >
                          <X className="h-4 w-4 mr-2" />
                          Mégse
                        </Button>
                        <Button
                          size="sm"
                          onClick={handleAddNew}
                          disabled={!newComponent.name || !newComponent.type}
                        >
                          <Save className="h-4 w-4 mr-2" />
                          Mentés
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Components table */}
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Komponens</TableHead>
                        <TableHead>Típus</TableHead>
                        <TableHead>Gyártó/Modell</TableHead>
                        <TableHead>Állapot</TableHead>
                        <TableHead>Következő karbantartás</TableHead>
                        <TableHead className="text-right">Műveletek</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {components.map((component) => (
                        <ComponentRow
                          key={component.id}
                          component={component}
                          isEditing={editingId === component.id}
                          onEdit={() => handleEdit(component.id)}
                          onSave={(data) => handleSave(component.id, data)}
                          onCancel={() => setEditingId(null)}
                          onDelete={() => handleDelete(component.id)}
                        />
                      ))}
                      {components.length === 0 && (
                        <TableRow>
                          <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                            Még nincsenek komponensek hozzáadva
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>
              </div>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>
    </div>
  )
}

function ComponentRow({ 
  component, 
  isEditing, 
  onEdit, 
  onSave, 
  onCancel, 
  onDelete 
}: {
  component: any
  isEditing: boolean
  onEdit: () => void
  onSave: (data: any) => void
  onCancel: () => void
  onDelete: () => void
}) {
  const [editData, setEditData] = useState(component)
  const statusInfo = statusConfig[component.status as keyof typeof statusConfig]
  const StatusIcon = statusInfo.icon

  if (isEditing) {
    return (
      <TableRow className="bg-muted/20">
        <TableCell>
          <Input
            value={editData.name}
            onChange={(e) => setEditData(prev => ({ ...prev, name: e.target.value }))}
            className="h-8"
          />
        </TableCell>
        <TableCell>
          <Select
            value={editData.type}
            onValueChange={(value) => setEditData(prev => ({ ...prev, type: value }))}
          >
            <SelectTrigger className="h-8">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(componentTypes).map(([key, label]) => (
                <SelectItem key={key} value={key}>{label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </TableCell>
        <TableCell>
          <div className="space-y-1">
            <Input
              value={editData.manufacturer}
              onChange={(e) => setEditData(prev => ({ ...prev, manufacturer: e.target.value }))}
              placeholder="Gyártó"
              className="h-8"
            />
            <Input
              value={editData.model}
              onChange={(e) => setEditData(prev => ({ ...prev, model: e.target.value }))}
              placeholder="Modell"
              className="h-8"
            />
          </div>
        </TableCell>
        <TableCell>
          <Select
            value={editData.status}
            onValueChange={(value) => setEditData(prev => ({ ...prev, status: value }))}
          >
            <SelectTrigger className="h-8">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(statusConfig).map(([key, config]) => (
                <SelectItem key={key} value={key}>{config.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </TableCell>
        <TableCell>
          <Input
            type="date"
            value={editData.nextMaintenance}
            onChange={(e) => setEditData(prev => ({ ...prev, nextMaintenance: e.target.value }))}
            className="h-8"
          />
        </TableCell>
        <TableCell className="text-right">
          <div className="flex justify-end space-x-1">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => onSave(editData)}
            >
              <Check className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={onCancel}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </TableCell>
      </TableRow>
    )
  }

  return (
    <TableRow>
      <TableCell>
        <div>
          <p className="font-medium">{component.name}</p>
          <p className="text-sm text-muted-foreground">{component.description}</p>
          <p className="text-xs text-muted-foreground font-mono">{component.serialNumber}</p>
        </div>
      </TableCell>
      <TableCell>
        <Badge variant="outline">
          {componentTypes[component.type as keyof typeof componentTypes]}
        </Badge>
      </TableCell>
      <TableCell>
        <div>
          <p className="font-medium">{component.manufacturer}</p>
          <p className="text-sm text-muted-foreground">{component.model}</p>
        </div>
      </TableCell>
      <TableCell>
        <div className="flex items-center space-x-2">
          <StatusIcon className="h-4 w-4 text-muted-foreground" />
          <Badge variant="secondary" className={`${statusInfo.color} text-white`}>
            {statusInfo.label}
          </Badge>
        </div>
      </TableCell>
      <TableCell>
        <div>
          <p className="text-sm">
            {new Date(component.nextMaintenance).toLocaleDateString('hu-HU')}
          </p>
          <p className="text-xs text-muted-foreground">
            ({Math.ceil((new Date(component.nextMaintenance).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} nap)
          </p>
        </div>
      </TableCell>
      <TableCell className="text-right">
        <div className="flex justify-end space-x-1">
          <Button
            size="sm"
            variant="ghost"
            onClick={onEdit}
          >
            <Edit2 className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={onDelete}
            className="text-destructive hover:text-destructive"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </TableCell>
    </TableRow>
  )
}