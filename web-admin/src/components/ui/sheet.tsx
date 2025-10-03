import * as React from "react"
import * as SheetPrimitive from "@radix-ui/react-dialog"
import { cva, type VariantProps } from "class-variance-authority"
import { X } from "lucide-react"
import { cn } from "@/lib/ui/utils"

/**
 * Sheet/Drawer component built with Radix UI Dialog
 * Provides slide-in panels from different sides
 */

// Sheet root component
const Sheet = SheetPrimitive.Root

// Sheet trigger
const SheetTrigger = SheetPrimitive.Trigger

// Sheet close
const SheetClose = SheetPrimitive.Close

// Sheet portal
const SheetPortal = SheetPrimitive.Portal

// Sheet overlay
const SheetOverlay = React.forwardRef<
  React.ElementRef<typeof SheetPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof SheetPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <SheetPrimitive.Overlay
    className={cn(
      "fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
    ref={ref}
  />
))
SheetOverlay.displayName = SheetPrimitive.Overlay.displayName

// Sheet content variants
const sheetVariants = cva(
  "fixed z-50 gap-4 bg-background p-6 shadow-lg transition ease-in-out data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:duration-300 data-[state=open]:duration-500",
  {
    variants: {
      side: {
        top: "inset-x-0 top-0 border-b data-[state=closed]:slide-out-to-top data-[state=open]:slide-in-from-top",
        bottom: "inset-x-0 bottom-0 border-t data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom",
        left: "inset-y-0 left-0 h-full w-3/4 border-r data-[state=closed]:slide-out-to-left data-[state=open]:slide-in-from-left sm:max-w-sm",
        right: "inset-y-0 right-0 h-full w-3/4 border-l data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right sm:max-w-sm",
      },
    },
    defaultVariants: {
      side: "right",
    },
  }
)

// Sheet content component
export interface SheetContentProps
  extends React.ComponentPropsWithoutRef<typeof SheetPrimitive.Content>,
    VariantProps<typeof sheetVariants> {
  /**
   * Whether to show the close button
   * @default true
   */
  showClose?: boolean
}

const SheetContent = React.forwardRef<
  React.ElementRef<typeof SheetPrimitive.Content>,
  SheetContentProps
>(({ side = "right", className, children, showClose = true, ...props }, ref) => (
  <SheetPortal>
    <SheetOverlay />
    <SheetPrimitive.Content
      ref={ref}
      className={cn(sheetVariants({ side }), className)}
      {...props}
    >
      {children}
      {showClose && (
        <SheetPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-secondary">
          <X className="h-4 w-4" />
          <span className="sr-only">Close</span>
        </SheetPrimitive.Close>
      )}
    </SheetPrimitive.Content>
  </SheetPortal>
))
SheetContent.displayName = SheetPrimitive.Content.displayName

// Sheet header
const SheetHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "flex flex-col space-y-2 text-center sm:text-left",
      className
    )}
    {...props}
  />
))
SheetHeader.displayName = "SheetHeader"

// Sheet footer
const SheetFooter = React.forwardRef<
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
SheetFooter.displayName = "SheetFooter"

// Sheet title
const SheetTitle = React.forwardRef<
  React.ElementRef<typeof SheetPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof SheetPrimitive.Title>
>(({ className, ...props }, ref) => (
  <SheetPrimitive.Title
    ref={ref}
    className={cn("text-lg font-semibold text-foreground", className)}
    {...props}
  />
))
SheetTitle.displayName = SheetPrimitive.Title.displayName

// Sheet description
const SheetDescription = React.forwardRef<
  React.ElementRef<typeof SheetPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof SheetPrimitive.Description>
>(({ className, ...props }, ref) => (
  <SheetPrimitive.Description
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
SheetDescription.displayName = SheetPrimitive.Description.displayName

// Higher-level drawer component
export interface DrawerProps {
  /**
   * Whether the drawer is open
   */
  open: boolean
  
  /**
   * Callback when drawer open state changes
   */
  onOpenChange: (open: boolean) => void
  
  /**
   * Drawer title
   */
  title?: string
  
  /**
   * Drawer description
   */
  description?: string
  
  /**
   * Side to slide in from
   * @default "right"
   */
  side?: "top" | "bottom" | "left" | "right"
  
  /**
   * Whether to show close button
   * @default true
   */
  showClose?: boolean
  
  /**
   * Additional CSS classes
   */
  className?: string
  
  /**
   * Drawer content
   */
  children: React.ReactNode
  
  /**
   * Footer content (buttons, actions)
   */
  footer?: React.ReactNode
}

const Drawer = React.forwardRef<
  React.ElementRef<typeof SheetContent>,
  DrawerProps
>(({ 
  open, 
  onOpenChange, 
  title, 
  description, 
  side = "right", 
  showClose = true,
  className,
  children,
  footer,
  ...props 
}, ref) => {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent 
        ref={ref} 
        side={side} 
        showClose={showClose}
        className={className}
        {...props}
      >
        {(title || description) && (
          <SheetHeader>
            {title && <SheetTitle>{title}</SheetTitle>}
            {description && <SheetDescription>{description}</SheetDescription>}
          </SheetHeader>
        )}
        
        <div className="flex-1 overflow-auto">
          {children}
        </div>
        
        {footer && (
          <SheetFooter>{footer}</SheetFooter>
        )}
      </SheetContent>
    </Sheet>
  )
})
Drawer.displayName = "Drawer"

// Navigation drawer for menus
export interface NavigationDrawerProps {
  /**
   * Whether the drawer is open
   */
  open: boolean
  
  /**
   * Callback when drawer open state changes
   */
  onOpenChange: (open: boolean) => void
  
  /**
   * Navigation items
   */
  items: Array<{
    label: string
    href?: string
    onClick?: () => void
    icon?: React.ReactNode
    active?: boolean
    disabled?: boolean
  }>
  
  /**
   * Header content
   */
  header?: React.ReactNode
  
  /**
   * Footer content
   */
  footer?: React.ReactNode
  
  /**
   * Side to slide in from
   * @default "left"
   */
  side?: "left" | "right"
}

const NavigationDrawer = React.forwardRef<
  React.ElementRef<typeof SheetContent>,
  NavigationDrawerProps
>(({ 
  open, 
  onOpenChange, 
  items, 
  header,
  footer,
  side = "left",
  ...props 
}, ref) => {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent ref={ref} side={side} {...props}>
        {header && (
          <SheetHeader>{header}</SheetHeader>
        )}
        
        <nav className="flex-1">
          <ul className="space-y-1">
            {items.map((item, index) => (
              <li key={index}>
                {item.href ? (
                  <a
                    href={item.href}
                    onClick={() => {
                      if (item.onClick) item.onClick()
                      onOpenChange(false)
                    }}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                      "hover:bg-accent hover:text-accent-foreground",
                      item.active && "bg-accent text-accent-foreground",
                      item.disabled && "pointer-events-none opacity-50"
                    )}
                  >
                    {item.icon && (
                      <span className="h-4 w-4">{item.icon}</span>
                    )}
                    {item.label}
                  </a>
                ) : (
                  <button
                    type="button"
                    onClick={() => {
                      if (item.onClick) item.onClick()
                      onOpenChange(false)
                    }}
                    disabled={item.disabled}
                    className={cn(
                      "flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                      "hover:bg-accent hover:text-accent-foreground",
                      item.active && "bg-accent text-accent-foreground",
                      item.disabled && "pointer-events-none opacity-50"
                    )}
                  >
                    {item.icon && (
                      <span className="h-4 w-4">{item.icon}</span>
                    )}
                    {item.label}
                  </button>
                )}
              </li>
            ))}
          </ul>
        </nav>
        
        {footer && (
          <SheetFooter>{footer}</SheetFooter>
        )}
      </SheetContent>
    </Sheet>
  )
})
NavigationDrawer.displayName = "NavigationDrawer"

// Export all components
export {
  Sheet,
  SheetPortal,
  SheetOverlay,
  SheetTrigger,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetFooter,
  SheetTitle,
  SheetDescription,
  Drawer,
  NavigationDrawer,
}

// Type exports
export type SheetSide = "top" | "bottom" | "left" | "right"