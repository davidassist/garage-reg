import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DoorOpen } from 'lucide-react'

export function GatesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Kapuk</h1>
        <p className="text-gray-600">Kapuk kezelése és adminisztrációja</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <DoorOpen className="mr-2 h-5 w-5" />
            Kapuk listája
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">A kapuk funkciója fejlesztés alatt áll.</p>
        </CardContent>
      </Card>
    </div>
  )
}