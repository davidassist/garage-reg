/**
 * GarageReg Design System UI Components
 * 
 * A comprehensive set of accessible, customizable UI components
 * built with OKLCH colors, Radix UI primitives, and Tailwind CSS.
 */

// Core utilities
export * from "./utils"

// Button components
export {
  Button,
  buttonVariants,
  getButtonClasses,
  type ButtonProps,
  type ButtonVariant,
  type ButtonSize,
} from "./button"

// New components
export { Badge, badgeVariants } from "./badge"
export { 
  Table, 
  TableHeader, 
  TableBody, 
  TableFooter, 
  TableHead, 
  TableRow, 
  TableCell, 
  TableCaption 
} from "./table"
export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuGroup,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuRadioGroup,
} from "./dropdown-menu"

// Input components  
export {
  Input,
  Label,
  HelperText,
  FormField,
  InputWithIcon,
  Textarea,
  inputVariants,
  getInputClasses,
  type InputProps,
  type LabelProps,
  type HelperTextProps,
  type FormFieldProps,
  type InputWithIconProps,
  type TextareaProps,
  type InputVariant,
  type InputSize,
} from "./input"

// Select components
export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  SelectScrollUpButton,
  SelectScrollDownButton,
  SimpleSelect,
  GroupedSelect,
  type SimpleSelectProps,
  type GroupedSelectProps,
  type SelectTriggerSize,
} from "./select"

// Dialog components
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
  type ConfirmDialogProps,
  type AlertDialogProps,
  type DialogSize,
  type AlertType,
} from "./dialog"

// Sheet/Drawer components
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
  type SheetContentProps,
  type DrawerProps,
  type NavigationDrawerProps,
  type SheetSide,
} from "./sheet"

// Tooltip components
export {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider,
  SimpleTooltip,
  InfoTooltip,
  type SimpleTooltipProps,
  type InfoTooltipProps,
  type TooltipSide,
} from "./tooltip"

// Toast components
export {
  ToastProvider,
  ToastViewport,
  Toast,
  ToastTitle,
  ToastDescription,
  ToastClose,
  ToastAction,
  Toaster,
  useToast,
  type ToastProps,
  type ToastActionElement,
  type ToastVariant,
} from "./toast"