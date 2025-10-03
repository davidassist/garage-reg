import { X, Edit, Trash2, FileText, Calendar, Wrench, Shield, Settings, MapPin } from 'lucide-react'
import { format } from 'date-fns'
import { hu } from 'date-fns/locale'
import { 
  Gate, 
  GateTypeLabels, 
  GateStatusLabels, 
  GateStatusColors,
  ControllerTypeLabels,
  MotorTypeLabels,
} from '@/lib/types/gate'

interface GateDetailViewProps {
  gate: Gate
  isOpen: boolean
  onClose: () => void
  onEdit: () => void
  onDelete: () => void
}

export default function GateDetailView({ 
  gate, 
  isOpen, 
  onClose, 
  onEdit, 
  onDelete 
}: GateDetailViewProps) {
  if (!isOpen) return null

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-'
    try {
      return format(new Date(dateString), 'yyyy. MMMM dd.', { locale: hu })
    } catch {
      return '-'
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{gate.name}</h2>
              <p className="text-sm text-gray-600">Kód: {gate.code}</p>
            </div>
            <div className="flex items-center">
              <span 
                className={`inline-flex px-3 py-1 text-sm font-medium rounded-full border ${
                  GateStatusColors[gate.status as keyof typeof GateStatusColors]
                }`}
              >
                {GateStatusLabels[gate.status as keyof typeof GateStatusLabels]}
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={onEdit}
              className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Edit className="h-4 w-4 mr-2" />
              Szerkesztés
            </button>
            <button
              onClick={onDelete}
              className="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Törlés
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-100px)] p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Basic Info */}
            <div className="space-y-6">
              {/* Basic Information */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <FileText className="h-5 w-5 text-gray-600 mr-2" />
                  <h3 className="text-lg font-medium text-gray-900">Alapadatok</h3>
                </div>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Típus:</span>
                    <p className="text-gray-900">{GateTypeLabels[gate.type as keyof typeof GateTypeLabels]}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Sorozatszám:</span>
                    <p className="text-gray-900 font-mono">{gate.serialNumber}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Gyártó:</span>
                    <p className="text-gray-900">{gate.manufacturer}</p>
                  </div>
                  {gate.model && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Modell:</span>
                      <p className="text-gray-900">{gate.model}</p>
                    </div>
                  )}
                  {gate.yearOfManufacture && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Gyártási év:</span>
                      <p className="text-gray-900">{gate.yearOfManufacture}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Location */}
              {gate.location && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center mb-3">
                    <MapPin className="h-5 w-5 text-gray-600 mr-2" />
                    <h3 className="text-lg font-medium text-gray-900">Helyszín</h3>
                  </div>
                  <p className="text-gray-900">{gate.location}</p>
                </div>
              )}

              {/* Dimensions */}
              {(gate.width || gate.height || gate.weight) && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Méretek</h3>
                  <div className="space-y-3">
                    {gate.width && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Szélesség:</span>
                        <p className="text-gray-900">{gate.width} m</p>
                      </div>
                    )}
                    {gate.height && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Magasság:</span>
                        <p className="text-gray-900">{gate.height} m</p>
                      </div>
                    )}
                    {gate.weight && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Súly:</span>
                        <p className="text-gray-900">{gate.weight} kg</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Middle Column - Technical Details */}
            <div className="space-y-6">
              {/* Control System */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <Settings className="h-5 w-5 text-gray-600 mr-2" />
                  <h3 className="text-lg font-medium text-gray-900">Vezérlőrendszer</h3>
                </div>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Típus:</span>
                    <p className="text-gray-900">
                      {ControllerTypeLabels[gate.controllerType as keyof typeof ControllerTypeLabels]}
                    </p>
                  </div>
                  {gate.controllerModel && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Modell:</span>
                      <p className="text-gray-900">{gate.controllerModel}</p>
                    </div>
                  )}
                  {gate.remoteControls !== undefined && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Távirányítók:</span>
                      <p className="text-gray-900">{gate.remoteControls} db</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Motor System */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <Wrench className="h-5 w-5 text-gray-600 mr-2" />
                  <h3 className="text-lg font-medium text-gray-900">Motorrendszer</h3>
                </div>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Típus:</span>
                    <p className="text-gray-900">
                      {MotorTypeLabels[gate.motorType as keyof typeof MotorTypeLabels]}
                    </p>
                  </div>
                  {gate.motorPower && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Teljesítmény:</span>
                      <p className="text-gray-900">{gate.motorPower} W</p>
                    </div>
                  )}
                  {gate.motorModel && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Modell:</span>
                      <p className="text-gray-900">{gate.motorModel}</p>
                    </div>
                  )}
                  {gate.gearboxRatio && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Hajtómű áttétel:</span>
                      <p className="text-gray-900">{gate.gearboxRatio}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Safety Systems */}
              {(gate.photocells || gate.edgeProtection || gate.manualRelease) && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center mb-3">
                    <Shield className="h-5 w-5 text-gray-600 mr-2" />
                    <h3 className="text-lg font-medium text-gray-900">Biztonsági rendszerek</h3>
                  </div>
                  <div className="space-y-3">
                    {gate.photocells && gate.photocells.count !== undefined && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Fotocellák:</span>
                        <p className="text-gray-900">
                          {gate.photocells.count} db
                          {gate.photocells.type && ` (${gate.photocells.type})`}
                        </p>
                      </div>
                    )}
                    {gate.edgeProtection && gate.edgeProtection.type && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Élvédelem:</span>
                        <p className="text-gray-900">{gate.edgeProtection.type}</p>
                      </div>
                    )}
                    {gate.manualRelease && gate.manualRelease.type && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Kézi kioldó:</span>
                        <p className="text-gray-900">{gate.manualRelease.type}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column - Maintenance & Dates */}
            <div className="space-y-6">
              {/* Maintenance */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <Calendar className="h-5 w-5 text-gray-600 mr-2" />
                  <h3 className="text-lg font-medium text-gray-900">Karbantartás</h3>
                </div>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Utolsó karbantartás:</span>
                    <p className="text-gray-900">{formatDate(gate.lastMaintenance)}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Következő karbantartás:</span>
                    <p className="text-gray-900">{formatDate(gate.nextMaintenance)}</p>
                  </div>
                  {gate.maintenanceInterval && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Karbantartási ciklus:</span>
                      <p className="text-gray-900">{gate.maintenanceInterval} nap</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Installation */}
              {(gate.installationDate || gate.installerCompany) && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Telepítés</h3>
                  <div className="space-y-3">
                    {gate.installationDate && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Telepítés dátuma:</span>
                        <p className="text-gray-900">{formatDate(gate.installationDate)}</p>
                      </div>
                    )}
                    {gate.installerCompany && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Telepítő cég:</span>
                        <p className="text-gray-900">{gate.installerCompany}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Documentation */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Dokumentáció</h3>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Létrehozva:</span>
                    <p className="text-gray-900">{formatDate(gate.createdAt)}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Létrehozta:</span>
                    <p className="text-gray-900">{gate.createdBy}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Módosítva:</span>
                    <p className="text-gray-900">{formatDate(gate.updatedAt)}</p>
                  </div>
                  {gate.updatedBy && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Módosította:</span>
                      <p className="text-gray-900">{gate.updatedBy}</p>
                    </div>
                  )}
                  {gate.manualUrl && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Használati útmutató:</span>
                      <a 
                        href={gate.manualUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 underline break-all"
                      >
                        Megnyitás
                      </a>
                    </div>
                  )}
                  {gate.warrantyExpiry && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Garancia lejárat:</span>
                      <p className="text-gray-900">{formatDate(gate.warrantyExpiry)}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Notes */}
          {gate.notes && (
            <div className="mt-6 bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Megjegyzések</h3>
              <p className="text-gray-700 whitespace-pre-wrap">{gate.notes}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}