'use client'

import { Toaster as HotToaster } from 'react-hot-toast'

/**
 * Globális Toaster komponens fejlett hibakezeléssel
 * 
 * Features:
 * - Egyedi magyar stílusok
 * - Success, error, warning színkódolás 
 * - Responsive pozicionálás
 * - Accessibility támogatás
 * - Validation error megjelenítés
 */
export function Toaster() {
  return (
    <HotToaster
      position="top-right"
      gutter={8}
      containerClassName=""
      containerStyle={{}}
      toastOptions={{
        // Globális beállítások
        duration: 5000,
        style: {
          background: '#fff',
          color: '#363636',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '12px 16px',
          fontSize: '14px',
          fontFamily: 'Inter, system-ui, sans-serif',
          maxWidth: '420px',
        },
        
        // Success toast stílus
        success: {
          duration: 4000,
          style: {
            background: '#f0fdf4',
            color: '#166534',
            border: '1px solid #bbf7d0',
          },
          iconTheme: {
            primary: '#16a34a',
            secondary: '#f0fdf4',
          },
        },
        
        // Error toast stílus
        error: {
          duration: 6000,
          style: {
            background: '#fef2f2',
            color: '#991b1b',
            border: '1px solid #fecaca',
          },
          iconTheme: {
            primary: '#dc2626',
            secondary: '#fef2f2',
          },
        },
        
        // Loading toast stílus
        loading: {
          duration: Infinity,
          style: {
            background: '#eff6ff',
            color: '#1e40af',
            border: '1px solid #dbeafe',
          },
          iconTheme: {
            primary: '#3b82f6',
            secondary: '#eff6ff',
          },
        },
      }}
    />
  )
}