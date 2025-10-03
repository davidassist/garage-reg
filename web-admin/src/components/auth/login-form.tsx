'use client'

import { useState } from 'react'
import { useAuth } from '@/lib/auth/context'
import { LoginCredentials } from '@/lib/auth/types'
import { useApiErrorToast, getFieldError } from '@/lib/hooks/useApiErrorToast'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Eye, EyeOff, Lock, Mail, AlertCircle, Loader2 } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { LoginRequestSchema, ValidationApiError } from '@/lib/api/types'

import { z } from 'zod'

type LoginFormData = z.infer<typeof LoginRequestSchema>

export default function LoginForm() {
  const { login, loading, error } = useAuth()
  const { showError } = useApiErrorToast()
  const [showPassword, setShowPassword] = useState(false)
  const [validationErrors, setValidationErrors] = useState<Record<string, string[]>>({})

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(LoginRequestSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  })

  const onSubmit = async (data: LoginFormData) => {
    try {
      setValidationErrors({})
      
      const credentials: LoginCredentials = {
        email: data.email,
        password: data.password,
        rememberMe: data.rememberMe,
      }
      
      const result = await login(credentials)
      
      if (!result.success) {
        showError(new Error(result.error || 'Bejelentkezés sikertelen'))
      }
      // Success case is handled by the auth context (redirect to 2FA or dashboard)
    } catch (error) {
      console.error('Login error:', error)
      
      if (error instanceof ValidationApiError) {
        setValidationErrors(error.fieldErrors)
      } else {
        showError(error)
      }
    }
  }

  const demoCredentials = {
    email: 'admin@garagereg.com',
    password: 'password123',
  }

  const fillDemoCredentials = () => {
    const emailInput = document.getElementById('email') as HTMLInputElement
    const passwordInput = document.getElementById('password') as HTMLInputElement
    
    if (emailInput) emailInput.value = demoCredentials.email
    if (passwordInput) passwordInput.value = demoCredentials.password
  }

  const displayError = error
  
  // Helper function to get field error
  const getFieldErrorText = (field: string): string | undefined => {
    return validationErrors[field]?.[0] || errors[field as keyof LoginFormData]?.message
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-center mb-4">
            <div className="p-3 bg-blue-600 rounded-full">
              <Lock className="h-6 w-6 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center">Welcome back</CardTitle>
          <CardDescription className="text-center">
            Sign in to your GarageReg account
          </CardDescription>
        </CardHeader>
        
        <form onSubmit={handleSubmit(onSubmit)}>
          <CardContent className="space-y-4">
            {displayError && (
              <Alert variant="destructive" data-testid="error-message">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{displayError}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="email">Email cím</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  id="email"
                  type="email"
                  placeholder="Email cím megadása"
                  className={`pl-10 ${getFieldErrorText('email') ? 'border-red-500 focus:border-red-500' : ''}`}
                  {...register('email')}
                />
              </div>
              {getFieldErrorText('email') && (
                <p className="text-sm text-red-600 flex items-center">
                  <AlertCircle className="h-3 w-3 mr-1" />
                  {getFieldErrorText('email')}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Jelszó</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Jelszó megadása"
                  className={`pl-10 pr-10 ${getFieldErrorText('password') ? 'border-red-500 focus:border-red-500' : ''}`}
                  {...register('password')}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {getFieldErrorText('password') && (
                <p className="text-sm text-red-600 flex items-center">
                  <AlertCircle className="h-3 w-3 mr-1" />
                  {getFieldErrorText('password')}
                </p>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <input
                id="rememberMe"
                type="checkbox"
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                {...register('rememberMe')}
              />
              <Label htmlFor="rememberMe" className="text-sm">
                Emlékezzen rám 30 napig
              </Label>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={fillDemoCredentials}
                className="text-sm text-blue-600 hover:text-blue-800 underline"
              >
                Demo adatok használata
              </button>
            </div>
          </CardContent>

          <CardFooter className="space-y-4">
            <Button
              type="submit"
              className="w-full"
              disabled={isSubmitting || loading}
            >
              {(isSubmitting || loading) && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Bejelentkezés
            </Button>

            <div className="text-center">
              <a
                href="/forgot-password"
                className="text-sm text-blue-600 hover:text-blue-800 underline"
              >
                Elfelejtett jelszó?
              </a>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}