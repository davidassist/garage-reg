'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

interface ErrorProps {
  error: Error & { digest?: string }
  reset: () => void
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error)
    
    // You can add error reporting service here
    // Example: Sentry.captureException(error)
  }, [error])

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          {/* Error Icon */}
          <div className="mx-auto h-16 w-16 bg-red-100 rounded-lg flex items-center justify-center mb-6">
            <svg
              className="h-8 w-8 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          {/* Error Message */}
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Something went wrong
          </h1>
          
          <p className="text-lg text-gray-600 mb-8">
            We encountered an unexpected error. Our team has been notified and is working to fix this.
          </p>

          {/* Error Details (Development Only) */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg text-left">
              <h3 className="text-sm font-medium text-red-800 mb-2">
                Development Error Details:
              </h3>
              <pre className="text-xs text-red-700 whitespace-pre-wrap break-words">
                {error.message}
              </pre>
              {error.digest && (
                <p className="text-xs text-red-600 mt-2">
                  Error ID: {error.digest}
                </p>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="space-y-4">
            <Button
              onClick={reset}
              className="w-full"
            >
              Try Again
            </Button>
            
            <Button
              variant="outline"
              onClick={() => window.location.href = '/dashboard'}
              className="w-full"
            >
              Return to Dashboard
            </Button>
            
            <Button
              variant="ghost"
              onClick={() => window.location.reload()}
              className="w-full text-sm"
            >
              Reload Page
            </Button>
          </div>

          {/* Support Information */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              If this problem persists, please contact{' '}
              <a
                href="mailto:support@garagereg.com"
                className="text-primary-600 hover:text-primary-500 font-medium"
              >
                technical support
              </a>
              {' '}with the error details above.
            </p>
          </div>
        </div>
      </div>

      {/* Background Pattern */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-[50%] top-[50%] -translate-x-[50%] -translate-y-[50%] w-[200%] h-[200%] bg-gradient-to-br from-gray-50 via-white to-gray-100 opacity-50" />
        <div className="absolute left-[25%] top-[25%] w-64 h-64 bg-primary-100 rounded-full opacity-20 animate-pulse" />
        <div className="absolute right-[25%] bottom-[25%] w-48 h-48 bg-secondary-100 rounded-full opacity-20 animate-pulse" style={{ animationDelay: '1s' }} />
      </div>
    </div>
  )
}