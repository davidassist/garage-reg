'use client'

import { useState } from 'react'
import { useAuth } from '@/lib/auth/context'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Fingerprint, ArrowLeft, AlertCircle, Loader2, Key } from 'lucide-react'

export default function WebAuthnForm() {
  const { authenticateWebAuthn, loading, error, logout } = useAuth()
  const [webAuthnError, setWebAuthnError] = useState<string | null>(null)
  const [isAuthenticating, setIsAuthenticating] = useState(false)

  const handleWebAuthnAuth = async () => {
    try {
      setIsAuthenticating(true)
      setWebAuthnError(null)
      
      const result = await authenticateWebAuthn()
      
      if (!result.success) {
        setWebAuthnError(result.error || 'WebAuthn authentication failed')
      }
      // Success case is handled by the auth context (redirect to dashboard)
    } catch (error) {
      setWebAuthnError(error instanceof Error ? error.message : 'Authentication failed')
    } finally {
      setIsAuthenticating(false)
    }
  }

  const handleBackToLogin = () => {
    logout()
  }

  const displayError = webAuthnError || error

  const isWebAuthnSupported = typeof window !== 'undefined' && 
    window.navigator && 
    'credentials' in navigator && 
    'create' in navigator.credentials

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-center mb-4">
            <div className="p-3 bg-purple-600 rounded-full">
              <Fingerprint className="h-6 w-6 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center">Security Key Authentication</CardTitle>
          <CardDescription className="text-center">
            Use your security key or biometric authentication to continue
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {displayError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{displayError}</AlertDescription>
            </Alert>
          )}

          {!isWebAuthnSupported && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                WebAuthn is not supported in this browser. Please use a modern browser or try a different authentication method.
              </AlertDescription>
            </Alert>
          )}

          <div className="text-center space-y-4">
            <div className="p-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <Key className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-sm text-gray-600 mb-4">
                When ready, click the button below and follow your browser's prompts to authenticate with your security key or biometric device.
              </p>
              
              <div className="space-y-2 text-xs text-gray-500">
                <p>• Insert your security key (if using a hardware key)</p>
                <p>• Touch the sensor when prompted</p>
                <p>• Use your fingerprint or Face ID (if available)</p>
              </div>
            </div>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-sm">
                <strong>Having trouble?</strong><br />
                Make sure your security key is properly connected or your biometric sensor is clean and accessible.
              </AlertDescription>
            </Alert>
          </div>
        </CardContent>

        <CardFooter className="space-y-4">
          <Button
            onClick={handleWebAuthnAuth}
            className="w-full"
            disabled={isAuthenticating || loading || !isWebAuthnSupported}
          >
            {(isAuthenticating || loading) && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            <Fingerprint className="mr-2 h-4 w-4" />
            Authenticate with Security Key
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
      </Card>
    </div>
  )
}