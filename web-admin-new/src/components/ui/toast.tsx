/**
 * Toast Notification System
 * Displays user-friendly error and success messages
 */

import { useState, useEffect, useCallback } from 'react'

// Toast types and interfaces
export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  type: ToastType
  title: string
  message: string
  details?: string
  dismissible: boolean
  autoHide: boolean
  duration?: number
  timestamp: Date
  action?: {
    label: string
    onClick: () => void
  }
}

export interface ToastOptions {
  type?: ToastType
  title?: string
  dismissible?: boolean
  autoHide?: boolean
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}

// Toast context and provider
interface ToastContextValue {
  toasts: Toast[]
  showToast: (message: string, options?: ToastOptions) => string
  showSuccess: (message: string, options?: Omit<ToastOptions, 'type'>) => string
  showError: (message: string, options?: Omit<ToastOptions, 'type'>) => string
  showWarning: (message: string, options?: Omit<ToastOptions, 'type'>) => string
  showInfo: (message: string, options?: Omit<ToastOptions, 'type'>) => string
  dismissToast: (id: string) => void
  clearAllToasts: () => void
}

// Default toast options
const defaultToastOptions: Required<Omit<ToastOptions, 'action'>> = {
  type: 'info',
  title: '',
  dismissible: true,
  autoHide: true,
  duration: 5000
}

// Toast type configurations
const toastTypeConfig: Record<ToastType, { icon: string; bgColor: string; textColor: string; borderColor: string }> = {
  success: {
    icon: '✅',
    bgColor: 'bg-green-50',
    textColor: 'text-green-800',
    borderColor: 'border-green-200'
  },
  error: {
    icon: '❌',
    bgColor: 'bg-red-50',
    textColor: 'text-red-800',
    borderColor: 'border-red-200'
  },
  warning: {
    icon: '⚠️',
    bgColor: 'bg-yellow-50',
    textColor: 'text-yellow-800',
    borderColor: 'border-yellow-200'
  },
  info: {
    icon: 'ℹ️',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-200'
  }
}

// Toast hook for managing toast state
export function useToasts(): ToastContextValue {
  const [toasts, setToasts] = useState<Toast[]>([])

  // Generate unique toast ID
  const generateToastId = useCallback((): string => {
    return `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }, [])

  // Show toast with options
  const showToast = useCallback((message: string, options: ToastOptions = {}): string => {
    const toastOptions = { ...defaultToastOptions, ...options }
    const id = generateToastId()
    
    const newToast: Toast = {
      id,
      type: toastOptions.type,
      title: toastOptions.title,
      message,
      dismissible: toastOptions.dismissible,
      autoHide: toastOptions.autoHide,
      duration: toastOptions.duration,
      timestamp: new Date(),
      action: options.action
    }

    setToasts(prev => [...prev, newToast])

    // Auto-remove toast if configured
    if (newToast.autoHide && newToast.duration) {
      setTimeout(() => {
        dismissToast(id)
      }, newToast.duration)
    }

    return id
  }, [generateToastId])

  // Convenience methods for different toast types
  const showSuccess = useCallback((message: string, options: Omit<ToastOptions, 'type'> = {}): string => {
    return showToast(message, { ...options, type: 'success' })
  }, [showToast])

  const showError = useCallback((message: string, options: Omit<ToastOptions, 'type'> = {}): string => {
    return showToast(message, { ...options, type: 'error', autoHide: false })
  }, [showToast])

  const showWarning = useCallback((message: string, options: Omit<ToastOptions, 'type'> = {}): string => {
    return showToast(message, { ...options, type: 'warning' })
  }, [showToast])

  const showInfo = useCallback((message: string, options: Omit<ToastOptions, 'type'> = {}): string => {
    return showToast(message, { ...options, type: 'info' })
  }, [showToast])

  // Dismiss specific toast
  const dismissToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  // Clear all toasts
  const clearAllToasts = useCallback(() => {
    setToasts([])
  }, [])

  // Listen for global error events from error handler
  useEffect(() => {
    const handleErrorToast = (event: CustomEvent) => {
      const error = event.detail
      showError(error.message, {
        title: error.title,
        details: error.details,
        dismissible: error.dismissible,
        autoHide: error.autoHide,
        duration: error.duration
      })
    }

    window.addEventListener('show-error-toast', handleErrorToast as EventListener)
    
    return () => {
      window.removeEventListener('show-error-toast', handleErrorToast as EventListener)
    }
  }, [showError])

  return {
    toasts,
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    dismissToast,
    clearAllToasts
  }
}

// Individual Toast Component
interface ToastComponentProps {
  toast: Toast
  onDismiss: (id: string) => void
}

export function ToastComponent({ toast, onDismiss }: ToastComponentProps) {
  const config = toastTypeConfig[toast.type]
  
  const handleDismiss = () => {
    onDismiss(toast.id)
  }

  const handleAction = () => {
    if (toast.action) {
      toast.action.onClick()
      handleDismiss()
    }
  }

  return (
    <div className={`
      relative p-4 rounded-lg border-l-4 shadow-lg
      ${config.bgColor} ${config.textColor} ${config.borderColor}
      animate-slide-in-right
    `}>
      <div className="flex items-start gap-3">
        {/* Icon */}
        <span className="text-lg flex-shrink-0 mt-0.5">
          {config.icon}
        </span>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          {toast.title && (
            <h4 className="font-semibold text-sm mb-1">
              {toast.title}
            </h4>
          )}
          
          <p className="text-sm">
            {toast.message}
          </p>
          
          {toast.details && (
            <p className="text-xs opacity-75 mt-1">
              {toast.details}
            </p>
          )}
          
          {toast.action && (
            <button
              onClick={handleAction}
              className="mt-2 text-xs font-medium underline hover:no-underline"
            >
              {toast.action.label}
            </button>
          )}
        </div>

        {/* Dismiss button */}
        {toast.dismissible && (
          <button
            onClick={handleDismiss}
            className="flex-shrink-0 p-1 hover:bg-black/10 rounded"
            aria-label="Dismiss notification"
          >
            <span className="text-lg">×</span>
          </button>
        )}
      </div>

      {/* Progress bar for auto-hide toasts */}
      {toast.autoHide && toast.duration && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/10 rounded-b-lg overflow-hidden">
          <div 
            className="h-full bg-current opacity-30 animate-progress"
            style={{
              animationDuration: `${toast.duration}ms`
            }}
          />
        </div>
      )}
    </div>
  )
}

// Toast Container Component
interface ToastContainerProps {
  toasts: Toast[]
  onDismiss: (id: string) => void
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'
  maxToasts?: number
}

export function ToastContainer({ 
  toasts, 
  onDismiss, 
  position = 'top-right',
  maxToasts = 5 
}: ToastContainerProps) {
  // Limit number of visible toasts
  const visibleToasts = toasts.slice(-maxToasts)

  // Position classes
  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2'
  }

  if (visibleToasts.length === 0) {
    return null
  }

  return (
    <div className={`fixed z-50 ${positionClasses[position]} space-y-2`}>
      {visibleToasts.map(toast => (
        <ToastComponent
          key={toast.id}
          toast={toast}
          onDismiss={onDismiss}
        />
      ))}
    </div>
  )
}

// Toast Provider Component
interface ToastProviderProps {
  children: React.ReactNode
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'
  maxToasts?: number
}

export function ToastProvider({ children, position = 'top-right', maxToasts = 5 }: ToastProviderProps) {
  const { toasts, dismissToast } = useToasts()

  return (
    <>
      {children}
      <ToastContainer
        toasts={toasts}
        onDismiss={dismissToast}
        position={position}
        maxToasts={maxToasts}
      />
    </>
  )
}

// Export the custom CSS needed for animations
export const toastCSS = `
  @keyframes slide-in-right {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes progress {
    from {
      transform: scaleX(0);
    }
    to {
      transform: scaleX(1);
    }
  }

  .animate-slide-in-right {
    animation: slide-in-right 0.3s ease-out;
  }

  .animate-progress {
    animation: progress linear;
    transform-origin: left;
  }
`