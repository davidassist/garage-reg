"use client"

import React from "react"
import { useState } from "react"
import {
  Button,
  Input,
  FormField,
  SimpleSelect,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  Drawer,
  SimpleTooltip,
  InfoTooltip,
  useToast,
  Toaster,
  ConfirmDialog,
  AlertDialog,
} from "@/components/ui"

/**
 * Design System Demo Page
 * 
 * Interactive showcase of all UI components with accessibility tests
 * This serves as both documentation and testing interface
 */

export default function DesignSystemDemo() {
  const [inputValue, setInputValue] = useState("")
  const [selectValue, setSelectValue] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [alertOpen, setAlertOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleAsyncAction = async () => {
    setLoading(true)
    await new Promise(resolve => setTimeout(resolve, 2000))
    setLoading(false)
    toast({
      title: "Success!",
      description: "Async action completed successfully",
      variant: "success",
    })
  }

  const selectOptions = [
    { value: "option1", label: "First Option" },
    { value: "option2", label: "Second Option" },
    { value: "option3", label: "Third Option" },
    { value: "disabled", label: "Disabled Option", disabled: true },
  ]

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold tracking-tight">
            GarageReg Design System
          </h1>
          <p className="text-lg text-muted-foreground mt-2">
            OKLCH-based components with full accessibility support
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-12">
        {/* Color Palette */}
        <section>
          <h2 className="text-2xl font-semibold mb-6">Color System</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Primary Colors */}
            <div>
              <h3 className="text-lg font-medium mb-3">Primary (Brand)</h3>
              <div className="space-y-2">
                {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950].map((shade) => (
                  <div
                    key={shade}
                    className={`h-12 rounded-md bg-primary-${shade} flex items-center px-3 text-sm font-medium`}
                    style={{ 
                      backgroundColor: `oklch(${97 - (shade / 1000) * 89}% ${0.020 + (shade / 1000) * 0.100} 240)`,
                      color: shade >= 500 ? "white" : "black"
                    }}
                  >
                    primary-{shade}
                  </div>
                ))}
              </div>
            </div>

            {/* Secondary/Gray Colors */}
            <div>
              <h3 className="text-lg font-medium mb-3">Secondary (Gray)</h3>
              <div className="space-y-2">
                {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950].map((shade) => (
                  <div
                    key={shade}
                    className="h-12 rounded-md flex items-center px-3 text-sm font-medium"
                    style={{ 
                      backgroundColor: `oklch(${98 - (shade / 1000) * 90}% ${0.005 + (shade / 1000) * 0.025} 285)`,
                      color: shade >= 500 ? "white" : "black"
                    }}
                  >
                    gray-{shade}
                  </div>
                ))}
              </div>
            </div>

            {/* Semantic Colors */}
            <div>
              <h3 className="text-lg font-medium mb-3">Semantic</h3>
              <div className="space-y-2">
                <div className="h-12 rounded-md bg-success-500 flex items-center px-3 text-sm font-medium text-white">
                  Success
                </div>
                <div className="h-12 rounded-md bg-warning-500 flex items-center px-3 text-sm font-medium text-white">
                  Warning
                </div>
                <div className="h-12 rounded-md bg-error-500 flex items-center px-3 text-sm font-medium text-white">
                  Error
                </div>
                <div className="h-12 rounded-md bg-info-500 flex items-center px-3 text-sm font-medium text-white">
                  Info
                </div>
              </div>
            </div>

            {/* Theme Colors */}
            <div>
              <h3 className="text-lg font-medium mb-3">Theme</h3>
              <div className="space-y-2">
                <div className="h-12 rounded-md bg-background border flex items-center px-3 text-sm font-medium">
                  Background
                </div>
                <div className="h-12 rounded-md bg-card border flex items-center px-3 text-sm font-medium">
                  Card
                </div>
                <div className="h-12 rounded-md bg-muted flex items-center px-3 text-sm font-medium">
                  Muted
                </div>
                <div className="h-12 rounded-md bg-accent flex items-center px-3 text-sm font-medium">
                  Accent
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Typography */}
        <section>
          <h2 className="text-2xl font-semibold mb-6">Typography</h2>
          <div className="space-y-4">
            <div className="text-xs">Extra Small (12px) - .text-xs</div>
            <div className="text-sm">Small (14px) - .text-sm</div>
            <div className="text-base">Base (16px) - .text-base</div>
            <div className="text-lg">Large (18px) - .text-lg</div>
            <div className="text-xl">Extra Large (20px) - .text-xl</div>
            <div className="text-2xl">2X Large (24px) - .text-2xl</div>
            <div className="text-3xl">3X Large (30px) - .text-3xl</div>
            <div className="text-4xl">4X Large (36px) - .text-4xl</div>
          </div>
        </section>

        {/* Buttons */}
        <section>
          <h2 className="text-2xl font-semibold mb-6">Buttons</h2>
          <div className="space-y-6">
            {/* Variants */}
            <div>
              <h3 className="text-lg font-medium mb-3">Variants</h3>
              <div className="flex flex-wrap gap-3">
                <Button variant="default">Default</Button>
                <Button variant="destructive">Destructive</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="link">Link</Button>
                <Button variant="success">Success</Button>
                <Button variant="warning">Warning</Button>
                <Button variant="info">Info</Button>
              </div>
            </div>

            {/* Sizes */}
            <div>
              <h3 className="text-lg font-medium mb-3">Sizes</h3>
              <div className="flex flex-wrap items-center gap-3">
                <Button size="sm">Small</Button>
                <Button size="md">Medium</Button>
                <Button size="lg">Large</Button>
                <Button size="icon">⚙</Button>
                <Button size="icon-sm">⚙</Button>
                <Button size="icon-lg">⚙</Button>
              </div>
            </div>

            {/* States */}
            <div>
              <h3 className="text-lg font-medium mb-3">States</h3>
              <div className="flex flex-wrap gap-3">
                <Button>Normal</Button>
                <Button disabled>Disabled</Button>
                <Button loading>Loading</Button>
                <Button 
                  loading={loading} 
                  onClick={handleAsyncAction}
                >
                  Async Action
                </Button>
              </div>
            </div>

            {/* With Icons */}
            <div>
              <h3 className="text-lg font-medium mb-3">With Icons</h3>
              <div className="flex flex-wrap gap-3">
                <Button leftIcon="📁">Open File</Button>
                <Button rightIcon="→">Next</Button>
                <Button leftIcon="💾" rightIcon="✓">Save & Close</Button>
              </div>
            </div>
          </div>
        </section>

        {/* Form Elements */}
        <section>
          <h2 className="text-2xl font-semibold mb-6">Form Elements</h2>
          <div className="max-w-md space-y-6">
            {/* Input Field */}
            <FormField
              label="Email Address"
              required
              helperText="We'll never share your email"
            >
              <Input
                type="email"
                placeholder="you@example.com"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
            </FormField>

            {/* Input with Error */}
            <FormField
              label="Password"
              error="Password must be at least 8 characters"
              required
            >
              <Input
                type="password"
                placeholder="••••••••"
              />
            </FormField>

            {/* Select */}
            <FormField
              label="Choose Option"
              helperText="Select from the available options"
            >
              <SimpleSelect
                placeholder="Select an option"
                value={selectValue}
                onValueChange={setSelectValue}
                options={selectOptions}
              />
            </FormField>

            {/* Input Sizes */}
            <div>
              <h3 className="text-lg font-medium mb-3">Input Sizes</h3>
              <div className="space-y-3">
                <Input size="sm" placeholder="Small input" />
                <Input size="md" placeholder="Medium input (default)" />
                <Input size="lg" placeholder="Large input" />
              </div>
            </div>
          </div>
        </section>

        {/* Interactive Components */}
        <section>
          <h2 className="text-2xl font-semibold mb-6">Interactive Components</h2>
          <div className="space-y-6">
            {/* Dialogs */}
            <div>
              <h3 className="text-lg font-medium mb-3">Dialogs</h3>
              <div className="flex flex-wrap gap-3">
                <Button onClick={() => setDialogOpen(true)}>
                  Open Dialog
                </Button>
                <Button onClick={() => setConfirmOpen(true)}>
                  Confirm Dialog
                </Button>
                <Button onClick={() => setAlertOpen(true)}>
                  Alert Dialog
                </Button>
              </div>
            </div>

            {/* Drawer */}
            <div>
              <h3 className="text-lg font-medium mb-3">Drawer/Sheet</h3>
              <Button onClick={() => setDrawerOpen(true)}>
                Open Drawer
              </Button>
            </div>

            {/* Tooltips */}
            <div>
              <h3 className="text-lg font-medium mb-3">Tooltips</h3>
              <div className="flex flex-wrap gap-6">
                <SimpleTooltip content="This is a tooltip">
                  <Button variant="outline">Hover for tooltip</Button>
                </SimpleTooltip>
                <InfoTooltip 
                  content="This provides additional information about the feature"
                  size="md" 
                />
              </div>
            </div>

            {/* Toasts */}
            <div>
              <h3 className="text-lg font-medium mb-3">Toast Notifications</h3>
              <div className="flex flex-wrap gap-3">
                <Button
                  variant="outline"
                  onClick={() => toast({
                    title: "Success",
                    description: "Your action was completed successfully",
                    variant: "success",
                  })}
                >
                  Success Toast
                </Button>
                <Button
                  variant="outline"
                  onClick={() => toast({
                    title: "Warning", 
                    description: "Please review your input",
                    variant: "warning",
                  })}
                >
                  Warning Toast
                </Button>
                <Button
                  variant="outline"
                  onClick={() => toast({
                    title: "Error",
                    description: "Something went wrong",
                    variant: "destructive",
                  })}
                >
                  Error Toast
                </Button>
                <Button
                  variant="outline"
                  onClick={() => toast({
                    title: "Information",
                    description: "Here's some useful information",
                    variant: "info",
                  })}
                >
                  Info Toast
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Accessibility Testing */}
        <section>
          <h2 className="text-2xl font-semibold mb-6">Accessibility Testing</h2>
          <div className="space-y-4">
            <div className="p-4 border rounded-lg">
              <h3 className="text-lg font-medium mb-2">Keyboard Navigation</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Tab through these elements and test keyboard interaction:
              </p>
              <div className="flex flex-wrap gap-3">
                <Button>Button 1</Button>
                <Button>Button 2</Button>
                <Input placeholder="Text input" />
                <SimpleSelect
                  placeholder="Select option"
                  options={[
                    { value: "1", label: "Option 1" },
                    { value: "2", label: "Option 2" },
                  ]}
                />
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <h3 className="text-lg font-medium mb-2">Focus Management</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Focus should be visible and trapped in modal dialogs:
              </p>
              <Button onClick={() => setDialogOpen(true)}>
                Test Focus Trap
              </Button>
            </div>

            <div className="p-4 border rounded-lg">
              <h3 className="text-lg font-medium mb-2">Screen Reader Support</h3>
              <p className="text-sm text-muted-foreground mb-4">
                All interactive elements have proper labels and descriptions:
              </p>
              <div className="space-y-3">
                <Button aria-label="Save document">💾</Button>
                <Input 
                  aria-label="Search query" 
                  placeholder="Search..." 
                />
                <SimpleTooltip content="Delete item permanently">
                  <Button variant="destructive" aria-label="Delete item">
                    🗑️
                  </Button>
                </SimpleTooltip>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Dialogs and Overlays */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Example Dialog</DialogTitle>
            <DialogDescription>
              This is an example dialog with proper focus management and accessibility.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <p>Dialog content goes here. You can tab through the elements.</p>
            <div className="mt-4 space-y-3">
              <Input placeholder="Focus test input" />
              <Button variant="outline">Focus test button</Button>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setDialogOpen(false)}>
              Confirm
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title="Confirm Action"
        description="Are you sure you want to perform this action? This cannot be undone."
        confirmText="Yes, confirm"
        cancelText="Cancel"
        confirmVariant="destructive"
        onConfirm={() => {
          toast({
            title: "Confirmed",
            description: "Action was confirmed",
            variant: "success",
          })
        }}
      />

      <AlertDialog
        open={alertOpen}
        onOpenChange={setAlertOpen}
        title="Important Notice"
        message="This is an important message that requires your attention."
        type="warning"
        okText="Understood"
      />

      <Drawer
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        title="Example Drawer"
        description="This is a slide-out panel for additional content"
        footer={
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setDrawerOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setDrawerOpen(false)}>
              Save
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <p>Drawer content goes here. This panel slides in from the side.</p>
          <FormField label="Example Field">
            <Input placeholder="Input in drawer" />
          </FormField>
          <FormField label="Another Field">
            <SimpleSelect
              placeholder="Select option"
              options={selectOptions}
            />
          </FormField>
        </div>
      </Drawer>

      <Toaster />
    </div>
  )
}