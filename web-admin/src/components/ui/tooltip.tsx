import * as React from "react"
import * as TooltipPrimitive from "@radix-ui/react-tooltip"
import { cn } from "@/lib/ui/utils"

/**
 * Tooltip component built with Radix UI Tooltip primitive
 * Provides accessible hover and focus tooltips
 */

// Tooltip provider - wrap your app with this
const TooltipProvider = TooltipPrimitive.Provider

// Tooltip root
const Tooltip = TooltipPrimitive.Root

// Tooltip trigger
const TooltipTrigger = TooltipPrimitive.Trigger

// Tooltip content
const TooltipContent = React.forwardRef<
  React.ElementRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>
>(({ className, sideOffset = 4, ...props }, ref) => (
  <TooltipPrimitive.Content
    ref={ref}
    sideOffset={sideOffset}
    className={cn(
      "z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
      className
    )}
    {...props}
  />
))
TooltipContent.displayName = TooltipPrimitive.Content.displayName

// Simple tooltip component for common usage
export interface SimpleTooltipProps {
  /**
   * Tooltip content text
   */
  content: React.ReactNode
  
  /**
   * Tooltip side
   * @default "top"
   */
  side?: "top" | "bottom" | "left" | "right"
  
  /**
   * Delay before showing tooltip in milliseconds
   * @default 700
   */
  delayDuration?: number
  
  /**
   * Whether tooltip should show on disabled elements
   * @default false
   */
  disableHoverableContent?: boolean
  
  /**
   * Element that triggers the tooltip
   */
  children: React.ReactNode
  
  /**
   * Additional CSS classes for content
   */
  className?: string
}

const SimpleTooltip = React.forwardRef<
  React.ElementRef<typeof TooltipContent>,
  SimpleTooltipProps
>(({ 
  content, 
  side = "top", 
  delayDuration = 700,
  disableHoverableContent = false,
  children, 
  className,
  ...props 
}, ref) => {
  return (
    <Tooltip delayDuration={delayDuration} disableHoverableContent={disableHoverableContent}>
      <TooltipTrigger asChild>
        {children}
      </TooltipTrigger>
      <TooltipContent 
        ref={ref}
        side={side} 
        className={className}
        {...props}
      >
        {content}
      </TooltipContent>
    </Tooltip>
  )
})
SimpleTooltip.displayName = "SimpleTooltip"

// Informational tooltip with icon
export interface InfoTooltipProps {
  /**
   * Tooltip content
   */
  content: React.ReactNode
  
  /**
   * Icon size
   * @default "sm"
   */
  size?: "sm" | "md" | "lg"
  
  /**
   * Additional CSS classes
   */
  className?: string
}

const InfoTooltip = React.forwardRef<
  React.ElementRef<typeof TooltipContent>,
  InfoTooltipProps
>(({ content, size = "sm", className, ...props }, ref) => {
  const iconSizes = {
    sm: "h-3 w-3",
    md: "h-4 w-4", 
    lg: "h-5 w-5",
  }
  
  return (
    <SimpleTooltip ref={ref} content={content} {...props}>
      <button
        type="button"
        className={cn(
          "inline-flex items-center justify-center rounded-full text-muted-foreground hover:text-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
          iconSizes[size],
          className
        )}
        aria-label="More information"
      >
        <svg
          className={iconSizes[size]}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </button>
    </SimpleTooltip>
  )
})
InfoTooltip.displayName = "InfoTooltip"

// Export all components
export {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider,
  SimpleTooltip,
  InfoTooltip,
}

// Type exports
export type TooltipSide = "top" | "bottom" | "left" | "right"