'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth/context'
import { TotpVerification } from '@/lib/auth/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Shield, ArrowLeft, AlertCircle, Loader2, Smartphone } from 'lucide-react'

export default function TotpForm() {
  const { verifyTotp, loading, error, logout } = useAuth()
  const [code, setCode] = useState('')
  const [trustDevice, setTrustDevice] = useState(false)
  const [totpError, setTotpError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [timeLeft, setTimeLeft] = useState(30)

  useEffect(() => {
    // TOTP codes expire every 30 seconds, show countdown
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          return 30 // Reset to 30 seconds
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (code.length !== 6) {
      setTotpError('Please enter a 6-digit code')
      return
    }

    try {
      setIsSubmitting(true)
      setTotpError(null)
      
      const verification: TotpVerification = {
        code,
        trustDevice,
      }
      
      const result = await verifyTotp(verification)
      
      if (!result.success) {
        setTotpError(result.error || 'Invalid verification code')
        setCode('') // Clear the code on error
      }
      // Success case is handled by the auth context (redirect to dashboard)
    } catch (error) {
      setTotpError(error instanceof Error ? error.message : 'Verification failed')
      setCode('')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCodeChange = (value: string) => {
    // Only allow digits and limit to 6 characters
    const sanitized = value.replace(/\D/g, '').slice(0, 6)
    setCode(sanitized)
    
    // Clear error when user starts typing
    if (totpError) {
      setTotpError(null)
    }
  }

  const handleBackToLogin = () => {
    logout()
  }

  const displayError = totpError || error

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-center mb-4">
            <div className="p-3 bg-green-600 rounded-full">
              <Shield className="h-6 w-6 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center">Two-Factor Authentication</CardTitle>
          <CardDescription className="text-center">
            Enter the 6-digit code from your authenticator app
          </CardDescription>
        </CardHeader>
        
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {displayError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{displayError}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Smartphone className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Verification Code</span>
                </div>
                <div className="text-xs text-gray-500">
                  Refreshes in {timeLeft}s
                </div>
              </div>
              
              <Input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                placeholder="000000"
                value={code}
                onChange={(e) => handleCodeChange(e.target.value)}
                className="text-center text-2xl font-mono tracking-wider"
                maxLength={6}
                autoComplete="one-time-code"
                autoFocus
              />
              
              <p className="text-xs text-gray-500 text-center">
                Open your authenticator app and enter the current 6-digit code
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <input
                id="trustDevice"
                type="checkbox"
                checked={trustDevice}
                onChange={(e) => setTrustDevice(e.target.checked)}
                className="rounded border-gray-300 text-green-600 shadow-sm focus:border-green-300 focus:ring focus:ring-green-200 focus:ring-opacity-50"
              />
              <label htmlFor="trustDevice" className="text-sm">
                Trust this device for 30 days
              </label>
            </div>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-sm">
                <strong>Can't access your authenticator?</strong><br />
                Contact your administrator or use a backup code if available.
              </AlertDescription>
            </Alert>
          </CardContent>

          <CardFooter className="space-y-4">
            <Button
              type="submit"
              className="w-full"
              disabled={isSubmitting || loading || code.length !== 6}
            >
              {(isSubmitting || loading) && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Verify Code
            </Button>

            <Button
              type="button"
              variant="ghost"
              onClick={handleBackToLogin}
              className="w-full"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Login
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}