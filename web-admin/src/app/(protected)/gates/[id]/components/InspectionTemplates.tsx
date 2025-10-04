'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
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
  CheckSquare, 
  Plus, 
  Edit2, 
  Trash2, 
  Copy, 
  Play,
  Save,
  X,
  Check,
  AlertTriangle,
  Clock,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { toast } from '@/components/ui/use-toast'

interface InspectionTemplatesProps {
  gateId: string
}

const mockTemplates = [
  {
    id: '1',
    name: 'Havi biztonsági ellenőrzés',
    description: 'Alapvető biztonsági funkciók havi ellenőrzése',
    frequency: 'monthly',
    estimatedDuration: 30,
    isActive: true,
    lastUsed: '2024-09-25T09:00:00',
    createdBy: 'Szabó Anna',
    checklist: [
      { id: 'c1', item: 'Fotocellák működésének ellenőrzése', required: true, notes: 'Mindkét fotocella tesztelése' },
      { id: 'c2', item: 'Vészleállító gomb működése', required: true, notes: '' },
      { id: 'c3', item: 'Kapu mechanikai állapota', required: true, notes: 'Sínék, kerekek, vezetők' },
      { id: 'c4', item: 'Távvezérlő működése', required: false, notes: '5m távolságról tesztelni' },
      { id: 'c5', item: 'Zajszint ellenőrzése', required: false, notes: 'Szokatlan hangok detektálása' }
    ]
  },
  {
    id: '2',
    name: 'Negyedéves karbantartás',
    description: 'Átfogó karbantartási és kenési munkák',
    frequency: 'quarterly',
    estimatedDuration: 120,
    isActive: true,
    lastUsed: '2024-07-01T14:00:00',
    createdBy: 'Kiss János',
    checklist: [
      { id: 'c6', item: 'Motor és hajtómű kenése', required: true, notes: 'Gyári ajánlott kenőanyag használata' },
      { id: 'c7', item: 'Lánc/szíj feszességének ellenőrzése', required: true, notes: '' },
      { id: 'c8', item: 'Elektromos kapcsolatok ellenőrzése', required: true, notes: 'Csatlakozók, kábelek' },
      { id: 'c9', item: 'Vezérlőegység tesztelése', required: true, notes: 'Paraméterek és funkciók' },
      { id: 'c10', item: 'Biztonsági beállítások kalibrálása', required: true, notes: 'Erő és idő limitsek' }
    ]
  },
  {
    id: '3',
    name: 'Éves főellenőrzés',
    description: 'Teljes körű éves biztonsági és megfelelőségi audit',
    frequency: 'yearly',
    estimatedDuration: 180,
    isActive: true,
    lastUsed: '2024-01-15T10:00:00',
    createdBy: 'Nagy Péter',
    checklist: [
      { id: 'c11', item: 'CE megfelelőségi dokumentáció', required: true, notes: 'Tanúsítványok és nyilatkozatok' },
      { id: 'c12', item: 'Elektronikus biztonsági rendszer tesztelése', required: true, notes: 'Teljes rendszer audit' },
      { id: 'c13', item: 'Mechanikai kopások mérése', required: true, notes: 'Tolómérővel mérni' },
      { id: 'c14', item: 'Teljesítménymérés és beállítás', required: true, notes: 'Nyitási/zárási idők optimalizálása' }
    ]
  }
]

const frequencyLabels = {
  weekly: 'Heti',
  monthly: 'Havi',
  quarterly: 'Negyedéves',
  yearly: 'Éves',
  custom: 'Egyéni'
}

export function InspectionTemplates({ gateId }: InspectionTemplatesProps) {
  const [templates, setTemplates] = useState(mockTemplates)
  const [templatesOpen, setTemplatesOpen] = useState(true)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [addingNew, setAddingNew] = useState(false)
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    description: '',
    frequency: 'monthly',
    estimatedDuration: 30,
    checklist: [] as any[]
  })

  const handleEdit = (id: string) => {
    setEditingId(id)
    setAddingNew(false)
  }

  const handleSave = (id: string, updatedData: any) => {
    setTemplates(prev => prev.map(template => 
      template.id === id ? { ...template, ...updatedData } : template
    ))
    setEditingId(null)
    toast({
      title: "Sablon frissítve",
      description: "Az ellenőrzési sablon sikeresen mentésre került.",
    })
  }

  const handleDelete = (id: string) => {
    setTemplates(prev => prev.filter(template => template.id !== id))
    toast({
      title: "Sablon törölve",
      description: "Az ellenőrzési sablon sikeresen eltávolításra került.",
    })
  }

  const handleCopy = (template: any) => {
    const newId = Date.now().toString()
    const copiedTemplate = {
      ...template,
      id: newId,
      name: `${template.name} (másolat)`,
      lastUsed: null,
      createdBy: 'Aktuális felhasználó'
    }
    setTemplates(prev => [...prev, copiedTemplate])
    toast({
      title: "Sablon másolva",
      description: "Az ellenőrzési sablon sikeresen lemásolásra került.",
    })
  }

  const handleRunInspection = (template: any) => {
    toast({
      title: "Ellenőrzés indítása",
      description: `${template.name} ellenőrzés megkezdése...`,
    })
  }

  const handleToggleActive = (id: string, isActive: boolean) => {
    setTemplates(prev => prev.map(template => 
      template.id === id ? { ...template, isActive } : template
    ))
  }

  return (
    <div className="space-y-6">
      <Collapsible open={templatesOpen} onOpenChange={setTemplatesOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <CheckSquare className="h-5 w-5 mr-2" />
                  Ellenőrzési sablonok ({templates.length})
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
                    Új sablon
                  </Button>
                  {templatesOpen ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </div>
              </div>
              <CardDescription>
                Előre definiált ellenőrzési listák és karbantartási sablonok
              </CardDescription>
            </CardHeader>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent>
              <div className="space-y-6">
                {/* Add new template form */}
                {addingNew && (
                  <Card className="bg-muted/20 border-dashed">
                    <CardContent className="p-6">
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="new-name">Sablon neve *</Label>
                            <Input
                              id="new-name"
                              value={newTemplate.name}
                              onChange={(e) => setNewTemplate(prev => ({ ...prev, name: e.target.value }))}
                              placeholder="pl. Heti biztonsági ellenőrzés"
                            />
                          </div>
                          <div>
                            <Label htmlFor="new-frequency">Gyakoriság *</Label>
                            <Select
                              value={newTemplate.frequency}
                              onValueChange={(value) => setNewTemplate(prev => ({ ...prev, frequency: value }))}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {Object.entries(frequencyLabels).map(([key, label]) => (
                                  <SelectItem key={key} value={key}>{label}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="new-duration">Becsült időtartam (perc)</Label>
                            <Input
                              id="new-duration"
                              type="number"
                              value={newTemplate.estimatedDuration}
                              onChange={(e) => setNewTemplate(prev => ({ ...prev, estimatedDuration: parseInt(e.target.value) || 30 }))}
                              min="5"
                              max="480"
                            />
                          </div>
                        </div>

                        <div>
                          <Label htmlFor="new-description">Leírás</Label>
                          <Textarea
                            id="new-description"
                            value={newTemplate.description}
                            onChange={(e) => setNewTemplate(prev => ({ ...prev, description: e.target.value }))}
                            placeholder="Rövid leírás a sablon céljáról és tartalmáról"
                            rows={3}
                          />
                        </div>

                        <div className="flex justify-end space-x-2">
                          <Button
                            variant="outline"
                            onClick={() => setAddingNew(false)}
                          >
                            <X className="h-4 w-4 mr-2" />
                            Mégse
                          </Button>
                          <Button
                            onClick={() => {
                              const newId = Date.now().toString()
                              const template = {
                                id: newId,
                                ...newTemplate,
                                isActive: true,
                                lastUsed: null,
                                createdBy: 'Aktuális felhasználó',
                                checklist: []
                              }
                              setTemplates(prev => [...prev, template])
                              setNewTemplate({ name: '', description: '', frequency: 'monthly', estimatedDuration: 30, checklist: [] })
                              setAddingNew(false)
                              toast({
                                title: "Új sablon létrehozva",
                                description: "Az ellenőrzési sablon sikeresen hozzáadásra került.",
                              })
                            }}
                            disabled={!newTemplate.name}
                          >
                            <Save className="h-4 w-4 mr-2" />
                            Létrehozás
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Templates list */}
                <div className="space-y-4">
                  {templates.map((template) => (
                    <Card key={template.id} className={template.isActive ? '' : 'opacity-75'}>
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="space-y-1">
                            <div className="flex items-center space-x-3">
                              <CardTitle className="text-lg">{template.name}</CardTitle>
                              <Badge variant={template.isActive ? 'default' : 'secondary'}>
                                {template.isActive ? 'Aktív' : 'Inaktív'}
                              </Badge>
                              <Badge variant="outline">
                                {frequencyLabels[template.frequency as keyof typeof frequencyLabels]}
                              </Badge>
                            </div>
                            <CardDescription>{template.description}</CardDescription>
                            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                              <div className="flex items-center">
                                <Clock className="h-4 w-4 mr-1" />
                                {template.estimatedDuration} perc
                              </div>
                              <div>
                                {template.checklist.length} ellenőrzési pont
                              </div>
                              {template.lastUsed && (
                                <div>
                                  Utoljára használva: {new Date(template.lastUsed).toLocaleDateString('hu-HU')}
                                </div>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={template.isActive}
                              onCheckedChange={(checked) => handleToggleActive(template.id, checked)}
                            />
                            <Button
                              size="sm"
                              onClick={() => handleRunInspection(template)}
                              disabled={!template.isActive}
                            >
                              <Play className="h-4 w-4 mr-2" />
                              Indítás
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleCopy(template)}
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleEdit(template.id)}
                            >
                              <Edit2 className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDelete(template.id)}
                              className="text-destructive hover:text-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardHeader>

                      {template.checklist.length > 0 && (
                        <CardContent>
                          <div className="space-y-2">
                            <h4 className="font-medium">Ellenőrzési pontok:</h4>
                            <div className="space-y-2">
                              {template.checklist.slice(0, 3).map((item) => (
                                <div key={item.id} className="flex items-start space-x-3 text-sm">
                                  <div className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${
                                    item.required ? 'bg-red-500' : 'bg-gray-400'
                                  }`}></div>
                                  <div className="flex-1">
                                    <p className={item.required ? 'font-medium' : ''}>{item.item}</p>
                                    {item.notes && (
                                      <p className="text-muted-foreground text-xs">{item.notes}</p>
                                    )}
                                  </div>
                                </div>
                              ))}
                              {template.checklist.length > 3 && (
                                <p className="text-xs text-muted-foreground pl-5">
                                  ... és még {template.checklist.length - 3} ellenőrzési pont
                                </p>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      )}
                    </Card>
                  ))}

                  {templates.length === 0 && (
                    <Card className="border-dashed">
                      <CardContent className="text-center py-8">
                        <CheckSquare className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                        <p className="text-muted-foreground mb-4">
                          Még nincsenek ellenőrzési sablonok létrehozva
                        </p>
                        <Button onClick={() => setAddingNew(true)}>
                          <Plus className="h-4 w-4 mr-2" />
                          Első sablon létrehozása
                        </Button>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </div>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>
    </div>
  )
}