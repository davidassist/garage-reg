'use client'

import { useRouter } from 'next/navigation'
import { GateForm } from '@/components/forms/gate-form'
import { toast } from '@/components/ui/use-toast'
import { Gate } from '@/lib/api/types'

export default function CreateGatePage({ 
  searchParams 
}: { 
  searchParams: { siteId?: string } 
}) {
  const router = useRouter()

  const handleSuccess = (gate: Gate) => {
    toast({
      title: "Kapu létrehozva",
      description: `${gate.name} sikeresen létrehozva.`,
    })
    router.push(`/gates/${gate.id}`)
  }

  const handleCancel = () => {
    router.push('/gates')
  }

  return (
    <GateForm 
      siteId={searchParams.siteId}
      onSuccess={handleSuccess}
      onCancel={handleCancel}
    />
  )
}