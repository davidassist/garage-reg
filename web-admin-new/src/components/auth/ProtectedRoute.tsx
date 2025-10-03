import { ReactNode } from 'react'
import { useAuthStore } from '@/stores/auth'
import { usePermissions, type PermissionCheck } from '@/hooks/permissions'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ShieldAlert } from 'lucide-react'

interface ProtectedRouteProps {
  children: ReactNode
  requiredPermissions?: PermissionCheck[]
  requireAll?: boolean // If true, user must have ALL permissions. If false, user needs ANY permission
}

export function ProtectedRoute({ 
  children, 
  requiredPermissions = [],
  requireAll = false 
}: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuthStore()
  const { hasAllPermissions, hasAnyPermission } = usePermissions()

  // Not authenticated
  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Bejelentkezés szükséges
          </h1>
          <p className="text-gray-600 mb-4">
            A tartalom megtekintéséhez be kell jelentkeznie.
          </p>
          <Button onClick={() => window.location.reload()}>
            Bejelentkezés
          </Button>
        </div>
      </div>
    )
  }

  // Check permissions if required
  if (requiredPermissions.length > 0) {
    const hasPermission = requireAll 
      ? hasAllPermissions(requiredPermissions)
      : hasAnyPermission(requiredPermissions)

    if (!hasPermission) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <div className="max-w-md w-full">
            <Alert variant="destructive">
              <ShieldAlert className="h-4 w-4" />
              <AlertDescription>
                <div className="mt-2">
                  <h4 className="font-semibold mb-2">Nincs jogosultsága</h4>
                  <p className="text-sm">
                    Nincs megfelelő jogosultsága az oldal megtekintéséhez. 
                    Lépjen kapcsolatba a rendszer adminisztrátorával.
                  </p>
                  <div className="mt-4">
                    <Button 
                      variant="outline" 
                      onClick={() => window.history.back()}
                      className="mr-2"
                    >
                      Vissza
                    </Button>
                    <Button onClick={() => window.location.href = '/dashboard'}>
                      Dashboard
                    </Button>
                  </div>
                </div>
              </AlertDescription>
            </Alert>
          </div>
        </div>
      )
    }
  }

  // All checks passed, render children
  return <>{children}</>
}