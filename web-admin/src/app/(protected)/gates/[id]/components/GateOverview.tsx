'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  MapPin, 
  Calendar, 
  Wrench, 
  Shield, 
  Zap, 
  Thermometer,
  Weight,
  Ruler,
  Clock,
  Radio,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'

interface GateOverviewProps {
  gate: any // Replace with proper type
}

export function GateOverview({ gate }: GateOverviewProps) {
  const [basicInfoOpen, setBasicInfoOpen] = useState(true)
  const [technicalSpecsOpen, setTechnicalSpecsOpen] = useState(true)
  const [warrantyOpen, setWarrantyOpen] = useState(true)

  return (
    <div className="space-y-6">
      {/* Basic Information */}
      <Collapsible open={basicInfoOpen} onOpenChange={setBasicInfoOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <MapPin className="h-5 w-5 mr-2" />
                  Alapinformációk
                </CardTitle>
                {basicInfoOpen ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </div>
              <CardDescription>
                Kapu alapvető adatai és telepítési információk
              </CardDescription>
            </CardHeader>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Kapu neve</label>
                  <p className="text-lg font-semibold">{gate.name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Típus</label>
                  <div className="flex items-center mt-1">
                    <Badge variant="outline">
                      {gate.type === 'entrance' ? 'Bejárat' : 
                       gate.type === 'exit' ? 'Kijárat' : 
                       gate.type === 'service' ? 'Szerviz' : 'Egyéb'}
                    </Badge>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Telephely</label>
                  <p className="font-medium">{gate.siteName}</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Gyártó</label>
                  <p className="font-medium">{gate.manufacturer}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Modell</label>
                  <p className="font-medium">{gate.model}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Sorozatszám</label>
                  <p className="font-mono text-sm">{gate.serialNumber}</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Telepítés dátuma</label>
                  <div className="flex items-center mt-1">
                    <Calendar className="h-4 w-4 mr-2 text-muted-foreground" />
                    <p>{new Date(gate.installationDate).toLocaleDateString('hu-HU')}</p>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Cím</label>
                  <p className="text-sm">{gate.location.address}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Koordináták</label>
                  <p className="text-sm font-mono">{gate.location.coordinates}</p>
                </div>
              </div>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>

      {/* Technical Specifications */}
      <Collapsible open={technicalSpecsOpen} onOpenChange={setTechnicalSpecsOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <Wrench className="h-5 w-5 mr-2" />
                  Műszaki specifikáció
                </CardTitle>
                {technicalSpecsOpen ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </div>
              <CardDescription>
                Részletes műszaki adatok és teljesítményjellemzők
              </CardDescription>
            </CardHeader>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent className="space-y-6">
              {/* Dimensions */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="bg-muted/20">
                  <CardContent className="flex items-center p-4">
                    <Ruler className="h-8 w-8 text-blue-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Szélesség</p>
                      <p className="text-2xl font-bold">{gate.dimensions.width}m</p>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="bg-muted/20">
                  <CardContent className="flex items-center p-4">
                    <Ruler className="h-8 w-8 text-green-600 mr-3 rotate-90" />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Magasság</p>
                      <p className="text-2xl font-bold">{gate.dimensions.height}m</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-muted/20">
                  <CardContent className="flex items-center p-4">
                    <Weight className="h-8 w-8 text-purple-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Súly</p>
                      <p className="text-2xl font-bold">{gate.dimensions.weight}kg</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Motor & Power */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-semibold flex items-center">
                    <Zap className="h-4 w-4 mr-2" />
                    Meghajtás
                  </h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Típus:</span>
                      <span className="font-medium capitalize">{gate.motor.type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Teljesítmény:</span>
                      <span className="font-medium">{gate.motor.power}W</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Gyártó:</span>
                      <span className="font-medium">{gate.motor.manufacturer}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Modell:</span>
                      <span className="font-medium">{gate.motor.model}</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-semibold flex items-center">
                    <Clock className="h-4 w-4 mr-2" />
                    Működési paraméterek
                  </h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Nyitási idő:</span>
                      <span className="font-medium">{gate.technicalSpecs.openingTime}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Zárási idő:</span>
                      <span className="font-medium">{gate.technicalSpecs.closingTime}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Max. súly:</span>
                      <span className="font-medium">{gate.technicalSpecs.maxWeight}kg</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Távirányító:</span>
                      <span className="font-medium">{gate.technicalSpecs.remoteFrequency}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Environmental Specs */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="bg-muted/20">
                  <CardContent className="flex items-center p-4">
                    <Thermometer className="h-8 w-8 text-orange-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Üzemi hőmérséklet</p>
                      <p className="text-lg font-bold">{gate.technicalSpecs.operationTemperature}</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-muted/20">
                  <CardContent className="flex items-center p-4">
                    <Zap className="h-8 w-8 text-yellow-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Tápellátás</p>
                      <p className="text-lg font-bold">{gate.technicalSpecs.powerSupply}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>

      {/* Warranty Information */}
      <Collapsible open={warrantyOpen} onOpenChange={setWarrantyOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <Shield className="h-5 w-5 mr-2" />
                  Garancia és karbantartás
                </CardTitle>
                {warrantyOpen ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </div>
              <CardDescription>
                Garancia időszak és karbantartási információk
              </CardDescription>
            </CardHeader>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Garancia kezdete</label>
                  <div className="flex items-center mt-1">
                    <Calendar className="h-4 w-4 mr-2 text-muted-foreground" />
                    <p>{new Date(gate.warranty.startDate).toLocaleDateString('hu-HU')}</p>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Garancia vége</label>
                  <div className="flex items-center mt-1">
                    <Calendar className="h-4 w-4 mr-2 text-muted-foreground" />
                    <p>{new Date(gate.warranty.endDate).toLocaleDateString('hu-HU')}</p>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Garancia szolgáltató</label>
                  <p className="font-medium">{gate.warranty.provider}</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Utolsó karbantartás</label>
                  <div className="flex items-center mt-1">
                    <Wrench className="h-4 w-4 mr-2 text-muted-foreground" />
                    <p>{new Date(gate.lastMaintenance).toLocaleDateString('hu-HU')}</p>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Következő karbantartás</label>
                  <div className="flex items-center mt-1">
                    <Clock className="h-4 w-4 mr-2 text-muted-foreground" />
                    <p>{new Date(gate.nextMaintenance).toLocaleDateString('hu-HU')}</p>
                  </div>
                </div>
                <div>
                  <Button variant="outline" size="sm">
                    Karbantartás ütemezése
                  </Button>
                </div>
              </div>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>
    </div>
  )
}