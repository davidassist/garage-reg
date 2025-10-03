import * as React from "react"
import { cn } from "@/lib/ui/utils"

/**
 * Input component with variants, sizes, and accessibility features
 * Supports labels, helper text, error states, and icons
 */

// Input variant styles
const inputVariants = {
  base: "flex w-full rounded-md border border-input bg-background ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
  
  variants: {
    variant: {
      default: "text-foreground",
      error: "border-error-500 text-foreground focus-visible:ring-error-500",
    },
    
    size: {
      sm: "h-8 px-2 text-xs",
      md: "h-10 px-3 py-2 text-sm", 
      lg: "h-11 px-3 py-3 text-base",
    },
  },
  
  defaultVariants: {
    variant: "default" as const,
    size: "md" as const,
  },
}

// Helper function to generate input classes
function getInputClasses({
  variant = "default",
  size = "md",
  className,
}: {
  variant?: keyof typeof inputVariants.variants.variant
  size?: keyof typeof inputVariants.variants.size
  className?: string
}) {
  const variantClass = inputVariants.variants.variant[variant]
  const sizeClass = inputVariants.variants.size[size]
  
  return cn(inputVariants.base, variantClass, sizeClass, className)
}

// Base input props
export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  /**
   * Input style variant
   * @default "default"
   */
  variant?: keyof typeof inputVariants.variants.variant
  
  /**
   * Input size
   * @default "md"
   */
  size?: keyof typeof inputVariants.variants.size
}

// Base Input component
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, variant = "default", size = "md", type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={getInputClasses({ variant, size, className })}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

// Label component for inputs
export interface LabelProps
  extends React.LabelHTMLAttributes<HTMLLabelElement> {
  /**
   * Whether the field is required (adds asterisk)
   * @default false
   */
  required?: boolean
}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, children, required, ...props }, ref) => (
    <label
      ref={ref}
      className={cn(
        "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
        className
      )}
      {...props}
    >
      {children}
      {required && (
        <span className="ml-1 text-error-500" aria-label="required">
          *
        </span>
      )}
    </label>
  )
)
Label.displayName = "Label"

// Helper text component
export interface HelperTextProps
  extends React.HTMLAttributes<HTMLParagraphElement> {
  /**
   * Helper text variant - affects styling
   * @default "default"
   */
  variant?: "default" | "error"
}

const HelperText = React.forwardRef<HTMLParagraphElement, HelperTextProps>(
  ({ className, variant = "default", ...props }, ref) => (
    <p
      ref={ref}
      className={cn(
        "text-xs mt-1.5",
        variant === "error" 
          ? "text-error-500" 
          : "text-muted-foreground",
        className
      )}
      {...props}
    />
  )
)
HelperText.displayName = "HelperText"

// Form field wrapper component
export interface FormFieldProps {
  /**
   * Field label text
   */
  label?: string
  
  /**
   * Whether the field is required
   * @default false  
   */
  required?: boolean
  
  /**
   * Helper text to display below input
   */
  helperText?: string
  
  /**
   * Error message to display
   */
  error?: string
  
  /**
   * Unique ID for the input element
   */
  id?: string
  
  /**
   * Additional CSS classes
   */
  className?: string
  
  /**
   * Input element or custom content
   */
  children: React.ReactNode
}

const FormField = React.forwardRef<HTMLDivElement, FormFieldProps>(
  ({ label, required, helperText, error, id, className, children }, ref) => {
    const inputId = id || React.useId()
    const helperTextId = helperText || error ? `${inputId}-helper` : undefined
    
    return (
      <div ref={ref} className={cn("space-y-1.5", className)}>
        {label && (
          <Label htmlFor={inputId} required={required}>
            {label}
          </Label>
        )}
        
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child)) {
            return React.cloneElement(child as React.ReactElement<any>, {
              id: inputId,
              "aria-describedby": helperTextId,
              "aria-invalid": error ? "true" : "false",
              variant: error ? "error" : (child.props as any).variant,
            })
          }
          return child
        })}
        
        {(helperText || error) && (
          <HelperText 
            id={helperTextId}
            variant={error ? "error" : "default"}
          >
            {error || helperText}
          </HelperText>
        )}
      </div>
    )
  }
)
FormField.displayName = "FormField"

// Input with icon support
export interface InputWithIconProps extends InputProps {
  /**
   * Icon to display on the left side of input
   */
  leftIcon?: React.ReactNode
  
  /**
   * Icon to display on the right side of input  
   */
  rightIcon?: React.ReactNode
}

const InputWithIcon = React.forwardRef<HTMLInputElement, InputWithIconProps>(
  ({ className, leftIcon, rightIcon, size = "md", ...props }, ref) => {
    const hasLeftIcon = Boolean(leftIcon)
    const hasRightIcon = Boolean(rightIcon)
    
    const iconSize = size === "sm" ? "h-3 w-3" : size === "lg" ? "h-5 w-5" : "h-4 w-4"
    const paddingLeft = hasLeftIcon 
      ? size === "sm" ? "pl-7" : size === "lg" ? "pl-10" : "pl-9"
      : undefined
    const paddingRight = hasRightIcon
      ? size === "sm" ? "pr-7" : size === "lg" ? "pr-10" : "pr-9" 
      : undefined
    
    return (
      <div className="relative">
        {leftIcon && (
          <div className={cn(
            "absolute left-0 top-0 flex h-full items-center justify-center",
            size === "sm" ? "w-7" : size === "lg" ? "w-10" : "w-9",
            "text-muted-foreground pointer-events-none"
          )}>
            <div className={iconSize}>{leftIcon}</div>
          </div>
        )}
        
        <Input
          ref={ref}
          className={cn(paddingLeft, paddingRight, className)}
          size={size}
          {...props}
        />
        
        {rightIcon && (
          <div className={cn(
            "absolute right-0 top-0 flex h-full items-center justify-center",
            size === "sm" ? "w-7" : size === "lg" ? "w-10" : "w-9",
            "text-muted-foreground pointer-events-none"
          )}>
            <div className={iconSize}>{rightIcon}</div>
          </div>
        )}
      </div>
    )
  }
)
InputWithIcon.displayName = "InputWithIcon"

// Textarea component
export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  /**
   * Textarea variant
   * @default "default"
   */
  variant?: keyof typeof inputVariants.variants.variant
  
  /**
   * Auto-resize based on content
   * @default false
   */
  autoResize?: boolean
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, variant = "default", autoResize = false, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          inputVariants.base,
          inputVariants.variants.variant[variant],
          "min-h-[60px] px-3 py-2 text-sm",
          autoResize && "resize-none",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Textarea.displayName = "Textarea"

// Export all components and utilities
export { 
  Input, 
  Label, 
  HelperText, 
  FormField, 
  InputWithIcon, 
  Textarea,
  inputVariants,
  getInputClasses 
}

// Type exports
export type InputVariant = keyof typeof inputVariants.variants.variant
export type InputSize = keyof typeof inputVariants.variants.size