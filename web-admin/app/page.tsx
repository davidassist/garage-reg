import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🏠 Garage Registry System
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Komplex garázskezelő rendszer dinamikus űrlapokkal, fotófeltöltéssel,
            címkegenerálással és fejlett analitikákkal.
          </p>
        </div>

        {/* Main Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {/* Photo Upload System */}
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-3xl mb-4">📤</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Fotó Rendszer
            </h3>
            <p className="text-gray-600 mb-4">
              Drag & drop feltöltő, presigned URL-ek, többszálú feltöltés,
              EXIF adatok, GPS koordináták.
            </p>
            <div className="space-y-2">
              <Link
                href="/photo-upload-demo"
                className="block w-full px-4 py-2 text-sm font-medium text-blue-700 
                         bg-blue-50 rounded-md hover:bg-blue-100 transition-colors
                         text-center"
              >
                Teljes Demo
              </Link>
              <Link
                href="/photo-test"
                className="block w-full px-4 py-2 text-sm font-medium text-green-700 
                         bg-green-50 rounded-md hover:bg-green-100 transition-colors
                         text-center"
              >
                Egyszerű Teszt
              </Link>
            </div>
          </div>

          {/* Dynamic Forms */}
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-3xl mb-4">📋</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Dinamikus Űrlapok
            </h3>
            <p className="text-gray-600 mb-4">
              5 komponens típus: BoolSwitch, Enum, NumberRange, Photo, Note
              feltételes logikával.
            </p>
            <Link
              href="/dynamic-forms"
              className="block w-full px-4 py-2 text-sm font-medium text-purple-700 
                       bg-purple-50 rounded-md hover:bg-purple-100 transition-colors
                       text-center"
            >
              Form Builder
            </Link>
          </div>

          {/* Inspection System */}
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-3xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Ellenőrzési Rendszer
            </h3>
            <p className="text-gray-600 mb-4">
              Teljes folyamat: indítás → kitöltés → lezárás. Élő mentés,
              állapot helyreállítás, unsaved changes.
            </p>
            <Link
              href="/inspection-demo"
              className="block w-full px-4 py-2 text-sm font-medium text-teal-700 
                       bg-teal-50 rounded-md hover:bg-teal-100 transition-colors
                       text-center"
            >
              Ellenőrzés Demo
            </Link>
          </div>

          {/* Gate Details */}
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-3xl mb-4">🚪</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Kapu Részletek
            </h3>
            <p className="text-gray-600 mb-4">
              5 tab-os részletes nézet: Alapadatok, Karbantartás, Dokumentumok, 
              Fényképek, Előzmények.
            </p>
            <Link
              href="/gates/1"
              className="block w-full px-4 py-2 text-sm font-medium text-indigo-700 
                       bg-indigo-50 rounded-md hover:bg-indigo-100 transition-colors
                       text-center"
            >
              Kapu Részletek
            </Link>
          </div>

          {/* Labels */}
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-3xl mb-4">🏷️</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Címke Rendszer
            </h3>
            <p className="text-gray-600 mb-4">
              QR kódos címkék generálása A4 formátumban, nyomtatási 
              optimalizációval.
            </p>
            <Link
              href="/labels"
              className="block w-full px-4 py-2 text-sm font-medium text-orange-700 
                       bg-orange-50 rounded-md hover:bg-orange-100 transition-colors
                       text-center"
            >
              Címke Generátor
            </Link>
          </div>

          {/* Analytics */}
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-3xl mb-4">📊</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Analitika
            </h3>
            <p className="text-gray-600 mb-4">
              Garázsok, kapuk, karbantartások és dokumentumok részletes 
              elemzése grafikonokkal.
            </p>
            <Link
              href="/analytics"
              className="block w-full px-4 py-2 text-sm font-medium text-red-700 
                       bg-red-50 rounded-md hover:bg-red-100 transition-colors
                       text-center"
            >
              Analitikai Nézet
            </Link>
          </div>

          {/* API Documentation */}
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-3xl mb-4">🔧</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              API Dokumentáció
            </h3>
            <p className="text-gray-600 mb-4">
              OpenAPI 3.0 specifikáció, endpoint leírások, 
              példák és típusdefiníciók.
            </p>
            <Link
              href="/api-docs"
              className="block w-full px-4 py-2 text-sm font-medium text-gray-700 
                       bg-gray-50 rounded-md hover:bg-gray-100 transition-colors
                       text-center"
            >
              API Docs
            </Link>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🟢 Rendszer Állapot
          </h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Implementált Funkciók:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>✅ Kapu részletes nézet (5 tab)</li>
                <li>✅ Dinamikus űrlap motor (5 komponens típus)</li>
                <li>✅ Fotófeltöltő rendszer (presigned URL)</li>
                <li>✅ EXIF adatok kinyerése (GPS, kamera)</li>
                <li>✅ Többszálú feltöltés (resumable)</li>
                <li>✅ Lightbox galéria (zoom, rotate)</li>
                <li>✅ Ellenőrzési rendszer (start → fill → close)</li>
                <li>✅ Auto-save & unsaved changes warning</li>
                <li>✅ QR címke generátor (A4 optimalizált)</li>
                <li>✅ Analitikai dashboard</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Technológiai Stack:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>🔹 Next.js 14 (App Router)</li>
                <li>🔹 TypeScript + Zod validáció</li>
                <li>🔹 Tailwind CSS styling</li>
                <li>🔹 AWS S3 kompatibilis upload</li>
                <li>🔹 TIFF EXIF parser</li>
                <li>🔹 Multi-threading upload</li>
                <li>🔹 Real-time progress tracking</li>
                <li>🔹 Responsive design</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-8 text-center text-gray-500">
          <p className="text-sm">
            🚀 Fejlett garázskezelés • 📱 Reszponzív design • ⚡ 60 FPS teljesítmény
          </p>
        </div>
      </div>
    </div>
  )
}