'use client'

import React, { useEffect, useState, useCallback } from 'react'
import { AlertTriangle, Save, X, RotateCcw } from 'lucide-react'
import { useRouter, usePathname } from 'next/navigation'

interface UnsavedChangesWarningProps {
  hasUnsavedChanges: boolean
  onSave?: () => Promise<void>
  onDiscard?: () => void
  saveLabel?: string
  message?: string
  className?: string
}

export function UnsavedChangesWarning({
  hasUnsavedChanges,
  onSave,
  onDiscard,
  saveLabel = 'Mentés',
  message = 'Nem mentett változások vannak. Biztosan el szeretnéd hagyni az oldalt?',
  className = ''
}: UnsavedChangesWarningProps) {
  const [showWarning, setShowWarning] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [pendingNavigation, setPendingNavigation] = useState<string | null>(null)
  const router = useRouter()
  const pathname = usePathname()

  // Browser beforeunload event
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault()
        e.returnValue = message
        return message
      }
    }

    if (hasUnsavedChanges) {
      window.addEventListener('beforeunload', handleBeforeUnload)
    }

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [hasUnsavedChanges, message])

  // Navigation interception
  useEffect(() => {
    const originalPush = router.push
    const originalBack = router.back
    const originalForward = router.forward

    if (hasUnsavedChanges) {
      // Override router methods
      router.push = (href: string) => {
        if (pathname !== href) {
          setPendingNavigation(href)
          setShowWarning(true)
          return Promise.resolve(true)
        }
        return originalPush(href)
      }

      router.back = () => {
        setPendingNavigation('back')
        setShowWarning(true)
      }

      router.forward = () => {
        setPendingNavigation('forward')  
        setShowWarning(true)
      }
    } else {
      // Restore original methods
      router.push = originalPush
      router.back = originalBack
      router.forward = originalForward
    }

    return () => {
      router.push = originalPush
      router.back = originalBack
      router.forward = originalForward
    }
  }, [hasUnsavedChanges, router, pathname])

  const handleSaveAndContinue = useCallback(async () => {
    if (onSave) {
      try {
        setIsSaving(true)
        await onSave()
        
        // Navigate after successful save
        if (pendingNavigation) {
          if (pendingNavigation === 'back') {
            window.history.back()
          } else if (pendingNavigation === 'forward') {
            window.history.forward()
          } else {
            window.location.href = pendingNavigation
          }
        }
        
        setShowWarning(false)
        setPendingNavigation(null)
      } catch (error) {
        console.error('Save failed:', error)
        // Keep warning open on error
      } finally {
        setIsSaving(false)
      }
    }
  }, [onSave, pendingNavigation])

  const handleDiscardAndContinue = useCallback(() => {
    if (onDiscard) {
      onDiscard()
    }

    // Navigate after discarding
    if (pendingNavigation) {
      if (pendingNavigation === 'back') {
        window.history.back()
      } else if (pendingNavigation === 'forward') {
        window.history.forward()
      } else {
        window.location.href = pendingNavigation
      }
    }
    
    setShowWarning(false)
    setPendingNavigation(null)
  }, [onDiscard, pendingNavigation])

  const handleCancel = useCallback(() => {
    setShowWarning(false)
    setPendingNavigation(null)
  }, [])

  if (!showWarning || !hasUnsavedChanges) return null

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        {/* Warning Dialog */}
        <div className={`bg-white rounded-lg shadow-xl max-w-md w-full ${className}`}>
          {/* Header */}
          <div className="flex items-center space-x-3 p-6 border-b">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-orange-600" />
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Nem mentett változások
              </h3>
              <p className="text-sm text-gray-600">
                Mentés nélkül elveszhetnek az adatok
              </p>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            <p className="text-gray-700 mb-4">{message}</p>
            
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <div className="flex items-start space-x-2">
                <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5" />
                <div className="text-sm">
                  <p className="text-yellow-800 font-medium">Mit szeretnél tenni?</p>
                  <ul className="text-yellow-700 mt-1 space-y-1">
                    <li>• <strong>Mentés és folytatás:</strong> Adatok mentése, majd navigáció</li>
                    <li>• <strong>Elvetés:</strong> Változások elvesztése, azonnali navigáció</li>
                    <li>• <strong>Mégsem:</strong> Maradás az aktuális oldalon</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 p-6 border-t bg-gray-50">
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border 
                       border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Mégsem
            </button>
            
            <button
              onClick={handleDiscardAndContinue}
              className="px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border 
                       border-red-300 rounded-md hover:bg-red-100 transition-colors 
                       flex items-center space-x-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Elvetés</span>
            </button>
            
            {onSave && (
              <button
                onClick={handleSaveAndContinue}
                disabled={isSaving}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors 
                         flex items-center space-x-2 ${
                  isSaving
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isSaving ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                <span>{isSaving ? 'Mentés...' : saveLabel}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

// Hook for managing unsaved changes state
export function useUnsavedChanges() {
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [changedFields, setChangedFields] = useState<string[]>([])
  const [lastChangeAt, setLastChangeAt] = useState<Date | null>(null)

  const markAsChanged = useCallback((fieldId?: string) => {
    setHasUnsavedChanges(true)
    setLastChangeAt(new Date())
    
    if (fieldId && !changedFields.includes(fieldId)) {
      setChangedFields(prev => [...prev, fieldId])
    }
  }, [changedFields])

  const markAsSaved = useCallback(() => {
    setHasUnsavedChanges(false)
    setChangedFields([])
    setLastChangeAt(null)
  }, [])

  const discardChanges = useCallback(() => {
    setHasUnsavedChanges(false)
    setChangedFields([])
    setLastChangeAt(null)
  }, [])

  return {
    hasUnsavedChanges,
    changedFields,
    lastChangeAt,
    markAsChanged,
    markAsSaved,
    discardChanges
  }
}

// Enhanced version with local storage backup
interface UnsavedChangesWithBackupProps extends UnsavedChangesWarningProps {
  backupKey?: string
  formData?: any
  onRestore?: (data: any) => void
}

export function UnsavedChangesWithBackup({
  backupKey,
  formData,
  onRestore,
  ...props
}: UnsavedChangesWithBackupProps) {
  const [hasBackup, setHasBackup] = useState(false)

  // Check for existing backup on mount
  useEffect(() => {
    if (backupKey) {
      const backup = localStorage.getItem(`unsaved-${backupKey}`)
      setHasBackup(!!backup)
    }
  }, [backupKey])

  // Save to backup when changes occur
  useEffect(() => {
    if (props.hasUnsavedChanges && backupKey && formData) {
      const backup = {
        data: formData,
        timestamp: new Date().toISOString(),
        version: '1.0'
      }
      localStorage.setItem(`unsaved-${backupKey}`, JSON.stringify(backup))
    }
  }, [props.hasUnsavedChanges, backupKey, formData])

  // Clear backup when saved
  const handleSave = async () => {
    if (props.onSave) {
      await props.onSave()
      if (backupKey) {
        localStorage.removeItem(`unsaved-${backupKey}`)
        setHasBackup(false)
      }
    }
  }

  // Clear backup when discarded
  const handleDiscard = () => {
    if (props.onDiscard) {
      props.onDiscard()
    }
    if (backupKey) {
      localStorage.removeItem(`unsaved-${backupKey}`)
      setHasBackup(false)
    }
  }

  // Restore from backup
  const handleRestore = () => {
    if (backupKey && onRestore) {
      const backup = localStorage.getItem(`unsaved-${backupKey}`)
      if (backup) {
        try {
          const parsed = JSON.parse(backup)
          onRestore(parsed.data)
          setHasBackup(false)
        } catch (error) {
          console.error('Failed to restore backup:', error)
        }
      }
    }
  }

  return (
    <>
      {/* Backup Restore Notification */}
      {hasBackup && !props.hasUnsavedChanges && (
        <div className="fixed top-4 right-4 bg-blue-50 border border-blue-200 rounded-lg p-4 shadow-lg z-40">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <RotateCcw className="w-4 h-4 text-blue-600" />
            </div>
            
            <div className="flex-1">
              <h4 className="font-medium text-blue-900">Helyreállítható adatok</h4>
              <p className="text-sm text-blue-700 mt-1">
                Van egy mentett munkamenet, amit helyreállíthatsz.
              </p>
              
              <div className="flex items-center space-x-2 mt-3">
                <button
                  onClick={handleRestore}
                  className="px-3 py-1 text-sm font-medium text-blue-700 bg-blue-100 
                           rounded hover:bg-blue-200 transition-colors"
                >
                  Helyreállítás
                </button>
                <button
                  onClick={() => {
                    if (backupKey) {
                      localStorage.removeItem(`unsaved-${backupKey}`)
                      setHasBackup(false)
                    }
                  }}
                  className="px-3 py-1 text-sm font-medium text-gray-600 hover:text-gray-800 
                           transition-colors"
                >
                  Elvetés
                </button>
              </div>
            </div>
            
            <button
              onClick={() => setHasBackup(false)}
              className="p-1 text-blue-400 hover:text-blue-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Main Warning */}
      <UnsavedChangesWarning
        {...props}
        onSave={handleSave}
        onDiscard={handleDiscard}
      />
    </>
  )
}