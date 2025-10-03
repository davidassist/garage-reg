import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Building2 } from 'lucide-react'

export function BuildingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Épületek</h1>
        <p className="text-gray-600">Épületek kezelése és adminisztrációja</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Building2 className="mr-2 h-5 w-5" />
            Épületek listája
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">Az épületek funkciója fejlesztés alatt áll.</p>
        </CardContent>
      </Card>
    </div>
  )
}