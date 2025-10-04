'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/components/ui/use-toast'
import { Loader2 } from 'lucide-react'

const clientSchema = z.object({
  name: z.string().min(1, 'A név megadása kötelező'),
  email: z.string().email('Érvényes email cím szükséges'),
  phone: z.string().min(1, 'A telefonszám megadása kötelező'),
  contactPerson: z.string().min(1, 'A kapcsolattartó neve kötelező'),
  taxNumber: z.string().min(1, 'Az adószám megadása kötelező'),
  address: z.string().min(1, 'A cím megadása kötelező'),
  status: z.enum(['active', 'inactive', 'suspended']),
})

type ClientFormData = z.infer<typeof clientSchema>

interface Client {
  id: string
  name: string
  email: string
  phone: string
  address: string
  contactPerson: string
  taxNumber: string
  status: 'active' | 'inactive' | 'suspended'
  sitesCount: number
  buildingsCount: number
  gatesCount: number
  createdAt: string
  updatedAt: string
}

interface ClientFormProps {
  client?: Client
  onSubmit: () => void
  onCancel: () => void
}

export function ClientForm({ client, onSubmit, onCancel }: ClientFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors }
  } = useForm<ClientFormData>({
    resolver: zodResolver(clientSchema),
    defaultValues: client ? {
      name: client.name,
      email: client.email,
      phone: client.phone,
      contactPerson: client.contactPerson,
      taxNumber: client.taxNumber,
      address: client.address,
      status: client.status,
    } : {
      status: 'active'
    }
  })

  const watchedStatus = watch('status')

  const mutation = useMutation({
    mutationFn: async (data: ClientFormData) => {
      setIsSubmitting(true)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      if (client) {
        console.log('Updating client:', client.id, data)
      } else {
        console.log('Creating client:', data)
      }
      
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] })
      toast({
        title: client ? "Ügyfél módosítva" : "Ügyfél létrehozva",
        description: client 
          ? "Az ügyfél adatai sikeresen módosítva lettek."
          : "Az új ügyfél sikeresen létrehozva lett."
      })
      onSubmit()
    },
    onError: () => {
      toast({
        title: "Hiba",
        description: "A művelet végrehajtása sikertelen.",
        variant: "destructive"
      })
    },
    onSettled: () => {
      setIsSubmitting(false)
    }
  })

  const onFormSubmit = (data: ClientFormData) => {
    mutation.mutate(data)
  }

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="name">Cég neve *</Label>
          <Input
            id="name"
            {...register('name')}
            placeholder="pl. Budapesti Városkapu Kft."
          />
          {errors.name && (
            <p className="text-sm text-red-500">{errors.name.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="taxNumber">Adószám *</Label>
          <Input
            id="taxNumber"
            {...register('taxNumber')}
            placeholder="pl. 12345678-2-41"
          />
          {errors.taxNumber && (
            <p className="text-sm text-red-500">{errors.taxNumber.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="contactPerson">Kapcsolattartó *</Label>
          <Input
            id="contactPerson"
            {...register('contactPerson')}
            placeholder="pl. Nagy Péter"
          />
          {errors.contactPerson && (
            <p className="text-sm text-red-500">{errors.contactPerson.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="status">Státusz</Label>
          <Select
            value={watchedStatus}
            onValueChange={(value: string) => setValue('status', value as 'active' | 'inactive' | 'suspended')}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="active">Aktív</SelectItem>
              <SelectItem value="inactive">Inaktív</SelectItem>
              <SelectItem value="suspended">Felfüggesztve</SelectItem>
            </SelectContent>
          </Select>
          {errors.status && (
            <p className="text-sm text-red-500">{errors.status.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="email">Email cím *</Label>
          <Input
            id="email"
            type="email"
            {...register('email')}
            placeholder="pl. info@varoskapu.hu"
          />
          {errors.email && (
            <p className="text-sm text-red-500">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="phone">Telefonszám *</Label>
          <Input
            id="phone"
            {...register('phone')}
            placeholder="pl. +36 1 234 5678"
          />
          {errors.phone && (
            <p className="text-sm text-red-500">{errors.phone.message}</p>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="address">Cím *</Label>
        <Textarea
          id="address"
          {...register('address')}
          placeholder="pl. 1011 Budapest, Fő utca 1."
          rows={3}
        />
        {errors.address && (
          <p className="text-sm text-red-500">{errors.address.message}</p>
        )}
      </div>

      <div className="flex justify-end gap-3">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Mégse
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {client ? 'Mentés' : 'Létrehozás'}
        </Button>
      </div>
    </form>
  )
}