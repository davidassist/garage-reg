'use client'

import { useState } from 'react'
import { useApiErrorToast, customToast } from '@/lib/hooks/useApiErrorToast'
import { apiClient } from '@/lib/api/client'
import { 
  ApiClientError, 
  ValidationApiError, 
  NetworkError 
} from '@/lib/api/types'
import { withRequiredAuth } from '@/lib/auth/with-auth'

function ApiTestPage() {
  const { showError, showSuccess, showLoading, dismiss } = useApiErrorToast()
  const [loading, setLoading] = useState<string | null>(null)

  // Simulate different types of API errors
  const simulateValidationError = () => {
    const error = new ValidationApiError(
      'Az űrlap érvényesítése sikertelen',
      {
        email: ['Érvényes email címet adjon meg', 'Ez az email már használatban van'],
        password: ['A jelszó legalább 8 karakter hosszú kell legyen'],
        name: ['A név megadása kötelező'],
      }
    )
    showError(error)
  }

  const simulateUnauthorizedError = () => {
    const error = new ApiClientError(401, 'UNAUTHORIZED', 'Nincs jogosultsága ehhez a művelethez')
    showError(error)
  }

  const simulateForbiddenError = () => {
    const error = new ApiClientError(403, 'FORBIDDEN', 'Hozzáférés megtagadva')
    showError(error)
  }

  const simulateNotFoundError = () => {
    const error = new ApiClientError(404, 'NOT_FOUND', 'A keresett erőforrás nem található')
    showError(error)
  }

  const simulateServerError = () => {
    const error = new ApiClientError(500, 'SERVER_ERROR', 'Belső szerver hiba történt')
    showError(error)
  }

  const simulateNetworkError = () => {
    const error = new NetworkError('Hálózati kapcsolat hiba')
    showError(error)
  }

  // Test real API calls with error handling
  const testRealApiCall = async (endpoint: string) => {
    const loadingToast = showLoading('API hívás folyamatban...')
    setLoading(loadingToast)

    try {
      const response = await apiClient.get(endpoint)
      dismiss(loadingToast)
      setLoading(null)
      showSuccess('API hívás sikeres!')
      console.log('Response:', response.data)
    } catch (error) {
      dismiss(loadingToast)
      setLoading(null)
      showError(error)
    }
  }

  // Test validation endpoint (should return 422)
  const testValidationEndpoint = async () => {
    const loadingToast = showLoading('Érvényesítés tesztelése...')
    setLoading(loadingToast)

    try {
      await apiClient.post('/auth/login', {
        email: 'invalid-email',
        password: '123', // too short
      })
      dismiss(loadingToast)
      setLoading(null)
      showSuccess('Váratlan siker!')
    } catch (error) {
      dismiss(loadingToast)
      setLoading(null)
      showError(error)
    }
  }

  const showCustomMessages = () => {
    customToast.success('Művelet sikeresen végrehajtva!')
    
    setTimeout(() => {
      customToast.warning('Figyelmeztetés: Ellenőrizze az adatokat!')
    }, 1000)
    
    setTimeout(() => {
      customToast.info('Információ: Az új funkció elérhető!')
    }, 2000)
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        API Hibakezelés és Toast Teszt
      </h1>
      
      <div className="space-y-8">
        {/* Simulated Errors */}
        <section>
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Szimulált Hibák
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <button
              onClick={simulateValidationError}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              Érvényesítési Hiba (422)
            </button>
            
            <button
              onClick={simulateUnauthorizedError}
              className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
            >
              Jogosulatlan (401)
            </button>
            
            <button
              onClick={simulateForbiddenError}
              className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
            >
              Tiltott (403)
            </button>
            
            <button
              onClick={simulateNotFoundError}
              className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
            >
              Nem található (404)
            </button>
            
            <button
              onClick={simulateServerError}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Szerver hiba (500)
            </button>
            
            <button
              onClick={simulateNetworkError}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              Hálózati hiba
            </button>
          </div>
        </section>

        {/* Real API Tests */}
        <section>
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Valós API Tesztek
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => testRealApiCall('/dashboard/stats')}
              disabled={!!loading}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Dashboard Stats (sikeres)
            </button>
            
            <button
              onClick={() => testRealApiCall('/nonexistent')}
              disabled={!!loading}
              className="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Nem létező endpoint (404)
            </button>
            
            <button
              onClick={testValidationEndpoint}
              disabled={!!loading}
              className="px-4 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Érvényesítés teszt (422)
            </button>
          </div>
        </section>

        {/* Custom Toast Messages */}
        <section>
          <h2 className="text-lg font-semibond text-gray-800 mb-4">
            Egyéni Toast Üzenetek
          </h2>
          <div className="space-y-2">
            <button
              onClick={showCustomMessages}
              className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              Mutasd az egyéni üzeneteket
            </button>
            
            <button
              onClick={() => dismiss()}
              className="ml-4 px-4 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500 transition-colors"
            >
              Összes toast elrejtése
            </button>
          </div>
        </section>

        {/* Field Error Example */}
        <section>
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Mezőszintű Hibák (Form példa)
          </h2>
          <div className="bg-white p-6 border border-gray-200 rounded-lg">
            <p className="text-sm text-gray-600 mb-4">
              Ez egy példa form, amely bemutatja hogyan jeleníthetők meg a mezőszintű hibák elegánsan.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Email cím"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Jelszó</label>
                <input
                  type="password"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Jelszó"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Név</label>
                <input
                  type="text"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Teljes név"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Instructions */}
        <section className="bg-blue-50 p-6 rounded-lg">
          <h2 className="text-lg font-semibold text-blue-800 mb-2">
            Használati Útmutató
          </h2>
          <div className="text-sm text-blue-700 space-y-2">
            <p><strong>Érvényesítési hibák:</strong> Mezőszintű hibák megjelenítése részletes üzenetekkel</p>
            <p><strong>HTTP hibák:</strong> Automatikus magyar nyelvű üzenetek státusz kód alapján</p>
            <p><strong>Hálózati hibák:</strong> Kapcsolódási problémák kezelése</p>
            <p><strong>Retry logika:</strong> Szerver hibák esetén automatikus újrapróbálkozás</p>
            <p><strong>Token frissítés:</strong> 401 hiba esetén automatikus token refresh</p>
          </div>
        </section>
      </div>
    </div>
  )
}

export default withRequiredAuth(ApiTestPage)