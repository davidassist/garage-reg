import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './button'
import { Mail, Download, Plus, Trash2 } from 'lucide-react'

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
      description: 'Visual style variant of the button',
    },
    size: {
      control: { type: 'select' },
      options: ['md', 'sm', 'lg', 'icon', 'icon-sm', 'icon-lg'],
      description: 'Size of the button',
    },
    disabled: {
      control: { type: 'boolean' },
      description: 'Disable button interaction',
    },
    asChild: {
      control: { type: 'boolean' },
      description: 'Render as a different element while keeping the button styling',
    },
  },
} satisfies Meta<typeof Button>

export default meta
type Story = StoryObj<typeof meta>

// Primary button (default variant)
export const Default: Story = {
  args: {
    children: 'Button',
    variant: 'default',
    size: 'md',
  },
}

// All variants showcase
export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-wrap gap-4">
      <Button variant="default">Default</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="link">Link</Button>
      <Button variant="destructive">Destructive</Button>
    </div>
  ),
}

// All sizes showcase
export const AllSizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
}

// Buttons with icons
export const WithIcons: Story = {
  render: () => (
    <div className="flex flex-wrap gap-4">
      <Button>
        <Mail className="mr-2 h-4 w-4" />
        Send Email
      </Button>
      <Button variant="outline">
        <Download className="mr-2 h-4 w-4" />
        Download
      </Button>
      <Button variant="secondary">
        <Plus className="mr-2 h-4 w-4" />
        Add Item
      </Button>
      <Button variant="destructive">
        <Trash2 className="mr-2 h-4 w-4" />
        Delete
      </Button>
    </div>
  ),
}

// Icon-only buttons
export const IconOnly: Story = {
  render: () => (
    <div className="flex gap-2">
      <Button size="icon">
        <Plus className="h-4 w-4" />
        <span className="sr-only">Add item</span>
      </Button>
      <Button size="icon" variant="outline">
        <Mail className="h-4 w-4" />
        <span className="sr-only">Send email</span>
      </Button>
      <Button size="icon" variant="ghost">
        <Download className="h-4 w-4" />
        <span className="sr-only">Download</span>
      </Button>
    </div>
  ),
}

// Button states
export const States: Story = {
  render: () => (
    <div className="space-y-4">
      <div className="flex gap-4">
        <Button>Normal</Button>
        <Button disabled>Disabled</Button>
      </div>
      
      <div className="flex gap-4">
        <Button variant="destructive">Normal</Button>
        <Button variant="destructive" disabled>Disabled</Button>
      </div>
      
      <div className="flex gap-4">
        <Button variant="outline">Normal</Button>
        <Button variant="outline" disabled>Disabled</Button>
      </div>
    </div>
  ),
}

// Loading state (if implemented)
export const Loading: Story = {
  render: () => (
    <div className="flex gap-4">
      <Button disabled>
        <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        Loading...
      </Button>
      <Button variant="outline" disabled>
        <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        Processing
      </Button>
    </div>
  ),
}

// Accessibility demonstration
export const Accessibility: Story = {
  render: () => (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">Keyboard Navigation Test</h3>
      <p className="text-sm text-muted-foreground mb-4">
        Use Tab to navigate, Enter/Space to activate, and check focus indicators.
      </p>
      
      <div className="flex flex-wrap gap-2">
        <Button>First Button</Button>
        <Button variant="outline">Second Button</Button>
        <Button variant="secondary">Third Button</Button>
        <Button size="icon" aria-label="Settings">
          <Mail className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="mt-4 p-4 bg-muted rounded-lg">
        <h4 className="font-medium mb-2">Focus Management</h4>
        <ul className="text-sm space-y-1">
          <li>• All buttons have visible focus indicators</li>
          <li>• Icon buttons include proper ARIA labels</li>
          <li>• Screen readers announce button role and state</li>
          <li>• Keyboard activation works with Enter and Space</li>
        </ul>
      </div>
    </div>
  ),
}

// Color contrast (OKLCH demonstration)
export const ColorContrast: Story = {
  render: () => (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">OKLCH Color System</h3>
      <p className="text-sm text-muted-foreground mb-4">
        All colors maintain proper contrast ratios in light and dark themes.
      </p>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <h4 className="font-medium">Light Theme</h4>
          <div className="bg-background p-4 rounded border">
            <Button>Primary</Button>
            <Button variant="secondary" className="ml-2">Secondary</Button>
            <Button variant="outline" className="ml-2">Outline</Button>
          </div>
        </div>
        
        <div className="space-y-2">
          <h4 className="font-medium">Dark Theme</h4>
          <div className="bg-background p-4 rounded border dark">
            <Button>Primary</Button>
            <Button variant="secondary" className="ml-2">Secondary</Button>
            <Button variant="outline" className="ml-2">Outline</Button>
          </div>
        </div>
      </div>
    </div>
  ),
}

// Form examples
export const InForms: Story = {
  render: () => (
    <div className="max-w-md space-y-6">
      <h3 className="text-lg font-medium">Form Usage Examples</h3>
      
      <form className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium">
            Email
          </label>
          <input
            id="email"
            type="email"
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="Enter your email"
          />
        </div>
        
        <div className="flex gap-2">
          <Button type="submit" className="flex-1">
            Submit
          </Button>
          <Button type="button" variant="outline">
            Cancel
          </Button>
        </div>
      </form>
    </div>
  ),
}