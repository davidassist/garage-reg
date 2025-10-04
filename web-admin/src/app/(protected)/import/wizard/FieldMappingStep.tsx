'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
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
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  AlertTriangle, 
  CheckCircle, 
  ArrowRight, 
  RotateCcw,
  Eye,
  EyeOff
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { ImportType, FieldMapping } from './types'

interface FieldMappingStepProps {
  importType: ImportType
  uploadedData: any[]
  onNext: (mappings: FieldMapping[]) => void
  onBack: () => void
}

const fieldDefinitions = {
  gates: {
    name: { required: true, type: 'string' as const, label: 'Kapu neve' },
    type: { 
      required: true, 
      type: 'enum' as const, 
      label: 'Kapu típusa',
      enumValues: ['entrance', 'exit', 'service', 'emergency']
    },
    siteId: { required: true, type: 'string' as const, label: 'Telephely ID' },
    manufacturer: { required: false, type: 'string' as const, label: 'Gyártó' },
    model: { required: false, type: 'string' as const, label: 'Modell' },
    serialNumber: { required: false, type: 'string' as const, label: 'Sorozatszám' },
    width: { required: false, type: 'number' as const, label: 'Szélesség (m)' },
    height: { required: false, type: 'number' as const, label: 'Magasság (m)' },
    weight: { required: false, type: 'number' as const, label: 'Súly (kg)' },
    motorType: { 
      required: false, 
      type: 'enum' as const, 
      label: 'Motor típus',
      enumValues: ['hydraulic', 'electric', 'pneumatic']
    },
    motorPower: { required: false, type: 'number' as const, label: 'Motor teljesítmény (kW)' },
    status: { 
      required: false, 
      type: 'enum' as const, 
      label: 'Állapot',
      enumValues: ['active', 'inactive', 'maintenance', 'error']
    }
  },
  sites: {
    name: { required: true, type: 'string' as const, label: 'Telephely neve' },
    address: { required: true, type: 'string' as const, label: 'Cím' },
    city: { required: true, type: 'string' as const, label: 'Város' },
    postalCode: { required: true, type: 'string' as const, label: 'Irányítószám' },
    country: { required: false, type: 'string' as const, label: 'Ország' },
    contactName: { required: false, type: 'string' as const, label: 'Kapcsolattartó neve' },
    contactEmail: { required: false, type: 'email' as const, label: 'Kapcsolattartó email' },
    contactPhone: { required: false, type: 'phone' as const, label: 'Kapcsolattartó telefon' },
    status: { 
      required: false, 
      type: 'enum' as const, 
      label: 'Állapot',
      enumValues: ['active', 'inactive']
    }
  },
  users: {
    firstName: { required: true, type: 'string' as const, label: 'Keresztnév' },
    lastName: { required: true, type: 'string' as const, label: 'Vezetéknév' },
    email: { required: true, type: 'email' as const, label: 'Email cím' },
    role: { 
      required: true, 
      type: 'enum' as const, 
      label: 'Szerepkör',
      enumValues: ['admin', 'technician', 'viewer']
    },
    permissions: { required: false, type: 'string' as const, label: 'Jogosultságok' },
    phone: { required: false, type: 'phone' as const, label: 'Telefonszám' },
    department: { required: false, type: 'string' as const, label: 'Részleg' },
    status: { 
      required: false, 
      type: 'enum' as const, 
      label: 'Állapot',
      enumValues: ['active', 'inactive']
    }
  },
  inspections: {
    gateId: { required: true, type: 'string' as const, label: 'Kapu ID' },
    inspectorName: { required: true, type: 'string' as const, label: 'Felülvizsgáló neve' },
    scheduledDate: { required: true, type: 'date' as const, label: 'Tervezett dátum' },
    completedDate: { required: false, type: 'date' as const, label: 'Befejezés dátuma' },
    status: { 
      required: true, 
      type: 'enum' as const, 
      label: 'Állapot',
      enumValues: ['scheduled', 'in_progress', 'completed', 'cancelled']
    },
    findings: { required: false, type: 'string' as const, label: 'Megállapítások' },
    recommendations: { required: false, type: 'string' as const, label: 'Javaslatok' },
    nextInspectionDate: { required: false, type: 'date' as const, label: 'Következő felülvizsgálat' }
  }
}

export function FieldMappingStep({ 
  importType, 
  uploadedData, 
  onNext, 
  onBack 
}: FieldMappingStepProps) {
  const [mappings, setMappings] = useState<FieldMapping[]>([])
  const [showPreview, setShowPreview] = useState(false)
  
  const fields = fieldDefinitions[importType]
  const csvFields = uploadedData.length > 0 ? Object.keys(uploadedData[0]).filter(key => key !== '_rowIndex') : []

  useEffect(() => {
    // Initialize mappings with auto-detected matches
    const initialMappings: FieldMapping[] = Object.entries(fields).map(([targetField, config]) => {
      // Try to find matching CSV field
      const matchingCsvField = csvFields.find(csvField => 
        csvField.toLowerCase().includes(targetField.toLowerCase()) ||
        targetField.toLowerCase().includes(csvField.toLowerCase()) ||
        (config.label && csvField.toLowerCase().includes(config.label.toLowerCase()))
      )

      return {
        csvField: matchingCsvField || '',
        targetField,
        isRequired: config.required,
        dataType: config.type,
        enumValues: config.enumValues,
        sample: matchingCsvField && uploadedData.length > 0 ? uploadedData[0][matchingCsvField] : undefined
      }
    })

    setMappings(initialMappings)
  }, [importType, uploadedData, csvFields])

  const updateMapping = (targetField: string, csvField: string | null) => {
    setMappings(prev => prev.map(mapping => 
      mapping.targetField === targetField 
        ? { 
            ...mapping, 
            csvField: csvField || '',
            sample: csvField && uploadedData.length > 0 ? uploadedData[0][csvField] : undefined
          }
        : mapping
    ))
  }

  const resetMappings = () => {
    setMappings(prev => prev.map(mapping => ({
      ...mapping,
      csvField: '',
      sample: undefined
    })))
  }

  const autoDetectMappings = () => {
    setMappings(prev => prev.map(mapping => {
      const targetField = mapping.targetField!
      const config = fields[targetField as keyof typeof fields]
      
      const matchingCsvField = csvFields.find(csvField => 
        csvField.toLowerCase().includes(targetField.toLowerCase()) ||
        targetField.toLowerCase().includes(csvField.toLowerCase()) ||
        (config.label && csvField.toLowerCase().includes(config.label.toLowerCase()))
      )

      return {
        ...mapping,
        csvField: matchingCsvField || '',
        sample: matchingCsvField && uploadedData.length > 0 ? uploadedData[0][matchingCsvField] : undefined
      }
    }))
  }

  const getValidationStatus = () => {
    const requiredMappings = mappings.filter(m => m.isRequired)
    const mappedRequired = requiredMappings.filter(m => m.csvField)
    const duplicateMappings = mappings
      .filter(m => m.csvField)
      .reduce((acc, m) => {
        acc[m.csvField] = (acc[m.csvField] || 0) + 1
        return acc
      }, {} as Record<string, number>)
    
    const hasDuplicates = Object.values(duplicateMappings).some(count => count > 1)
    
    return {
      isValid: mappedRequired.length === requiredMappings.length && !hasDuplicates,
      mappedRequired: mappedRequired.length,
      totalRequired: requiredMappings.length,
      hasDuplicates,
      duplicateFields: Object.entries(duplicateMappings)
        .filter(([_, count]) => count > 1)
        .map(([field]) => field)
    }
  }

  const handleContinue = () => {
    const validation = getValidationStatus()
    if (validation.isValid) {
      onNext(mappings)
    }
  }

  const validation = getValidationStatus()

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle>Mezők hozzárendelése</CardTitle>
          <CardDescription>
            Rendelje hozzá a CSV oszlopokat a megfelelő adatmezőkhöz. 
            A <Badge variant="destructive" className="mx-1">kötelező</Badge> mezőket 
            mindenképpen hozzá kell rendelni.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Badge variant={validation.isValid ? "default" : "secondary"}>
                {validation.mappedRequired}/{validation.totalRequired} kötelező mező hozzárendelve
              </Badge>
              {validation.hasDuplicates && (
                <Badge variant="destructive">
                  Duplikált hozzárendelések
                </Badge>
              )}
            </div>
            
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" onClick={resetMappings}>
                <RotateCcw className="mr-2 h-4 w-4" />
                Törlés
              </Button>
              <Button variant="outline" size="sm" onClick={autoDetectMappings}>
                <CheckCircle className="mr-2 h-4 w-4" />
                Automatikus észlelés
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setShowPreview(!showPreview)}
              >
                {showPreview ? <EyeOff className="mr-2 h-4 w-4" /> : <Eye className="mr-2 h-4 w-4" />}
                {showPreview ? 'Előnézet elrejtése' : 'Adatok előnézete'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Validation Errors */}
      {!validation.isValid && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-1">
              {validation.mappedRequired < validation.totalRequired && (
                <p>Még {validation.totalRequired - validation.mappedRequired} kötelező mezőt kell hozzárendelni.</p>
              )}
              {validation.hasDuplicates && (
                <p>
                  A következő CSV oszlopok többször vannak hozzárendelve: {validation.duplicateFields.join(', ')}
                </p>
              )}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Mapping Table */}
      <Card>
        <CardHeader>
          <CardTitle>Mezőhozzárendelés</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cél mező</TableHead>
                <TableHead>CSV oszlop</TableHead>
                <TableHead>Minta adat</TableHead>
                <TableHead>Típus</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mappings.map((mapping) => {
                const fieldConfig = fields[mapping.targetField! as keyof typeof fields]
                const isDuplicate = validation.duplicateFields.includes(mapping.csvField)
                
                return (
                  <TableRow key={mapping.targetField}>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{fieldConfig.label}</span>
                        {mapping.isRequired && (
                          <Badge variant="destructive" className="text-xs">
                            Kötelező
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Select
                          value={mapping.csvField}
                          onValueChange={(value: string) => updateMapping(mapping.targetField!, value === 'none' ? null : value)}
                        >
                          <SelectTrigger 
                            className={cn(
                              "w-48",
                              isDuplicate && "border-destructive",
                              mapping.isRequired && !mapping.csvField && "border-orange-500"
                            )}
                          >
                            <SelectValue placeholder="Válasszon oszlopot" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="none">
                              <span className="text-muted-foreground">Nincs hozzárendelve</span>
                            </SelectItem>
                            {csvFields.map((field) => (
                              <SelectItem key={field} value={field}>
                                {field}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        
                        {mapping.csvField && (
                          <ArrowRight className="h-4 w-4 text-muted-foreground" />
                        )}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className="max-w-32 truncate text-sm text-muted-foreground">
                        {mapping.sample || '-'}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className="space-y-1">
                        <Badge variant="outline" className="text-xs">
                          {mapping.dataType}
                        </Badge>
                        {mapping.enumValues && (
                          <div className="text-xs text-muted-foreground">
                            Értékek: {mapping.enumValues.join(', ')}
                          </div>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Data Preview */}
      {showPreview && uploadedData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Adatok előnézete</CardTitle>
            <CardDescription>
              Az első 5 sor az importálandó adatokból
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    {csvFields.map((field) => (
                      <TableHead key={field}>{field}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {uploadedData.slice(0, 5).map((row: any, index: number) => (
                    <TableRow key={index}>
                      {csvFields.map((field) => (
                        <TableCell key={field} className="max-w-32 truncate">
                          {row[field] || '-'}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button variant="outline" onClick={onBack}>
          Vissza
        </Button>
        
        <Button 
          onClick={handleContinue}
          disabled={!validation.isValid}
        >
          Tovább a validációhoz
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}