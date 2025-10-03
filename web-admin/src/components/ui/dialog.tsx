import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { X } from "lucide-react"
import { cn } from "@/lib/ui/utils"

/**
 * Dialog component built with Radix UI Dialog primitive
 * Includes overlay, content, header, footer, and accessibility features
 */

// Dialog root component
const Dialog = DialogPrimitive.Root

// Dialog trigger button
const DialogTrigger = DialogPrimitive.Trigger

// Dialog portal for rendering outside DOM tree
const DialogPortal = DialogPrimitive.Portal

// Dialog close button
const DialogClose = DialogPrimitive.Close

// Dialog overlay/backdrop
const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      "fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

// Dialog content container
const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content> & {
    /**
     * Dialog size variant
     * @default "md"
     */
    size?: "sm" | "md" | "lg" | "xl" | "full"
    
    /**
     * Whether to show the close button
     * @default true
     */
    showClose?: boolean
  }
>(({ className, children, size = "md", showClose = true, ...props }, ref) => {
  const sizeClasses = {
    sm: "max-w-md",
    md: "max-w-lg", 
    lg: "max-w-2xl",
    xl: "max-w-4xl",
    full: "max-w-[95vw] max-h-[95vh]",
  }
  
  return (
    <DialogPortal>
      <DialogOverlay />
      <DialogPrimitive.Content
        ref={ref}
        className={cn(
          "fixed left-[50%] top-[50%] z-50 grid w-full translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] rounded-lg",
          sizeClasses[size],
          size === "full" && "h-full w-full rounded-none",
          className
        )}
        {...props}
      >
        {children}
        {showClose && (
          <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </DialogPrimitive.Close>
        )}
      </DialogPrimitive.Content>
    </DialogPortal>
  )
})
DialogContent.displayName = DialogPrimitive.Content.displayName

// Dialog header section
const DialogHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "flex flex-col space-y-1.5 text-center sm:text-left",
      className
    )}
    {...props}
  />
))
DialogHeader.displayName = "DialogHeader"

// Dialog footer section
const DialogFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2",
      className
    )}
    {...props}
  />
))
DialogFooter.displayName = "DialogFooter"

// Dialog title
const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
DialogTitle.displayName = DialogPrimitive.Title.displayName

// Dialog description
const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
DialogDescription.displayName = DialogPrimitive.Description.displayName

// High-level confirmation dialog component
export interface ConfirmDialogProps {
  /**
   * Whether the dialog is open
   */
  open: boolean
  
  /**
   * Callback when dialog open state changes
   */
  onOpenChange: (open: boolean) => void
  
  /**
   * Dialog title
   */
  title: string
  
  /**
   * Dialog description/message
   */
  description?: string
  
  /**
   * Confirm button text
   * @default "Confirm"
   */
  confirmText?: string
  
  /**
   * Cancel button text
   * @default "Cancel"
   */
  cancelText?: string
  
  /**
   * Confirm button variant
   * @default "default"
   */
  confirmVariant?: "default" | "destructive" | "success"
  
  /**
   * Callback when confirmed
   */
  onConfirm?: () => void | Promise<void>
  
  /**
   * Callback when cancelled
   */
  onCancel?: () => void
  
  /**
   * Whether the confirm action is loading
   * @default false
   */
  loading?: boolean
  
  /**
   * Custom content to show instead of description
   */
  children?: React.ReactNode
}

const ConfirmDialog = React.forwardRef<
  React.ElementRef<typeof DialogContent>,
  ConfirmDialogProps
>(({ 
  open, 
  onOpenChange, 
  title, 
  description, 
  confirmText = "Confirm", 
  cancelText = "Cancel",
  confirmVariant = "default",
  onConfirm,
  onCancel,
  loading = false,
  children,
  ...props 
}, ref) => {
  const handleConfirm = async () => {
    if (onConfirm) {
      await onConfirm()
    }
    onOpenChange(false)
  }
  
  const handleCancel = () => {
    if (onCancel) {
      onCancel()
    }
    onOpenChange(false)
  }
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent ref={ref} {...props}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description && (
            <DialogDescription>{description}</DialogDescription>
          )}
        </DialogHeader>
        
        {children}
        
        <DialogFooter>
          <button
            type="button"
            onClick={handleCancel}
            disabled={loading}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
          >
            {cancelText}
          </button>
          
          <button
            type="button"
            onClick={handleConfirm}
            disabled={loading}
            className={cn(
              "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2",
              confirmVariant === "destructive" && "bg-error-500 text-white hover:bg-error-600",
              confirmVariant === "success" && "bg-success-500 text-white hover:bg-success-600", 
              confirmVariant === "default" && "bg-primary text-primary-foreground hover:bg-primary/90"
            )}
          >
            {loading && (
              <svg
                className="animate-spin -ml-1 mr-2 h-4 w-4"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            )}
            {confirmText}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
})
ConfirmDialog.displayName = "ConfirmDialog"

// Alert dialog for important messages
export interface AlertDialogProps {
  /**
   * Whether the dialog is open
   */
  open: boolean
  
  /**
   * Callback when dialog open state changes
   */
  onOpenChange: (open: boolean) => void
  
  /**
   * Dialog title
   */
  title: string
  
  /**
   * Dialog message
   */
  message?: string
  
  /**
   * Alert type affects styling
   * @default "info"
   */
  type?: "info" | "success" | "warning" | "error"
  
  /**
   * OK button text
   * @default "OK"
   */
  okText?: string
  
  /**
   * Callback when OK is clicked
   */
  onOk?: () => void
  
  /**
   * Custom content
   */
  children?: React.ReactNode
}

const AlertDialog = React.forwardRef<
  React.ElementRef<typeof DialogContent>,
  AlertDialogProps
>(({ 
  open, 
  onOpenChange, 
  title, 
  message, 
  type = "info",
  okText = "OK",
  onOk,
  children,
  ...props 
}, ref) => {
  const handleOk = () => {
    if (onOk) {
      onOk()
    }
    onOpenChange(false)
  }
  
  const typeColors = {
    info: "text-info-600",
    success: "text-success-600", 
    warning: "text-warning-600",
    error: "text-error-600",
  }
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent ref={ref} size="sm" {...props}>
        <DialogHeader>
          <DialogTitle className={cn("flex items-center gap-2", typeColors[type])}>
            {type === "success" && "✓"}
            {type === "warning" && "⚠"}
            {type === "error" && "✕"}
            {type === "info" && "ℹ"}
            {title}
          </DialogTitle>
          {message && (
            <DialogDescription>{message}</DialogDescription>
          )}
        </DialogHeader>
        
        {children}
        
        <DialogFooter>
          <button
            type="button"
            onClick={handleOk}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 w-full sm:w-auto"
          >
            {okText}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
})
AlertDialog.displayName = "AlertDialog"

// Export all components
export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  ConfirmDialog,
  AlertDialog,
}

// Type exports
export type DialogSize = "sm" | "md" | "lg" | "xl" | "full"
export type AlertType = "info" | "success" | "warning" | "error"