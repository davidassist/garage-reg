import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { MapPin } from 'lucide-react'

export function SitesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Telephelyek</h1>
        <p className="text-gray-600">Telephelyek kezelése és adminisztrációja</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MapPin className="mr-2 h-5 w-5" />
            Telephelyek listája
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">A telephelyek funkciója fejlesztés alatt áll.</p>
        </CardContent>
      </Card>
    </div>
  )
}