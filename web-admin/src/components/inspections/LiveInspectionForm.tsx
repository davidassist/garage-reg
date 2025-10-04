'use client'

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Save,
  FileText,
  Camera,
  MessageSquare,
  ArrowLeft,
  ArrowRight,
  Flag,
  User,
  Calendar,
  CheckSquare,
  Square,
  AlertCircle,
  Play,
  Pause,
  StopCircle
} from 'lucide-react'
import { EnhancedPhotoUploader } from '@/components/photo-upload/EnhancedPhotoUploader'

interface ChecklistItem {
  id: string
  title: string
  description?: string
  category: 'safety' | 'maintenance' | 'compliance' | 'documentation'
  required: boolean
  type: 'boolean' | 'text' | 'number' | 'photo' | 'select'
  options?: string[]
  value?: any
  status?: 'pending' | 'completed' | 'failed' | 'skipped'
  notes?: string
  photos?: string[]
  timestamp?: Date
}

interface InspectionSession {
  id: string
  templateId: string
  templateName: string
  objectType: 'gate' | 'building' | 'vehicle'
  objectId: string
  inspector: string
  startedAt: Date
  status: 'active' | 'paused' | 'completed' | 'cancelled'
  progress: number
  checklist: ChecklistItem[]
  notes: string
  estimatedDuration: number
  actualDuration?: number
}

interface LiveInspectionFormProps {
  sessionId: string
  onComplete: (session: InspectionSession) => void
  onCancel: () => void
  onSave?: (session: InspectionSession) => void
}

// Mock inspection data
const mockSession: InspectionSession = {
  id: 'inspection-001',
  templateId: 'template-1',
  templateName: 'Napi biztonsági ellenőrzés',
  objectType: 'gate',
  objectId: 'gate-123',
  inspector: 'Kovács János',
  startedAt: new Date(),
  status: 'active',
  progress: 0,
  notes: '',
  estimatedDuration: 15,
  checklist: [
    {
      id: 'check-1',
      title: 'Kapu működésének ellenőrzése',
      description: 'Nyitás/zárás funkciók tesztelése',
      category: 'safety',
      required: true,
      type: 'boolean',
      status: 'pending'
    },
    {
      id: 'check-2',
      title: 'Biztonsági szenzorok tesztelése',
      description: 'Mozgásérzékelők és akadálydetektorok működése',
      category: 'safety',
      required: true,
      type: 'select',
      options: ['Megfelelő', 'Kis eltérés', 'Hibás', 'Nem működik'],
      status: 'pending'
    },
    {
      id: 'check-3',
      title: 'Távvezérlő funkciók',
      description: 'Távirányító és mobilalkalmazás kapcsolat',
      category: 'maintenance',
      required: false,
      type: 'boolean',
      status: 'pending'
    },
    {
      id: 'check-4',
      title: 'Kenőanyag szint',
      description: 'Mechanikus alkatrészek kenése',
      category: 'maintenance',
      required: true,
      type: 'select',
      options: ['Megfelelő', 'Alacsony', 'Kritikusan alacsony'],
      status: 'pending'
    },
    {
      id: 'check-5',
      title: 'Dokumentáció fotók',
      description: 'Állapot dokumentálása képekkel',
      category: 'documentation',
      required: false,
      type: 'photo',
      status: 'pending'
    },
    {
      id: 'check-6',
      title: 'Megjegyzések',
      description: 'További észrevételek és javaslatok',
      category: 'documentation',
      required: false,
      type: 'text',
      status: 'pending'
    }
  ]
}

export function LiveInspectionForm({ 
  sessionId, 
  onComplete, 
  onCancel, 
  onSave 
}: LiveInspectionFormProps) {
  const [session, setSession] = useState<InspectionSession>(mockSession)
  const [currentItemIndex, setCurrentItemIndex] = useState(0)
  const [isAutoSaving, setIsAutoSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [showExitDialog, setShowExitDialog] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [elapsedTime, setElapsedTime] = useState(0)

  const autoSaveTimeoutRef = useRef<NodeJS.Timeout>()
  const timerRef = useRef<NodeJS.Timeout>()

  // Auto-save function
  const autoSave = useCallback(async () => {
    if (!hasUnsavedChanges) return

    setIsAutoSaving(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      onSave?.(session)
      setLastSaved(new Date())
      setHasUnsavedChanges(false)
      
      // Store in localStorage for offline support
      localStorage.setItem(`inspection-${sessionId}`, JSON.stringify(session))
    } catch (error) {
      console.error('Auto-save failed:', error)
    } finally {
      setIsAutoSaving(false)
    }
  }, [session, hasUnsavedChanges, onSave, sessionId])

  // Debounced auto-save
  useEffect(() => {
    if (hasUnsavedChanges) {
      clearTimeout(autoSaveTimeoutRef.current)
      autoSaveTimeoutRef.current = setTimeout(() => {
        autoSave()
      }, 2000) // Auto-save after 2 seconds of inactivity
    }

    return () => clearTimeout(autoSaveTimeoutRef.current)
  }, [hasUnsavedChanges, autoSave])

  // Timer for elapsed time
  useEffect(() => {
    if (!isPaused && session.status === 'active') {
      timerRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1)
      }, 1000)
    } else {
      clearInterval(timerRef.current)
    }

    return () => clearInterval(timerRef.current)
  }, [isPaused, session.status])

  // Load saved session on mount
  useEffect(() => {
    const savedSession = localStorage.getItem(`inspection-${sessionId}`)
    if (savedSession) {
      try {
        const parsed = JSON.parse(savedSession)
        setSession(parsed)
      } catch (error) {
        console.error('Failed to load saved session:', error)
      }
    }
  }, [sessionId])

  // Calculate progress
  const completedItems = session.checklist.filter(item => 
    item.status === 'completed' || item.status === 'skipped'
  ).length
  const progress = (completedItems / session.checklist.length) * 100

  const updateChecklistItem = (itemId: string, updates: Partial<ChecklistItem>) => {
    setSession(prev => ({
      ...prev,
      checklist: prev.checklist.map(item =>
        item.id === itemId 
          ? { ...item, ...updates, timestamp: new Date() }
          : item
      )
    }))
    setHasUnsavedChanges(true)
  }

  const updateSessionNotes = (notes: string) => {
    setSession(prev => ({ ...prev, notes }))
    setHasUnsavedChanges(true)
  }

  const handleItemValueChange = (itemId: string, value: any) => {
    const item = session.checklist.find(i => i.id === itemId)
    if (!item) return

    let status: ChecklistItem['status'] = 'completed'
    
    // Determine status based on value and type
    if (item.type === 'boolean' && value === false) {
      status = 'failed'
    } else if (item.type === 'select' && value === 'Nem működik') {
      status = 'failed'
    } else if (!value || value === '') {
      status = 'skipped'
    }

    updateChecklistItem(itemId, { value, status })
  }

  const handleItemNotes = (itemId: string, notes: string) => {
    updateChecklistItem(itemId, { notes })
  }

  const handlePhotoUpload = (itemId: string, photos: string[]) => {
    updateChecklistItem(itemId, { 
      photos, 
      status: photos.length > 0 ? 'completed' : 'pending' 
    })
  }

  const nextItem = () => {
    if (currentItemIndex < session.checklist.length - 1) {
      setCurrentItemIndex(currentItemIndex + 1)
    }
  }

  const prevItem = () => {
    if (currentItemIndex > 0) {
      setCurrentItemIndex(currentItemIndex - 1)
    }
  }

  const togglePause = () => {
    setIsPaused(!isPaused)
    setSession(prev => ({
      ...prev,
      status: isPaused ? 'active' : 'paused'
    }))
  }

  const handleComplete = () => {
    const finalSession = {
      ...session,
      status: 'completed' as const,
      progress: 100,
      actualDuration: elapsedTime / 60 // Convert to minutes
    }
    
    // Save final state
    localStorage.setItem(`inspection-${sessionId}`, JSON.stringify(finalSession))
    onComplete(finalSession)
  }

  const handleExit = () => {
    if (hasUnsavedChanges) {
      setShowExitDialog(true)
    } else {
      onCancel()
    }
  }

  const handleForceExit = () => {
    localStorage.removeItem(`inspection-${sessionId}`)
    onCancel()
  }

  const handleSaveAndExit = async () => {
    await autoSave()
    onCancel()
  }

  const currentItem = session.checklist[currentItemIndex]
  const isLastItem = currentItemIndex === session.checklist.length - 1
  const isFirstItem = currentItemIndex === 0

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'safety':
        return 'bg-red-50 text-red-700 border-red-200'
      case 'maintenance':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      case 'compliance':
        return 'bg-green-50 text-green-700 border-green-200'
      case 'documentation':
        return 'bg-purple-50 text-purple-700 border-purple-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  const getStatusIcon = (status?: ChecklistItem['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'skipped':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      default:
        return <Square className="w-5 h-5 text-gray-400" />
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-6 h-6" />
                {session.templateName}
              </CardTitle>
              <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <User className="w-4 h-4" />
                  {session.inspector}
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {session.startedAt.toLocaleDateString('hu-HU')}
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {formatTime(elapsedTime)} / {session.estimatedDuration} perc
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {/* Auto-save indicator */}
              {isAutoSaving && (
                <div className="flex items-center gap-2 text-sm text-blue-600">
                  <Save className="w-4 h-4 animate-spin" />
                  Mentés...
                </div>
              )}
              {lastSaved && !hasUnsavedChanges && (
                <div className="flex items-center gap-2 text-sm text-green-600">
                  <CheckCircle2 className="w-4 h-4" />
                  Mentve: {lastSaved.toLocaleTimeString('hu-HU')}
                </div>
              )}
              {hasUnsavedChanges && (
                <div className="flex items-center gap-2 text-sm text-orange-600">
                  <AlertCircle className="w-4 h-4" />
                  Nem mentett módosítások
                </div>
              )}
              
              {/* Control buttons */}
              <Button
                variant="outline"
                size="sm"
                onClick={togglePause}
                className="gap-1"
              >
                {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                {isPaused ? 'Folytatás' : 'Szünet'}
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleExit}
                className="gap-1"
              >
                <ArrowLeft className="w-4 h-4" />
                Kilépés
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          {/* Progress */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Haladás ({completedItems}/{session.checklist.length})</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Current Item */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    {getStatusIcon(currentItem.status)}
                    {currentItem.title}
                    {currentItem.required && (
                      <Badge variant="destructive" className="text-xs">Kötelező</Badge>
                    )}
                  </CardTitle>
                  <Badge className={`mt-2 ${getCategoryColor(currentItem.category)}`}>
                    {currentItem.category}
                  </Badge>
                </div>
                
                <div className="text-sm text-gray-500">
                  {currentItemIndex + 1} / {session.checklist.length}
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {currentItem.description && (
                <p className="text-gray-600">{currentItem.description}</p>
              )}
              
              {/* Input based on type */}
              {currentItem.type === 'boolean' && (
                <div className="space-y-2">
                  <Label>Állapot</Label>
                  <div className="flex gap-3">
                    <Button
                      variant={currentItem.value === true ? "default" : "outline"}
                      onClick={() => handleItemValueChange(currentItem.id, true)}
                      className="flex-1 gap-2"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      Megfelelő
                    </Button>
                    <Button
                      variant={currentItem.value === false ? "destructive" : "outline"}
                      onClick={() => handleItemValueChange(currentItem.id, false)}
                      className="flex-1 gap-2"
                    >
                      <XCircle className="w-4 h-4" />
                      Hibás
                    </Button>
                  </div>
                </div>
              )}
              
              {currentItem.type === 'select' && currentItem.options && (
                <div className="space-y-2">
                  <Label>Válasszon egy opciót</Label>
                  <div className="grid grid-cols-2 gap-2">
                    {currentItem.options.map((option) => (
                      <Button
                        key={option}
                        variant={currentItem.value === option ? "default" : "outline"}
                        onClick={() => handleItemValueChange(currentItem.id, option)}
                        className="justify-start"
                      >
                        {option}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
              
              {currentItem.type === 'text' && (
                <div className="space-y-2">
                  <Label>Megjegyzések</Label>
                  <Textarea
                    value={currentItem.value || ''}
                    onChange={(e) => handleItemValueChange(currentItem.id, e.target.value)}
                    placeholder="Írja be a megjegyzéseit..."
                    rows={4}
                  />
                </div>
              )}
              
              {currentItem.type === 'number' && (
                <div className="space-y-2">
                  <Label>Érték</Label>
                  <Input
                    type="number"
                    value={currentItem.value || ''}
                    onChange={(e) => handleItemValueChange(currentItem.id, parseFloat(e.target.value))}
                    placeholder="Adjon meg egy számot..."
                  />
                </div>
              )}
              
              {currentItem.type === 'photo' && (
                <div className="space-y-2">
                  <Label>Fotók feltöltése</Label>
                  <EnhancedPhotoUploader
                    maxFiles={5}
                    maxFileSize={10 * 1024 * 1024}
                    onUploadComplete={(photos) => {
                      const photoUrls = photos.map(p => p.urls.original)
                      handlePhotoUpload(currentItem.id, photoUrls)
                    }}
                    className="border-2 border-dashed border-gray-300 rounded-lg p-4"
                  />
                </div>
              )}
              
              {/* Notes for item */}
              <div className="space-y-2">
                <Label>További megjegyzések</Label>
                <Textarea
                  value={currentItem.notes || ''}
                  onChange={(e) => handleItemNotes(currentItem.id, e.target.value)}
                  placeholder="Opcionális megjegyzések ehhez a ponthoz..."
                  rows={2}
                />
              </div>
            </CardContent>
          </Card>

          {/* Navigation */}
          <div className="flex justify-between items-center">
            <Button
              variant="outline"
              onClick={prevItem}
              disabled={isFirstItem}
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Előző
            </Button>
            
            <div className="flex gap-2">
              {!isLastItem ? (
                <Button onClick={nextItem} className="gap-2">
                  Következő
                  <ArrowRight className="w-4 h-4" />
                </Button>
              ) : (
                <Button 
                  onClick={handleComplete}
                  className="gap-2 bg-green-600 hover:bg-green-700"
                >
                  <Flag className="w-4 h-4" />
                  Ellenőrzés befejezése
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Checklist Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Ellenőrzési lista</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {session.checklist.map((item, index) => (
                  <div
                    key={item.id}
                    className={`flex items-center gap-2 p-2 rounded cursor-pointer transition-colors ${
                      index === currentItemIndex 
                        ? 'bg-blue-100 border border-blue-300' 
                        : 'hover:bg-gray-50'
                    }`}
                    onClick={() => setCurrentItemIndex(index)}
                  >
                    {getStatusIcon(item.status)}
                    <span className="flex-1 text-sm truncate">{item.title}</span>
                    {item.required && (
                      <AlertCircle className="w-3 h-3 text-red-500" />
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Session Notes */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Általános megjegyzések
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={session.notes}
                onChange={(e) => updateSessionNotes(e.target.value)}
                placeholder="Általános megjegyzések az ellenőrzéshez..."
                rows={6}
              />
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Exit Confirmation Dialog */}
      <Dialog open={showExitDialog} onOpenChange={setShowExitDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nem mentett módosítások</DialogTitle>
            <DialogDescription>
              Vannak nem mentett módosítások az ellenőrzésben. Mit szeretne tenni?
            </DialogDescription>
          </DialogHeader>
          
          <div className="flex gap-3 justify-end">
            <Button variant="outline" onClick={() => setShowExitDialog(false)}>
              Mégse
            </Button>
            <Button variant="destructive" onClick={handleForceExit}>
              Kilépés mentés nélkül
            </Button>
            <Button onClick={handleSaveAndExit}>
              Mentés és kilépés
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}