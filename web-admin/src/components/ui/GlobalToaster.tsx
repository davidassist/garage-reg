'use client'

import { Toaster } from 'react-hot-toast'

interface GlobalToasterProps {
  position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right'
}

export function GlobalToaster({ position = 'top-right' }: GlobalToasterProps) {
  return (
    <Toaster
      position={position}
      toastOptions={{
        // Default options for all toasts
        duration: 5000,
        style: {
          background: '#363636',
          color: '#fff',
          fontSize: '14px',
          fontWeight: '500',
          borderRadius: '8px',
          padding: '12px 16px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          maxWidth: '500px',
        },
        
        // Success toasts
        success: {
          duration: 4000,
          style: {
            background: '#10B981',
            color: '#fff',
          },
          iconTheme: {
            primary: '#fff',
            secondary: '#10B981',
          },
        },
        
        // Error toasts
        error: {
          duration: 6000,
          style: {
            background: '#EF4444',
            color: '#fff',
          },
          iconTheme: {
            primary: '#fff',
            secondary: '#EF4444',
          },
        },
        
        // Loading toasts
        loading: {
          duration: Infinity,
          style: {
            background: '#6B7280',
            color: '#fff',
          },
        },
      }}
      containerStyle={{
        top: 20,
        left: 20,
        bottom: 20,
        right: 20,
      }}
      gutter={8}
    />
  )
}

export default GlobalToaster