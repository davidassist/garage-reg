'use client'

import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { GateForm } from '@/components/forms/gate-form'
import { toast } from '@/components/ui/use-toast'
import { Gate } from '@/lib/api/types'
import { apiClient } from '@/lib/api/client'

export default function EditGatePage({ 
  params 
}: { 
  params: { id: string } 
}) {
  const router = useRouter()

  const { data: gate, isLoading, error } = useQuery({
    queryKey: ['gate', params.id],
    queryFn: () => apiClient.getGate(params.id),
  })

  const handleSuccess = (gate: Gate) => {
    toast({
      title: "Kapu módosítva",
      description: `${gate.name} adatai sikeresen frissítve.`,
    })
    router.push(`/gates/${gate.id}`)
  }

  const handleCancel = () => {
    router.push(`/gates/${params.id}`)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground mt-2">Adatok betöltése...</p>
        </div>
      </div>
    )
  }

  if (error || !gate) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <h3 className="text-lg font-semibold">Hiba történt</h3>
          <p className="text-muted-foreground">A kapu adatai nem tölthetők be.</p>
        </div>
      </div>
    )
  }

  return (
    <GateForm 
      gate={gate as Gate}
      onSuccess={handleSuccess}
      onCancel={handleCancel}
    />
  )
}