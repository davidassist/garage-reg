import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          {/* 404 Icon */}
          <div className="mx-auto h-16 w-16 bg-primary-100 rounded-lg flex items-center justify-center mb-6">
            <svg
              className="h-8 w-8 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-3-3v3m0 6h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          {/* 404 Message */}
          <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
          
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Page Not Found
          </h2>
          
          <p className="text-lg text-gray-600 mb-8">
            The page you're looking for doesn't exist or has been moved.
          </p>

          {/* Navigation Options */}
          <div className="space-y-4">
            <Link href="/dashboard">
              <Button className="w-full">
                Go to Dashboard
              </Button>
            </Link>
            
            <Link href="/login">
              <Button variant="outline" className="w-full">
                Go to Login
              </Button>
            </Link>
            
            <Button
              variant="ghost"
              onClick={() => window.history.back()}
              className="w-full text-sm"
            >
              Go Back
            </Button>
          </div>

          {/* Popular Pages */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-800 mb-3">
              Popular Pages
            </h3>
            <div className="space-y-2 text-sm">
              <Link
                href="/vehicles"
                className="block text-primary-600 hover:text-primary-500"
              >
                Vehicle Management
              </Link>
              <Link
                href="/registrations"
                className="block text-primary-600 hover:text-primary-500"
              >
                Registration Management
              </Link>
              <Link
                href="/users"
                className="block text-primary-600 hover:text-primary-500"
              >
                User Management
              </Link>
              <Link
                href="/analytics"
                className="block text-primary-600 hover:text-primary-500"
              >
                Analytics & Reports
              </Link>
            </div>
          </div>

          {/* Search Suggestion */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Looking for something specific?{' '}
              <Link
                href="/search"
                className="text-primary-600 hover:text-primary-500 font-medium"
              >
                Try searching
              </Link>
              {' '}or{' '}
              <a
                href="mailto:support@garagereg.com"
                className="text-primary-600 hover:text-primary-500 font-medium"
              >
                contact support
              </a>
              .
            </p>
          </div>
        </div>
      </div>

      {/* Background Pattern */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-[50%] top-[50%] -translate-x-[50%] -translate-y-[50%] w-[200%] h-[200%] bg-gradient-to-br from-gray-50 via-white to-gray-100 opacity-50" />
        <div className="absolute left-[20%] top-[30%] w-32 h-32 bg-primary-100 rounded-full opacity-30 animate-bounce" style={{ animationDelay: '0s', animationDuration: '3s' }} />
        <div className="absolute right-[30%] top-[20%] w-24 h-24 bg-secondary-100 rounded-full opacity-30 animate-bounce" style={{ animationDelay: '1s', animationDuration: '4s' }} />
        <div className="absolute left-[70%] bottom-[40%] w-16 h-16 bg-primary-200 rounded-full opacity-40 animate-bounce" style={{ animationDelay: '2s', animationDuration: '5s' }} />
      </div>
    </div>
  )
}