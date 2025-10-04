import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/auth'
import { LoginForm } from './components/auth/LoginForm'
import { Dashboard } from './pages/Dashboard'
import { ClientsPage } from './pages/ClientsPage'
import { SitesPage } from './pages/SitesPage'
import { BuildingsPage } from './pages/BuildingsPage'
import { GatesPage } from './pages/GatesPage'
import { AuditPage } from './pages/AuditPage'
import { Layout } from './components/layout/Layout'
import { ProtectedRoute } from './components/auth/ProtectedRoute'

function App() {
  const { isAuthenticated, checkAuth, isLoading } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginForm />
  }

  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/clients/*"
            element={
              <ProtectedRoute requiredPermissions={[{ resource: 'clients', action: 'read' }]}>
                <ClientsPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/sites/*"
            element={
              <ProtectedRoute requiredPermissions={[{ resource: 'sites', action: 'read' }]}>
                <SitesPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/buildings/*"
            element={
              <ProtectedRoute requiredPermissions={[{ resource: 'buildings', action: 'read' }]}>
                <BuildingsPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/gates/*"
            element={
              <ProtectedRoute requiredPermissions={[{ resource: 'gates', action: 'read' }]}>
                <GatesPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/audit"
            element={
              <ProtectedRoute requiredPermissions={[{ resource: 'reports', action: 'read' }]}>
                <AuditPage />
              </ProtectedRoute>
            }
          />
          
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App