'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { 
  Save,
  X,
  Plus,
  Minus,
  Settings,
  Zap,
  Eye,
  Shield,
  Key,
  Camera
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Switch } from '@/components/ui/switch'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Separator } from '@/components/ui/separator'

import { useApiErrorToast, useFormErrorToast } from '@/lib/toast'
import { apiClient } from '@/lib/api/client'
import { 
  CreateGateFormSchema, 
  UpdateGateFormSchema, 
  CreateGateForm, 
  UpdateGateForm,
  Gate,
  GateType,
  GateStatus 
} from '@/lib/api/types'

interface GateFormProps {
  gate?: Gate | null
  siteId?: string
  onSuccess?: (gate: Gate) => void
  onCancel?: () => void
}

export function GateForm({ gate, siteId, onSuccess, onCancel }: GateFormProps) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { handleFormError } = useFormErrorToast()
  
  const isEditing = !!gate
  const schema = isEditing ? UpdateGateFormSchema : CreateGateFormSchema

  const form = useForm<CreateGateForm | UpdateGateForm>({
    resolver: zodResolver(schema),
    defaultValues: {
      siteId: gate?.siteId || siteId || '',
      name: gate?.name || '',
      type: gate?.type || 'entrance',
      status: gate?.status || 'active',
      serialNumber: gate?.serialNumber || '',
      manufacturer: gate?.manufacturer || '',
      model: gate?.model || '',
      
      // Físikai méretek
      width: gate?.width || undefined,
      height: gate?.height || undefined,
      weight: gate?.weight || undefined,
      
      // Vezérlő
      controller: {
        manufacturer: gate?.controller?.manufacturer || '',
        model: gate?.controller?.model || '',
        serialNumber: gate?.controller?.serialNumber || '',
      },
      
      // Motor
      motor: {
        type: gate?.motor?.type || undefined,
        power: gate?.motor?.power || undefined,
        manufacturer: gate?.motor?.manufacturer || '',
        model: gate?.motor?.model || '',
      },
      
      // Rugók
      springs: {
        type: gate?.springs?.type || undefined,
        count: gate?.springs?.count || undefined,
        manufacturer: gate?.springs?.manufacturer || '',
      },
      
      // Sínek
      tracks: {
        material: gate?.tracks?.material || undefined,
        length: gate?.tracks?.length || undefined,
        manufacturer: gate?.tracks?.manufacturer || '',
      },
      
      // Fotocella
      photocell: {
        hasPhotocell: gate?.photocell?.hasPhotocell || false,
        manufacturer: gate?.photocell?.manufacturer || '',
        model: gate?.photocell?.model || '',
        beamCount: gate?.photocell?.beamCount || undefined,
      },
      
      // Élvédelem
      edgeProtection: {
        hasEdgeProtection: gate?.edgeProtection?.hasEdgeProtection || false,
        type: gate?.edgeProtection?.type || undefined,
        manufacturer: gate?.edgeProtection?.manufacturer || '',
      },
      
      // Kézi kioldó
      manualRelease: {
        hasManualRelease: gate?.manualRelease?.hasManualRelease ?? true,
        type: gate?.manualRelease?.type || undefined,
        location: gate?.manualRelease?.location || '',
      },
      
      // Dátumok
      installationDate: gate?.installationDate || undefined,
      lastMaintenanceDate: gate?.lastMaintenanceDate || undefined,
      nextMaintenanceDate: gate?.nextMaintenanceDate || undefined,
      warrantyExpiryDate: gate?.warrantyExpiryDate || undefined,
      
      notes: gate?.notes || '',
    },
  })

  // Fetch sites for selection
  const { data: sitesResponse } = useQuery({
    queryKey: ['sites'],
    queryFn: () => apiClient.getSites({ limit: 100 }),
    enabled: !siteId, // Only fetch if siteId not provided
  })

  const sites = sitesResponse?.data?.items || []

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: async (data: CreateGateForm | UpdateGateForm) => {
      if (isEditing && gate) {
        return apiClient.updateGate(gate.id, data)
      } else {
        return apiClient.createGate(data)
      }
    },
    onSuccess: (savedGate) => {
      queryClient.invalidateQueries({ queryKey: ['gates'] })
      if (gate) {
        queryClient.invalidateQueries({ queryKey: ['gate', gate.id] })
      }
      onSuccess?.(savedGate)
      if (!onSuccess) {
        router.push('/gates')
      }
    },
    onError: (error) => {
      handleFormError(error, form.setError)
    },
  })

  const onSubmit = (data: CreateGateForm | UpdateGateForm) => {
    saveMutation.mutate(data)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isEditing ? 'Kapu szerkesztése' : 'Új kapu létrehozása'}
          </h1>
          <p className="text-muted-foreground">
            {isEditing 
              ? 'Módosítsa a kapu adatait és komponenseit'
              : 'Adja meg az új kapu részletes adatait'
            }
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={onCancel || (() => router.back())}>
            <X className="mr-2 h-4 w-4" />
            Mégse
          </Button>
          <Button 
            onClick={form.handleSubmit(onSubmit)}
            disabled={saveMutation.isPending}
          >
            <Save className="mr-2 h-4 w-4" />
            {saveMutation.isPending 
              ? 'Mentés...' 
              : isEditing ? 'Módosítások mentése' : 'Kapu létrehozása'
            }
          </Button>
        </div>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="basic">Alapadatok</TabsTrigger>
              <TabsTrigger value="technical">Műszaki</TabsTrigger>
              <TabsTrigger value="components">Komponensek</TabsTrigger>
              <TabsTrigger value="safety">Biztonság</TabsTrigger>
              <TabsTrigger value="maintenance">Karbantartás</TabsTrigger>
            </TabsList>

            {/* Alapadatok */}
            <TabsContent value="basic" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Settings className="mr-2 h-5 w-5" />
                    Alapadatok
                  </CardTitle>
                  <CardDescription>
                    A kapu alapvető azonosító adatai
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {!siteId && (
                      <FormField
                        control={form.control}
                        name="siteId"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Telephely *</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Válasszon telephelyet" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {sites.map((site: any) => (
                                  <SelectItem key={site.id} value={site.id}>
                                    {site.name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    )}

                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Kapu neve *</FormLabel>
                          <FormControl>
                            <Input placeholder="pl. Főbejárat" {...field} />
                          </FormControl>
                          <FormDescription>
                            Egyedi név a kapu azonosítására
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Kapu típusa *</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="entrance">Bejárat</SelectItem>
                              <SelectItem value="exit">Kijárat</SelectItem>
                              <SelectItem value="service">Szerviz</SelectItem>
                              <SelectItem value="emergency">Vészkijárat</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="status"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Állapot</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="active">Aktív</SelectItem>
                              <SelectItem value="inactive">Inaktív</SelectItem>
                              <SelectItem value="maintenance">Karbantartás alatt</SelectItem>
                              <SelectItem value="error">Hibás</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <FormField
                      control={form.control}
                      name="manufacturer"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Gyártó</FormLabel>
                          <FormControl>
                            <Input placeholder="pl. Hörmann" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="model"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Modell</FormLabel>
                          <FormControl>
                            <Input placeholder="pl. LPU 42" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="serialNumber"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Sorozatszám</FormLabel>
                          <FormControl>
                            <Input placeholder="pl. ABC123456" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Műszaki adatok */}
            <TabsContent value="technical" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Fizikai méretek</CardTitle>
                  <CardDescription>
                    A kapu fizikai tulajdonságai
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <FormField
                      control={form.control}
                      name="width"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Szélesség (m)</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              step="0.1"
                              placeholder="pl. 2.5"
                              {...field}
                              onChange={(e) => field.onChange(e.target.value ? parseFloat(e.target.value) : undefined)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="height"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Magasság (m)</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              step="0.1"
                              placeholder="pl. 2.2"
                              {...field}
                              onChange={(e) => field.onChange(e.target.value ? parseFloat(e.target.value) : undefined)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="weight"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Súly (kg)</FormLabel>
                          <FormControl>
                            <Input 
                              type="number"
                              placeholder="pl. 150"
                              {...field}
                              onChange={(e) => field.onChange(e.target.value ? parseFloat(e.target.value) : undefined)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Komponensek */}
            <TabsContent value="components" className="space-y-6">
              {/* Motor */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Zap className="mr-2 h-5 w-5" />
                    Motor
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="motor.type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Motor típus</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Válasszon típust" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="hydraulic">Hidraulikus</SelectItem>
                              <SelectItem value="electric">Elektromos</SelectItem>
                              <SelectItem value="pneumatic">Pneumatikus</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="motor.power"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Teljesítmény (kW)</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              step="0.1"
                              placeholder="pl. 0.75"
                              {...field}
                              onChange={(e) => field.onChange(e.target.value ? parseFloat(e.target.value) : undefined)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="motor.manufacturer"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Motor gyártó</FormLabel>
                          <FormControl>
                            <Input placeholder="pl. SEW" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="motor.model"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Motor modell</FormLabel>
                          <FormControl>
                            <Input placeholder="pl. R37DT80K4" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Vezérlő */}
              <Card>
                <CardHeader>
                  <CardTitle>Vezérlő egység</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <FormField
                      control={form.control}
                      name="controller.manufacturer"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Vezérlő gyártó</FormLabel>
                          <FormControl>
                            <Input placeholder="pl. Hörmann" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="controller.model"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Vezérlő modell</FormLabel>
                          <FormControl>
                            <Input placeholder="pl. A445" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="controller.serialNumber"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Vezérlő sorozatszám</FormLabel>
                          <FormControl>
                            <Input placeholder="pl. CTL987654" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Rugók és sínek */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Rugók</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <FormField
                      control={form.control}
                      name="springs.type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Rugó típus</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Válasszon típust" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="torsion">Torziós</SelectItem>
                              <SelectItem value="extension">Húzórugó</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="springs.count"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Rugók száma</FormLabel>
                          <FormControl>
                            <Input 
                              type="number"
                              placeholder="pl. 2"
                              {...field}
                              onChange={(e) => field.onChange(e.target.value ? parseInt(e.target.value) : undefined)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="springs.manufacturer"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Rugó gyártó</FormLabel>
                          <FormControl>
                            <Input placeholder="pl. Teckentrup" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Sínek</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <FormField
                      control={form.control}
                      name="tracks.material"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Sín anyaga</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Válasszon anyagot" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="steel">Acél</SelectItem>
                              <SelectItem value="aluminum">Alumínium</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="tracks.length"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Sín hossz (m)</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              step="0.1"
                              placeholder="pl. 3.5"
                              {...field}
                              onChange={(e) => field.onChange(e.target.value ? parseFloat(e.target.value) : undefined)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="tracks.manufacturer"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Sín gyártó</FormLabel>
                          <FormControl>
                            <Input placeholder="pl. Chamberlain" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Biztonságtechnika */}
            <TabsContent value="safety" className="space-y-6">
              {/* Fotocella */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Eye className="mr-2 h-5 w-5" />
                    Fotocella rendszer
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <FormField
                    control={form.control}
                    name="photocell.hasPhotocell"
                    render={({ field }) => (
                      <FormItem className="flex items-center space-x-2">
                        <FormControl>
                          <Switch
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <FormLabel>Fotocella rendszer telepítve</FormLabel>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {form.watch('photocell.hasPhotocell') && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <FormField
                        control={form.control}
                        name="photocell.manufacturer"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Fotocella gyártó</FormLabel>
                            <FormControl>
                              <Input placeholder="pl. CAME" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="photocell.model"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Fotocella modell</FormLabel>
                            <FormControl>
                              <Input placeholder="pl. DIR30" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="photocell.beamCount"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Fotosugarak száma</FormLabel>
                            <FormControl>
                              <Input 
                                type="number"
                                placeholder="pl. 2"
                                {...field}
                                onChange={(e) => field.onChange(e.target.value ? parseInt(e.target.value) : undefined)}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Élvédelem */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Shield className="mr-2 h-5 w-5" />
                    Élvédelem
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <FormField
                    control={form.control}
                    name="edgeProtection.hasEdgeProtection"
                    render={({ field }) => (
                      <FormItem className="flex items-center space-x-2">
                        <FormControl>
                          <Switch
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <FormLabel>Élvédelem telepítve</FormLabel>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {form.watch('edgeProtection.hasEdgeProtection') && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="edgeProtection.type"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Élvédelem típusa</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Válasszon típust" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="pneumatic">Pneumatikus</SelectItem>
                                <SelectItem value="optical">Optikai</SelectItem>
                                <SelectItem value="mechanical">Mechanikus</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="edgeProtection.manufacturer"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Élvédelem gyártó</FormLabel>
                            <FormControl>
                              <Input placeholder="pl. FAAC" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Kézi kioldó */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Key className="mr-2 h-5 w-5" />
                    Kézi kioldó
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <FormField
                    control={form.control}
                    name="manualRelease.hasManualRelease"
                    render={({ field }) => (
                      <FormItem className="flex items-center space-x-2">
                        <FormControl>
                          <Switch
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <FormLabel>Kézi kioldó rendszer</FormLabel>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {form.watch('manualRelease.hasManualRelease') && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="manualRelease.type"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Kioldó típusa</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Válasszon típust" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="key">Kulcs</SelectItem>
                                <SelectItem value="lever">Kar</SelectItem>
                                <SelectItem value="cord">Zsinór</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="manualRelease.location"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Kioldó helye</FormLabel>
                            <FormControl>
                              <Input placeholder="pl. Bal oldalsó sarok" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Karbantartás */}
            <TabsContent value="maintenance" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Karbantartási adatok</CardTitle>
                  <CardDescription>
                    Telepítési és karbantartási dátumok
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="installationDate"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Telepítés dátuma</FormLabel>
                          <FormControl>
                            <Input type="datetime-local" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="warrantyExpiryDate"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Garancia lejárata</FormLabel>
                          <FormControl>
                            <Input type="datetime-local" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="lastMaintenanceDate"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Utolsó karbantartás</FormLabel>
                          <FormControl>
                            <Input type="datetime-local" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="nextMaintenanceDate"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Következő karbantartás</FormLabel>
                          <FormControl>
                            <Input type="datetime-local" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <Separator />

                  <FormField
                    control={form.control}
                    name="notes"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Megjegyzések</FormLabel>
                        <FormControl>
                          <Textarea 
                            placeholder="További információk, speciális utasítások..."
                            rows={4}
                            {...field} 
                          />
                        </FormControl>
                        <FormDescription>
                          Bármilyen további információ a kapuról
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </form>
      </Form>
    </div>
  )
}