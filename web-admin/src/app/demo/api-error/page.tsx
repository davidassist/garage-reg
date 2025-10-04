'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useApiErrorToast, useFormErrorToast } from '@/lib/toast'
import { apiClient } from '@/lib/api/client'
import { ValidationApiError, ApiClientError } from '@/lib/api/types'

const clientFormSchema = z.object({
  name: z.string().min(1, 'Az ügyfél neve kötelező'),
  email: z.string().email('Érvényes email címet adjon meg'),
  phone: z.string().optional(),
  taxNumber: z.string().optional(),
  contactPerson: z.string().optional(),
  notes: z.string().optional(),
})

type ClientFormData = z.infer<typeof clientFormSchema>

export default function ApiErrorDemoPage() {
  const [isLoading, setIsLoading] = useState(false)
  const { showError, showSuccess, showValidationErrors } = useApiErrorToast()
  const { handleFormError } = useFormErrorToast()

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    reset,
  } = useForm<ClientFormData>({
    resolver: zodResolver(clientFormSchema),
  })

  // Szándékos 422 validációs hiba tesztelése
  const triggerValidationError = async () => {
    setIsLoading(true)
    try {
      // Szándékosan hibás adatok küldése
      await apiClient.createClient({
        name: '', // Kötelező mező üresen hagyva
        email: 'invalid-email', // Hibás email formátum
        taxNumber: '12345', // Túl rövid adószám
        phone: '+36-invalid', // Hibás telefon formátum
      })
    } catch (error) {
      console.log('Captured validation error:', error)
      
      if (error instanceof ValidationApiError) {
        showSuccess('✅ Validation error sikeresen elkapva és megjelenítve!')
        
        // React Hook Form error objektumokként beállítjuk
        Object.entries(error.fieldErrors).forEach(([field, messages]) => {
          if (messages.length > 0) {
            setError(field as keyof ClientFormData, {
              type: 'server',
              message: messages[0]
            })
          }
        })
        
        // Toast megjelenítés is
        showValidationErrors(error.fieldErrors)
      } else {
        handleFormError(error, setError)
      }
    } finally {
      setIsLoading(false)
    }
  }

  // 401 Unauthorized hiba tesztelése
  const trigger401Error = async () => {
    setIsLoading(true)
    try {
      // Token nélküli védett végpont hívása
      localStorage.removeItem('auth-token')
      await apiClient.getClients()
    } catch (error) {
      console.log('Captured 401 error:', error)
      showError(error, 'Sikeres 401 hiba kezelés!')
    } finally {
      setIsLoading(false)
    }
  }

  // 403 Forbidden hiba tesztelése  
  const trigger403Error = async () => {
    setIsLoading(true)
    try {
      // Mock 403 response
      throw new ApiClientError(403, 'FORBIDDEN', 'Nincs jogosultsága ehhez a művelethez')
    } catch (error) {
      console.log('Captured 403 error:', error)
      showError(error, 'Sikeres 403 hiba kezelés!')
    } finally {
      setIsLoading(false)
    }
  }

  // 500 Server Error tesztelése
  const trigger500Error = async () => {
    setIsLoading(true)
    try {
      throw new ApiClientError(500, 'INTERNAL_SERVER_ERROR', 'Belső szerver hiba')
    } catch (error) {
      console.log('Captured 500 error:', error)
      showError(error, 'Sikeres 500 hiba kezelés!')
    } finally {
      setIsLoading(false)
    }
  }

  // Network error tesztelése
  const triggerNetworkError = async () => {
    setIsLoading(true)
    try {
      // Hibás URL-re történő kérés szimulálása
      const originalBaseURL = apiClient['baseURL']
      apiClient['baseURL'] = 'http://nonexistent-server:9999'
      
      await apiClient.getDashboardStats()
    } catch (error) {
      console.log('Captured network error:', error)
      showError(error, 'Sikeres network error kezelés!')
    } finally {
      setIsLoading(false)
    }
  }

  const onValidFormSubmit = async (data: ClientFormData) => {
    setIsLoading(true)
    try {
      await apiClient.createClient(data)
      showSuccess('Ügyfél sikeresen létrehozva!')
      reset()
    } catch (error) {
      handleFormError(error, setError)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="max-w-4xl">
        <h1 className="text-3xl font-bold mb-2">API Hibakezelés és Toast Demo</h1>
        <p className="text-gray-600 mb-8">
          Ez az oldal bemutatja a fejlett fetch wrapper, hiba-envelope dekódolás és toast rendszer működését.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Validation Error Demo */}
          <Card>
            <CardHeader>
              <CardTitle>422 Validation Error Teszt</CardTitle>
              <CardDescription>
                Szándékosan hibás adatok küldése a mezőszintű hiba megjelenítés tesztelésére
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button 
                onClick={triggerValidationError}
                disabled={isLoading}
                variant="destructive"
                className="w-full"
              >
                422 Validation Error Kiváltása
              </Button>
              
              <div className="text-sm text-gray-600 space-y-2">
                <p><strong>Teszt adatok:</strong></p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Üres név mező</li>
                  <li>Hibás email formátum</li>
                  <li>Túl rövid adószám</li>
                  <li>Hibás telefon formátum</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Auth Errors Demo */}
          <Card>
            <CardHeader>
              <CardTitle>Auth Hibák Tesztelése</CardTitle>
              <CardDescription>
                401/403 hibák kezelésének bemutatása
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                onClick={trigger401Error}
                disabled={isLoading}
                variant="outline"
                className="w-full"
              >
                401 Unauthorized
              </Button>
              
              <Button 
                onClick={trigger403Error}
                disabled={isLoading}
                variant="outline"
                className="w-full"
              >
                403 Forbidden
              </Button>
            </CardContent>
          </Card>

          {/* Server Errors Demo */}
          <Card>
            <CardHeader>
              <CardTitle>Szerver Hibák Tesztelése</CardTitle>
              <CardDescription>
                5xx hibák és network errorok kezelése
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                onClick={trigger500Error}
                disabled={isLoading}
                variant="outline"
                className="w-full"
              >
                500 Server Error
              </Button>
              
              <Button 
                onClick={triggerNetworkError}
                disabled={isLoading}
                variant="outline"
                className="w-full"
              >
                Network Error
              </Button>
            </CardContent>
          </Card>

          {/* Valid Form Demo */}
          <Card>
            <CardHeader>
              <CardTitle>Érvényes Form Teszt</CardTitle>
              <CardDescription>
                Sikeres API hívás és form kezelés
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onValidFormSubmit)} className="space-y-4">
                <div>
                  <Label htmlFor="name">Ügyfél neve *</Label>
                  <Input
                    id="name"
                    {...register('name')}
                    placeholder="Példa Kft."
                    className={errors.name ? 'border-red-500' : ''}
                  />
                  {errors.name && (
                    <p className="text-sm text-red-600 mt-1">{errors.name.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="email">Email cím *</Label>
                  <Input
                    id="email"
                    type="email"
                    {...register('email')}
                    placeholder="info@example.com"
                    className={errors.email ? 'border-red-500' : ''}
                  />
                  {errors.email && (
                    <p className="text-sm text-red-600 mt-1">{errors.email.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="phone">Telefon</Label>
                  <Input
                    id="phone"
                    {...register('phone')}
                    placeholder="+36 1 234 5678"
                    className={errors.phone ? 'border-red-500' : ''}
                  />
                  {errors.phone && (
                    <p className="text-sm text-red-600 mt-1">{errors.phone.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="taxNumber">Adószám</Label>
                  <Input
                    id="taxNumber"
                    {...register('taxNumber')}
                    placeholder="12345678-1-23"
                    className={errors.taxNumber ? 'border-red-500' : ''}
                  />
                  {errors.taxNumber && (
                    <p className="text-sm text-red-600 mt-1">{errors.taxNumber.message}</p>
                  )}
                </div>

                <Button 
                  type="submit" 
                  disabled={isLoading}
                  className="w-full"
                >
                  {isLoading ? 'Küldés...' : 'Ügyfél Létrehozása'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Acceptance Criteria */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>✅ Elfogadási Kritériumok</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start space-x-2">
                <span className="text-green-600 font-bold">✓</span>
                <div>
                  <strong>Enhanced fetch wrapper:</strong>
                  <p className="text-sm text-gray-600">
                    Automatikus retry exponenciális backoff-fal, request deduplication, 
                    401/403 kezelés token refresh-sel
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-2">
                <span className="text-green-600 font-bold">✓</span>
                <div>
                  <strong>Hiba-envelope dekódolás:</strong>
                  <p className="text-sm text-gray-600">
                    Zod sémák a ValidationError, AuthError, ServerError típusokhoz
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-2">
                <span className="text-green-600 font-bold">✓</span>
                <div>
                  <strong>Globális Toast rendszer:</strong>
                  <p className="text-sm text-gray-600">
                    Magyar nyelvű hibaüzenetek, mezőszintű validation error megjelenítés
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-2">
                <span className="text-green-600 font-bold">✓</span>
                <div>
                  <strong>useApiErrorToast() hook:</strong>
                  <p className="text-sm text-gray-600">
                    Form integráció React Hook Form-mal, státusz koordinálás
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-2">
                <span className="text-green-600 font-bold">✓</span>
                <div>
                  <strong>422 validation error mezőszinten:</strong>
                  <p className="text-sm text-gray-600">
                    A szándékos hibák elegánsan jelennek meg mind toast-ban, mind form field-ekben
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}