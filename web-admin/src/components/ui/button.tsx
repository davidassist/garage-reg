import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cn } from "@/lib/ui/utils"

/**
 * Button component built with Radix UI Slot for composition
 * Supports multiple variants, sizes, and accessibility features
 */

// Button variant styles using OKLCH colors
const buttonVariants = {
  // Base styles for all buttons
  base: "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  
  // Style variants
  variants: {
    variant: {
      // Primary button - main brand color (OKLCH blue)
      default: "bg-primary text-primary-foreground hover:bg-primary/90 active:bg-primary/95",
      
      // Destructive button - error color (OKLCH red)  
      destructive: "bg-error-500 text-white hover:bg-error-600 active:bg-error-700 focus-visible:ring-error-500",
      
      // Outline button - transparent with border
      outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground active:bg-accent/90",
      
      // Secondary button - muted appearance
      secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80 active:bg-secondary/90",
      
      // Ghost button - transparent background
      ghost: "hover:bg-accent hover:text-accent-foreground active:bg-accent/90",
      
      // Link button - appears as text link
      link: "text-primary underline-offset-4 hover:underline active:text-primary/90",
      
      // Success button - green semantic color
      success: "bg-success-500 text-white hover:bg-success-600 active:bg-success-700 focus-visible:ring-success-500",
      
      // Warning button - orange semantic color  
      warning: "bg-warning-500 text-white hover:bg-warning-600 active:bg-warning-700 focus-visible:ring-warning-500",
      
      // Info button - blue semantic color
      info: "bg-info-500 text-white hover:bg-info-600 active:bg-info-700 focus-visible:ring-info-500",
    },
    
    // Size variants
    size: {
      sm: "h-8 px-3 text-xs rounded-sm",
      md: "h-10 px-4 py-2",
      lg: "h-11 px-8 rounded-lg",
      icon: "h-10 w-10",
      "icon-sm": "h-8 w-8 rounded-sm",
      "icon-lg": "h-11 w-11 rounded-lg",
    },
  },
  
  // Default variants when none specified
  defaultVariants: {
    variant: "default" as const,
    size: "md" as const,
  },
}

// Helper function to generate button classes
function getButtonClasses({
  variant = "default",
  size = "md", 
  className,
}: {
  variant?: keyof typeof buttonVariants.variants.variant
  size?: keyof typeof buttonVariants.variants.size
  className?: string
}) {
  const variantClass = buttonVariants.variants.variant[variant]
  const sizeClass = buttonVariants.variants.size[size]
  
  return cn(buttonVariants.base, variantClass, sizeClass, className)
}

// Button component props
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Button style variant
   * @default "default"
   */
  variant?: keyof typeof buttonVariants.variants.variant
  
  /**
   * Button size
   * @default "md"  
   */
  size?: keyof typeof buttonVariants.variants.size
  
  /**
   * Render as a different element or component
   * Uses Radix UI Slot for composition
   * @default false
   */
  asChild?: boolean
  
  /**
   * Loading state - shows spinner and disables interaction
   * @default false
   */
  loading?: boolean
  
  /**
   * Icon to display before the button content
   */
  leftIcon?: React.ReactNode
  
  /**
   * Icon to display after the button content  
   */
  rightIcon?: React.ReactNode
}

// Loading spinner component
const LoadingSpinner = React.forwardRef<
  SVGSVGElement,
  React.SVGProps<SVGSVGElement>
>(({ className, ...props }, ref) => (
  <svg
    ref={ref}
    className={cn("animate-spin", className)}
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M21 12a9 9 0 11-6.219-8.56" />
  </svg>
))
LoadingSpinner.displayName = "LoadingSpinner"

// Main Button component
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant = "default", 
    size = "md", 
    asChild = false, 
    loading = false,
    leftIcon,
    rightIcon,
    children,
    disabled,
    ...props 
  }, ref) => {
    const Comp = asChild ? Slot : "button"
    
    const isDisabled = disabled || loading
    
    return (
      <Comp
        className={getButtonClasses({ variant, size, className })}
        ref={ref}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        {...props}
      >
        {loading && (
          <LoadingSpinner className={cn(
            "mr-2",
            size === "sm" || size === "icon-sm" ? "h-3 w-3" : "h-4 w-4"
          )} />
        )}
        
        {!loading && leftIcon && (
          <span className={cn(
            "mr-2 flex items-center",
            size === "sm" || size === "icon-sm" ? "*:h-3 *:w-3" : "*:h-4 *:w-4"
          )}>
            {leftIcon}
          </span>
        )}
        
        {children}
        
        {!loading && rightIcon && (
          <span className={cn(
            "ml-2 flex items-center", 
            size === "sm" || size === "icon-sm" ? "*:h-3 *:w-3" : "*:h-4 *:w-4"
          )}>
            {rightIcon}
          </span>
        )}
      </Comp>
    )
  }
)
Button.displayName = "Button"

// Export button variants function for external use
export { Button, buttonVariants, getButtonClasses }

// Type exports for external use
export type ButtonVariant = keyof typeof buttonVariants.variants.variant
export type ButtonSize = keyof typeof buttonVariants.variants.size