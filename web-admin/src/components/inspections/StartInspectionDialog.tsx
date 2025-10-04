'use client'

import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Play, 
  FileCheck, 
  Clock, 
  User, 
  Calendar,
  Settings,
  CheckCircle2,
  AlertTriangle,
  Building2,
  Car
} from 'lucide-react'

interface InspectionTemplate {
  id: string
  name: string
  description: string
  category: 'maintenance' | 'safety' | 'compliance' | 'custom'
  estimatedDuration: number // minutes
  checklistCount: number
  lastUsed?: Date
  isRequired: boolean
}

interface StartInspectionDialogProps {
  gateId?: string
  buildingId?: string
  vehicleId?: string
  onStart: (inspection: {
    templateId: string
    inspector: string
    notes?: string
    scheduledDate?: Date
  }) => void
  trigger?: React.ReactNode
}

const mockTemplates: InspectionTemplate[] = [
  {
    id: 'template-1',
    name: 'Napi biztonsági ellenőrzés',
    description: 'Alapvető biztonsági szempontok ellenőrzése minden nap',
    category: 'safety',
    estimatedDuration: 15,
    checklistCount: 12,
    lastUsed: new Date('2024-10-03'),
    isRequired: true
  },
  {
    id: 'template-2', 
    name: 'Heti karbantartási átvizsgálás',
    description: 'Részletes műszaki állapot felmérés',
    category: 'maintenance',
    estimatedDuration: 45,
    checklistCount: 28,
    lastUsed: new Date('2024-09-30'),
    isRequired: false
  },
  {
    id: 'template-3',
    name: 'Megfelelőségi audit',
    description: 'Jogszabályi előírások teljesítésének ellenőrzése',
    category: 'compliance',
    estimatedDuration: 90,
    checklistCount: 35,
    isRequired: true
  },
  {
    id: 'template-4',
    name: 'Egyéni ellenőrzés',
    description: 'Személyre szabott ellenőrzési lista',
    category: 'custom',
    estimatedDuration: 30,
    checklistCount: 15,
    isRequired: false
  }
]

const getCategoryIcon = (category: InspectionTemplate['category']) => {
  switch (category) {
    case 'safety':
      return <AlertTriangle className="w-4 h-4 text-red-500" />
    case 'maintenance':
      return <Settings className="w-4 h-4 text-blue-500" />
    case 'compliance':
      return <CheckCircle2 className="w-4 h-4 text-green-500" />
    case 'custom':
      return <FileCheck className="w-4 h-4 text-purple-500" />
  }
}

const getCategoryColor = (category: InspectionTemplate['category']) => {
  switch (category) {
    case 'safety':
      return 'bg-red-50 text-red-700 border-red-200'
    case 'maintenance':
      return 'bg-blue-50 text-blue-700 border-blue-200'
    case 'compliance':
      return 'bg-green-50 text-green-700 border-green-200'
    case 'custom':
      return 'bg-purple-50 text-purple-700 border-purple-200'
  }
}

export function StartInspectionDialog({
  gateId,
  buildingId,
  vehicleId,
  onStart,
  trigger
}: StartInspectionDialogProps) {
  const [open, setOpen] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [inspector, setInspector] = useState('')
  const [notes, setNotes] = useState('')
  const [scheduledDate, setScheduledDate] = useState(new Date().toISOString().split('T')[0])
  const [isScheduled, setIsScheduled] = useState(false)
  const [templates, setTemplates] = useState<InspectionTemplate[]>([])
  const [loading, setLoading] = useState(false)

  // Load templates when dialog opens
  useEffect(() => {
    if (open) {
      setLoading(true)
      // Simulate API call
      setTimeout(() => {
        setTemplates(mockTemplates)
        setLoading(false)
      }, 500)
      
      // Set default inspector from session/auth
      setInspector('Kovács János') // Mock current user
    }
  }, [open])

  const handleStart = () => {
    if (!selectedTemplate || !inspector) return

    const inspection = {
      templateId: selectedTemplate,
      inspector,
      notes: notes.trim() || undefined,
      scheduledDate: isScheduled ? new Date(scheduledDate) : undefined
    }

    onStart(inspection)
    setOpen(false)
    
    // Reset form
    setSelectedTemplate('')
    setNotes('')
    setIsScheduled(false)
    setScheduledDate(new Date().toISOString().split('T')[0])
  }

  const selectedTemplateData = templates.find(t => t.id === selectedTemplate)
  const requiredTemplates = templates.filter(t => t.isRequired)
  const optionalTemplates = templates.filter(t => !t.isRequired)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button size="lg" className="gap-2">
            <Play className="w-5 h-5" />
            Ellenőrzés indítása
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <FileCheck className="w-6 h-6" />
            Új ellenőrzés indítása
          </DialogTitle>
        </DialogHeader>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Template Selection */}
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-lg mb-2">Ellenőrzési sablon</h3>
              <p className="text-sm text-gray-600 mb-4">
                Válassza ki a megfelelő ellenőrzési sablont az objektum típusa és célja szerint.
              </p>
            </div>

            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-24 bg-gray-100 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {/* Required Templates */}
                {requiredTemplates.length > 0 && (
                  <div>
                    <h4 className="font-medium text-sm text-gray-700 mb-2">Kötelező ellenőrzések</h4>
                    <div className="space-y-2">
                      {requiredTemplates.map((template) => (
                        <Card 
                          key={template.id}
                          className={`cursor-pointer transition-all hover:shadow-md ${
                            selectedTemplate === template.id 
                              ? 'ring-2 ring-blue-500 border-blue-200' 
                              : 'hover:border-gray-300'
                          }`}
                          onClick={() => setSelectedTemplate(template.id)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center gap-2">
                                {getCategoryIcon(template.category)}
                                <h4 className="font-medium">{template.name}</h4>
                                <Badge variant="destructive" className="text-xs">
                                  Kötelező
                                </Badge>
                              </div>
                              {selectedTemplate === template.id && (
                                <CheckCircle2 className="w-5 h-5 text-blue-500" />
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                            <div className="flex items-center gap-4 text-xs text-gray-500">
                              <div className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {template.estimatedDuration} perc
                              </div>
                              <div className="flex items-center gap-1">
                                <FileCheck className="w-3 h-3" />
                                {template.checklistCount} pont
                              </div>
                              {template.lastUsed && (
                                <div className="flex items-center gap-1">
                                  <Calendar className="w-3 h-3" />
                                  {template.lastUsed.toLocaleDateString('hu-HU')}
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {/* Optional Templates */}
                {optionalTemplates.length > 0 && (
                  <div>
                    <h4 className="font-medium text-sm text-gray-700 mb-2">Választható ellenőrzések</h4>
                    <div className="space-y-2">
                      {optionalTemplates.map((template) => (
                        <Card 
                          key={template.id}
                          className={`cursor-pointer transition-all hover:shadow-md ${
                            selectedTemplate === template.id 
                              ? 'ring-2 ring-blue-500 border-blue-200' 
                              : 'hover:border-gray-300'
                          }`}
                          onClick={() => setSelectedTemplate(template.id)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center gap-2">
                                {getCategoryIcon(template.category)}
                                <h4 className="font-medium">{template.name}</h4>
                              </div>
                              {selectedTemplate === template.id && (
                                <CheckCircle2 className="w-5 h-5 text-blue-500" />
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                            <div className="flex items-center gap-4 text-xs text-gray-500">
                              <div className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {template.estimatedDuration} perc
                              </div>
                              <div className="flex items-center gap-1">
                                <FileCheck className="w-3 h-3" />
                                {template.checklistCount} pont
                              </div>
                              {template.lastUsed && (
                                <div className="flex items-center gap-1">
                                  <Calendar className="w-3 h-3" />
                                  {template.lastUsed.toLocaleDateString('hu-HU')}
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Inspection Details */}
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-lg mb-2">Ellenőrzés részletei</h3>
            </div>

            {/* Context Information */}
            <Card className="bg-gray-50">
              <CardContent className="p-4">
                <h4 className="font-medium mb-2">Ellenőrzés tárgya</h4>
                <div className="space-y-2 text-sm">
                  {gateId && (
                    <div className="flex items-center gap-2">
                      <Car className="w-4 h-4 text-blue-500" />
                      <span>Garázs kapu: #{gateId}</span>
                    </div>
                  )}
                  {buildingId && (
                    <div className="flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-green-500" />
                      <span>Épület: #{buildingId}</span>
                    </div>
                  )}
                  {vehicleId && (
                    <div className="flex items-center gap-2">
                      <Car className="w-4 h-4 text-purple-500" />
                      <span>Jármű: #{vehicleId}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Inspector */}
            <div className="space-y-2">
              <Label htmlFor="inspector" className="flex items-center gap-2">
                <User className="w-4 h-4" />
                Ellenőr
              </Label>
              <Input
                id="inspector"
                value={inspector}
                onChange={(e) => setInspector(e.target.value)}
                placeholder="Ellenőr neve"
                required
              />
            </div>

            {/* Scheduling */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="scheduled"
                  checked={isScheduled}
                  onChange={(e) => setIsScheduled(e.target.checked)}
                  className="rounded"
                />
                <Label htmlFor="scheduled">Ütemezett ellenőrzés</Label>
              </div>
              
              {isScheduled && (
                <div className="space-y-2">
                  <Label htmlFor="scheduledDate">Tervezett dátum</Label>
                  <Input
                    id="scheduledDate"
                    type="date"
                    value={scheduledDate}
                    onChange={(e) => setScheduledDate(e.target.value)}
                  />
                </div>
              )}
            </div>

            {/* Notes */}
            <div className="space-y-2">
              <Label htmlFor="notes">Megjegyzések</Label>
              <Textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Opcionális megjegyzések az ellenőrzéshez..."
                rows={3}
              />
            </div>

            {/* Selected Template Summary */}
            {selectedTemplateData && (
              <Card className={`border-2 ${getCategoryColor(selectedTemplateData.category)}`}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">
                    {getCategoryIcon(selectedTemplateData.category)}
                    Kiválasztott sablon
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <h4 className="font-medium mb-1">{selectedTemplateData.name}</h4>
                  <p className="text-sm text-gray-600 mb-3">{selectedTemplateData.description}</p>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-500">Becsült idő:</span>
                      <span className="ml-1 font-medium">{selectedTemplateData.estimatedDuration} perc</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Ellenőrzési pontok:</span>
                      <span className="ml-1 font-medium">{selectedTemplateData.checklistCount} db</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <Button
                onClick={handleStart}
                disabled={!selectedTemplate || !inspector}
                className="flex-1 gap-2"
              >
                <Play className="w-4 h-4" />
                Ellenőrzés indítása
              </Button>
              <Button
                variant="outline"
                onClick={() => setOpen(false)}
              >
                Mégse
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}