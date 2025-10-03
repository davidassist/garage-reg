import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { X, Save, AlertCircle } from 'lucide-react'
import { 
  CreateGateSchema, 
  UpdateGateSchema, 
  type CreateGateRequest,
  type UpdateGateRequest,
  type Gate,
  GateType,
  GateSize,
  GateStatus,
  ControllerType,
  MotorType,
  GateTypeLabels,
  GateSizeLabels,
  GateStatusLabels,
  ControllerTypeLabels,
  MotorTypeLabels,
} from '@/lib/types/gate'

interface GateFormProps {
  gate?: Gate
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: CreateGateRequest | UpdateGateRequest) => void
  isSubmitting?: boolean
}

export default function GateForm({ 
  gate, 
  isOpen, 
  onClose, 
  onSubmit, 
  isSubmitting = false 
}: GateFormProps) {
  const isEditing = !!gate
  const schema = isEditing ? UpdateGateSchema : CreateGateSchema

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<CreateGateRequest | UpdateGateRequest>({
    resolver: zodResolver(schema),
    defaultValues: gate ? {
      name: gate.name,
      code: gate.code,
      type: gate.type,
      size: gate.size,
      status: gate.status,
      serialNumber: gate.serialNumber,
      manufacturer: gate.manufacturer,
      model: gate.model,
      yearOfManufacture: gate.yearOfManufacture,
      width: gate.width,
      height: gate.height,
      weight: gate.weight,
      controllerType: gate.controllerType,
      controllerModel: gate.controllerModel,
      remoteControls: gate.remoteControls,
      motorType: gate.motorType,
      motorPower: gate.motorPower,
      motorModel: gate.motorModel,
      gearboxRatio: gate.gearboxRatio,
      springs: gate.springs,
      rails: gate.rails,
      photocells: gate.photocells,
      edgeProtection: gate.edgeProtection,
      manualRelease: gate.manualRelease,
      siteId: gate.siteId,
      buildingId: gate.buildingId,
      location: gate.location,
      installationDate: gate.installationDate,
      installerCompany: gate.installerCompany,
      lastMaintenance: gate.lastMaintenance,
      nextMaintenance: gate.nextMaintenance,
      maintenanceInterval: gate.maintenanceInterval,
      notes: gate.notes,
      manualUrl: gate.manualUrl,
      warrantyExpiry: gate.warrantyExpiry,
    } : {
      type: GateType.SWING,
      size: GateSize.MEDIUM,
      status: GateStatus.ACTIVE,
      controllerType: ControllerType.REMOTE,
      motorType: MotorType.AC,
    },
  })

  const handleFormSubmit = (data: CreateGateRequest | UpdateGateRequest) => {
    onSubmit(data)
    if (!isEditing) {
      reset()
    }
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {isEditing ? 'Kapu szerkesztése' : 'Új kapu hozzáadása'}
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(handleFormSubmit)} className="overflow-y-auto max-h-[calc(90vh-140px)]">
          <div className="p-6 space-y-8">
            {/* Basic Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Alapadatok</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                    Kapu neve *
                  </label>
                  <input
                    id="name"
                    {...register('name')}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.name ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="pl. Főbejárat kapu"
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.name.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-1">
                    Kapu kód *
                  </label>
                  <input
                    id="code"
                    {...register('code')}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.code ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="pl. GATE-001"
                  />
                  {errors.code && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.code.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">
                    Típus *
                  </label>
                  <Controller
                    name="type"
                    control={control}
                    render={({ field }) => (
                      <select
                        {...field}
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors.type ? 'border-red-500' : 'border-gray-300'
                        }`}
                      >
                        {Object.entries(GateTypeLabels).map(([value, label]) => (
                          <option key={value} value={value}>
                            {label}
                          </option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.type && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.type.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="size" className="block text-sm font-medium text-gray-700 mb-1">
                    Méret *
                  </label>
                  <Controller
                    name="size"
                    control={control}
                    render={({ field }) => (
                      <select
                        {...field}
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors.size ? 'border-red-500' : 'border-gray-300'
                        }`}
                      >
                        {Object.entries(GateSizeLabels).map(([value, label]) => (
                          <option key={value} value={value}>
                            {label}
                          </option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.size && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.size.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
                    Állapot *
                  </label>
                  <Controller
                    name="status"
                    control={control}
                    render={({ field }) => (
                      <select
                        {...field}
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors.status ? 'border-red-500' : 'border-gray-300'
                        }`}
                      >
                        {Object.entries(GateStatusLabels).map(([value, label]) => (
                          <option key={value} value={value}>
                            {label}
                          </option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.status && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.status.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
                    Helyszín
                  </label>
                  <input
                    id="location"
                    {...register('location')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="pl. Főépület bejárat"
                  />
                </div>
              </div>
            </div>

            {/* Technical Specifications */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Műszaki adatok</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="serialNumber" className="block text-sm font-medium text-gray-700 mb-1">
                    Sorozatszám *
                  </label>
                  <input
                    id="serialNumber"
                    {...register('serialNumber')}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.serialNumber ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="pl. SN123456789"
                  />
                  {errors.serialNumber && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.serialNumber.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="manufacturer" className="block text-sm font-medium text-gray-700 mb-1">
                    Gyártó *
                  </label>
                  <input
                    id="manufacturer"
                    {...register('manufacturer')}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.manufacturer ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="pl. CAME, BFT, Nice"
                  />
                  {errors.manufacturer && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.manufacturer.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-1">
                    Modell
                  </label>
                  <input
                    id="model"
                    {...register('model')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="pl. ATI 3000"
                  />
                </div>

                <div>
                  <label htmlFor="yearOfManufacture" className="block text-sm font-medium text-gray-700 mb-1">
                    Gyártási év
                  </label>
                  <input
                    id="yearOfManufacture"
                    type="number"
                    {...register('yearOfManufacture', { valueAsNumber: true })}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.yearOfManufacture ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder={new Date().getFullYear().toString()}
                  />
                  {errors.yearOfManufacture && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.yearOfManufacture.message}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Dimensions */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Méretek</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="width" className="block text-sm font-medium text-gray-700 mb-1">
                    Szélesség (m)
                  </label>
                  <input
                    id="width"
                    type="number"
                    step="0.1"
                    {...register('width', { valueAsNumber: true })}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.width ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="pl. 3.5"
                  />
                  {errors.width && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.width.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="height" className="block text-sm font-medium text-gray-700 mb-1">
                    Magasság (m)
                  </label>
                  <input
                    id="height"
                    type="number"
                    step="0.1"
                    {...register('height', { valueAsNumber: true })}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.height ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="pl. 2.0"
                  />
                  {errors.height && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.height.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="weight" className="block text-sm font-medium text-gray-700 mb-1">
                    Súly (kg)
                  </label>
                  <input
                    id="weight"
                    type="number"
                    step="0.1"
                    {...register('weight', { valueAsNumber: true })}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.weight ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="pl. 150"
                  />
                  {errors.weight && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.weight.message}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Control System */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Vezérlőrendszer</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="controllerType" className="block text-sm font-medium text-gray-700 mb-1">
                    Vezérlő típusa *
                  </label>
                  <Controller
                    name="controllerType"
                    control={control}
                    render={({ field }) => (
                      <select
                        {...field}
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors.controllerType ? 'border-red-500' : 'border-gray-300'
                        }`}
                      >
                        {Object.entries(ControllerTypeLabels).map(([value, label]) => (
                          <option key={value} value={value}>
                            {label}
                          </option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.controllerType && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.controllerType.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="controllerModel" className="block text-sm font-medium text-gray-700 mb-1">
                    Vezérlő modell
                  </label>
                  <input
                    id="controllerModel"
                    {...register('controllerModel')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="pl. ZA3P"
                  />
                </div>

                <div>
                  <label htmlFor="remoteControls" className="block text-sm font-medium text-gray-700 mb-1">
                    Távirányítók száma
                  </label>
                  <input
                    id="remoteControls"
                    type="number"
                    min="0"
                    {...register('remoteControls', { valueAsNumber: true })}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.remoteControls ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="pl. 2"
                  />
                  {errors.remoteControls && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.remoteControls.message}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Motor System */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Motorrendszer</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="motorType" className="block text-sm font-medium text-gray-700 mb-1">
                    Motor típusa *
                  </label>
                  <Controller
                    name="motorType"
                    control={control}
                    render={({ field }) => (
                      <select
                        {...field}
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors.motorType ? 'border-red-500' : 'border-gray-300'
                        }`}
                      >
                        {Object.entries(MotorTypeLabels).map(([value, label]) => (
                          <option key={value} value={value}>
                            {label}
                          </option>
                        ))}
                      </select>
                    )}
                  />
                  {errors.motorType && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.motorType.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="motorPower" className="block text-sm font-medium text-gray-700 mb-1">
                    Motor teljesítmény (W)
                  </label>
                  <input
                    id="motorPower"
                    type="number"
                    min="0"
                    {...register('motorPower', { valueAsNumber: true })}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.motorPower ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="pl. 550"
                  />
                  {errors.motorPower && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.motorPower.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="motorModel" className="block text-sm font-medium text-gray-700 mb-1">
                    Motor modell
                  </label>
                  <input
                    id="motorModel"
                    {...register('motorModel')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="pl. BX-243"
                  />
                </div>

                <div>
                  <label htmlFor="gearboxRatio" className="block text-sm font-medium text-gray-700 mb-1">
                    Hajtómű áttétel
                  </label>
                  <input
                    id="gearboxRatio"
                    {...register('gearboxRatio')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="pl. 1:20"
                  />
                </div>
              </div>
            </div>

            {/* Safety Systems - Complex nested objects simplified for demo */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Biztonsági rendszerek</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="photocells.count" className="block text-sm font-medium text-gray-700 mb-1">
                    Fotocellák száma
                  </label>
                  <input
                    id="photocells.count"
                    type="number"
                    min="0"
                    {...register('photocells.count', { valueAsNumber: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="pl. 2"
                  />
                </div>

                <div>
                  <label htmlFor="photocells.type" className="block text-sm font-medium text-gray-700 mb-1">
                    Fotocella típus
                  </label>
                  <input
                    id="photocells.type"
                    {...register('photocells.type')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="pl. Infravörös"
                  />
                </div>

                <div>
                  <label htmlFor="edgeProtection.type" className="block text-sm font-medium text-gray-700 mb-1">
                    Élvédelem típusa
                  </label>
                  <input
                    id="edgeProtection.type"
                    {...register('edgeProtection.type')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="pl. Gumiszalag, érzékelő"
                  />
                </div>

                <div>
                  <label htmlFor="manualRelease.type" className="block text-sm font-medium text-gray-700 mb-1">
                    Kézi kioldó típusa
                  </label>
                  <input
                    id="manualRelease.type"
                    {...register('manualRelease.type')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="pl. Kulcsos, bowdenes"
                  />
                </div>
              </div>
            </div>

            {/* Additional Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">További információk</h3>
              <div className="space-y-4">
                <div>
                  <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
                    Megjegyzések
                  </label>
                  <textarea
                    id="notes"
                    rows={3}
                    {...register('notes')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="További információk, megjegyzések..."
                  />
                </div>

                <div>
                  <label htmlFor="manualUrl" className="block text-sm font-medium text-gray-700 mb-1">
                    Használati útmutató URL
                  </label>
                  <input
                    id="manualUrl"
                    type="url"
                    {...register('manualUrl')}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.manualUrl ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="https://example.com/manual.pdf"
                  />
                  {errors.manualUrl && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.manualUrl.message}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end space-x-3 px-6 py-4 border-t border-gray-200 bg-gray-50">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              Mégse
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Mentés...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {isEditing ? 'Mentés' : 'Létrehozás'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}