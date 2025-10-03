'use client'

import { useAuth } from '@/lib/auth/context'
import { AuthStep } from '@/lib/auth/types'
import LoginForm from '@/components/auth/login-form'
import TotpForm from '@/components/auth/totp-form'
import WebAuthnForm from '@/components/auth/webauthn-form'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const { step, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  if (isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Redirecting...</p>
        </div>
      </div>
    )
  }

  switch (step) {
    case AuthStep.TOTP:
      return <TotpForm />
    case AuthStep.WEBAUTHN:
      return <WebAuthnForm />
    case AuthStep.LOGIN:
    default:
      return <LoginForm />
  }
}