# GarageReg Design System & UI Guidelines

A comprehensive design system built with modern standards, accessibility-first approach, and OKLCH color space for consistent visual perception across all devices.

## Table of Contents

- [Overview](#overview)
- [Color System](#color-system)
- [Typography](#typography)
- [Spacing & Layout](#spacing--layout)
- [Components](#components)
- [Accessibility](#accessibility)
- [Usage Patterns](#usage-patterns)
- [Development Guidelines](#development-guidelines)

## Overview

The GarageReg Design System provides a unified visual language and component library for building consistent, accessible user interfaces. Built on modern web standards with a focus on usability, performance, and maintainability.

### Core Principles

- **Accessibility First**: WCAG 2.1 AA compliance by default
- **Modern Color Science**: OKLCH color space for perceptually uniform colors
- **Progressive Enhancement**: Works across all devices and browsers
- **Developer Experience**: Easy to use, well-documented, type-safe
- **Consistency**: Unified visual language across all interfaces

### Technology Stack

- **Framework**: Next.js 14+ with TypeScript
- **Styling**: Tailwind CSS with CSS Custom Properties
- **Components**: React + Radix UI primitives
- **Icons**: Lucide React
- **Color Space**: OKLCH for better color perception
- **Testing**: Storybook + Playwright for component testing

## Color System

Our color system is built on the OKLCH color space for superior color perception and accessibility across different devices and lighting conditions.

### OKLCH Color Space Benefits

- **Perceptually uniform**: Colors with the same lightness value appear equally bright
- **Better accessibility**: More predictable contrast ratios
- **Device-independent**: Consistent appearance across displays
- **Future-proof**: Wide gamut color support

### Color Palette

#### Primary Colors (Brand Blue - Hue 240°)
```css
--primary-50: oklch(97% 0.020 240);   /* Lightest */
--primary-500: oklch(56% 0.120 240);  /* Main brand */
--primary-950: oklch(16% 0.040 240);  /* Darkest */
```

#### Secondary/Gray Colors (Neutral - Hue 285°)
```css
--secondary-50: oklch(98% 0.005 285);
--secondary-500: oklch(57% 0.030 285);  /* True gray */
--secondary-950: oklch(8% 0.005 285);
```

#### Semantic Colors
- **Success**: Green (Hue 145°) - `oklch(60% 0.130 145)`
- **Warning**: Orange (Hue 85°) - `oklch(70% 0.150 85)`
- **Error**: Red (Hue 25°) - `oklch(55% 0.180 25)`
- **Info**: Cyan (Hue 220°) - `oklch(60% 0.120 220)`

### Dark Mode Support

All colors automatically adapt to dark mode through CSS custom properties:

```css
/* Light mode */
:root {
  --background: oklch(98% 0.005 285);
  --foreground: oklch(15% 0.010 285);
}

/* Dark mode */
.dark {
  --background: oklch(8% 0.005 285);
  --foreground: oklch(95% 0.010 285);
}
```

### Usage in Code

```tsx
import { theme } from '@/lib/ui/theme'

// Direct color access
const primaryColor = theme.colors.primary[500]

// Utility function
import { getColorValue } from '@/lib/ui/theme'
const color = getColorValue('primary.500')

// CSS classes (via Tailwind)
<div className="bg-primary-500 text-primary-50">
  Brand colored content
</div>
```

## Typography

### Font System

- **Primary**: Inter - Clean, readable sans-serif for UI text
- **Monospace**: JetBrains Mono - For code and technical content

### Type Scale

| Size | CSS | Line Height | Usage |
|------|-----|-------------|-------|
| xs | 0.75rem (12px) | 1rem | Fine print, captions |
| sm | 0.875rem (14px) | 1.25rem | Small text, labels |
| base | 1rem (16px) | 1.5rem | Body text |
| lg | 1.125rem (18px) | 1.75rem | Large body text |
| xl | 1.25rem (20px) | 1.75rem | Subheadings |
| 2xl | 1.5rem (24px) | 2rem | Page titles |
| 3xl | 1.875rem (30px) | 2.25rem | Section headers |
| 4xl | 2.25rem (36px) | 2.5rem | Large displays |

### Font Weights

- **Normal (400)**: Body text, descriptions
- **Medium (500)**: Labels, emphasized text
- **Semibold (600)**: Subheadings, important text
- **Bold (700)**: Headings, strong emphasis

### Usage Examples

```tsx
// Heading hierarchy
<h1 className="text-4xl font-bold">Main Page Title</h1>
<h2 className="text-2xl font-semibold">Section Header</h2>
<h3 className="text-xl font-medium">Subsection</h3>

// Body text
<p className="text-base">Regular paragraph text</p>
<p className="text-sm text-secondary-600">Secondary information</p>

// Code and technical content
<code className="font-mono text-sm">API_KEY=value</code>
```

## Spacing & Layout

### Spacing Scale (4px base unit)

| Token | Value | Usage |
|-------|-------|--------|
| 0.5 | 2px | Tight spacing |
| 1 | 4px | Base unit |
| 2 | 8px | Small gaps |
| 3 | 12px | Medium gaps |
| 4 | 16px | Standard spacing |
| 6 | 24px | Large spacing |
| 8 | 32px | Section spacing |
| 12 | 48px | Page sections |

### Layout Patterns

```tsx
// Card layout with consistent spacing
<div className="p-6 space-y-4">
  <h3 className="text-lg font-medium">Card Title</h3>
  <p className="text-sm text-secondary-600">Description</p>
  <div className="flex gap-3">
    <Button>Primary</Button>
    <Button variant="outline">Secondary</Button>
  </div>
</div>

// Form spacing
<form className="space-y-6">
  <div className="space-y-2">
    <Label>Field Label</Label>
    <Input placeholder="Enter value" />
  </div>
</form>
```

### Border Radius

- **sm**: 4px - Small elements, badges
- **DEFAULT**: 6px - Buttons, inputs, cards
- **md**: 8px - Larger components
- **lg**: 12px - Containers, modals
- **xl**: 16px - Large surfaces
- **full**: 9999px - Circular elements

## Components

### Core Components

#### Button
Primary interactive elements with multiple variants and states.

```tsx
import { Button } from '@/components/ui/button'

// Variants
<Button variant="default">Primary Action</Button>
<Button variant="outline">Secondary Action</Button>
<Button variant="ghost">Subtle Action</Button>
<Button variant="destructive">Delete Item</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="default">Regular</Button>
<Button size="lg">Large</Button>

// States
<Button disabled>Disabled</Button>
<Button loading>Loading...</Button>
```

#### Input
Form inputs with consistent styling and accessibility features.

```tsx
import { Input } from '@/components/ui/input'

<Input 
  type="email" 
  placeholder="Enter email"
  aria-describedby="email-help"
/>
```

#### Select
Dropdown selection with keyboard navigation and accessibility.

```tsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
    <SelectItem value="option2">Option 2</SelectItem>
  </SelectContent>
</Select>
```

#### Dialog
Modal dialogs for critical actions and forms.

```tsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'

<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
    </DialogHeader>
    <p>Dialog content goes here</p>
  </DialogContent>
</Dialog>
```

### Navigation Components

#### Sheet
Slide-out panels for navigation and secondary content.

```tsx
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'

<Sheet>
  <SheetTrigger asChild>
    <Button>Open Menu</Button>
  </SheetTrigger>
  <SheetContent side="left">
    <SheetHeader>
      <SheetTitle>Navigation</SheetTitle>
    </SheetHeader>
    {/* Navigation items */}
  </SheetContent>
</Sheet>
```

### Feedback Components

#### Toast
Non-intrusive notifications for user feedback.

```tsx
import { toast } from '@/components/ui/use-toast'

// Success notification
toast({
  title: "Success",
  description: "Operation completed successfully"
})

// Error notification  
toast({
  title: "Error",
  description: "Something went wrong",
  variant: "destructive"
})
```

#### Tooltip
Contextual help and additional information.

```tsx
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

<TooltipProvider>
  <Tooltip>
    <TooltipTrigger>
      <Button variant="outline">Hover me</Button>
    </TooltipTrigger>
    <TooltipContent>
      <p>Helpful information</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

## Accessibility

### WCAG 2.1 AA Compliance

All components meet or exceed WCAG 2.1 AA standards:

- **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Keyboard Navigation**: Full keyboard accessibility for all interactive elements
- **Screen Reader Support**: Proper ARIA labels and descriptions
- **Focus Management**: Visible focus indicators and logical tab order

### Focus Management

```tsx
// Focus rings (automatic with Tailwind)
<Button className="focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
  Accessible Button
</Button>

// Custom focus styles
<div className="focus-within:ring-2 focus-within:ring-primary-500">
  <Input />
</div>
```

### Screen Reader Support

```tsx
// Proper labeling
<Input 
  id="email"
  aria-label="Email address"
  aria-describedby="email-help"
/>
<p id="email-help" className="text-sm text-secondary-600">
  We'll never share your email
</p>

// Status announcements
<div role="status" aria-live="polite">
  Form submitted successfully
</div>
```

### Keyboard Navigation

- **Tab**: Navigate between focusable elements
- **Enter/Space**: Activate buttons and controls
- **Escape**: Close modals and dropdowns
- **Arrow Keys**: Navigate within components (menus, tabs)

## Usage Patterns

### Form Design

```tsx
<form className="space-y-6 max-w-md">
  <div className="space-y-2">
    <Label htmlFor="name">Full Name *</Label>
    <Input 
      id="name" 
      required 
      aria-describedby="name-error"
    />
    <p id="name-error" className="text-sm text-error-600">
      This field is required
    </p>
  </div>
  
  <Button type="submit" className="w-full">
    Submit Form
  </Button>
</form>
```

### Card Layouts

```tsx
<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
  {items.map(item => (
    <Card key={item.id}>
      <CardHeader>
        <CardTitle>{item.title}</CardTitle>
        <CardDescription>{item.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm">{item.content}</p>
      </CardContent>
      <CardFooter>
        <Button className="w-full">View Details</Button>
      </CardFooter>
    </Card>
  ))}
</div>
```

### Data Tables

```tsx
<div className="rounded-lg border">
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>Name</TableHead>
        <TableHead>Status</TableHead>
        <TableHead>Actions</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      {data.map(item => (
        <TableRow key={item.id}>
          <TableCell className="font-medium">{item.name}</TableCell>
          <TableCell>
            <Badge variant="success">{item.status}</Badge>
          </TableCell>
          <TableCell>
            <Button size="sm" variant="ghost">Edit</Button>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
</div>
```

## Development Guidelines

### Component Creation

1. **Use Radix UI primitives** for complex interactive components
2. **Follow compound component patterns** for flexibility
3. **Include proper TypeScript types** for all props
4. **Implement accessibility features** from the start
5. **Add Storybook stories** for documentation and testing

### Styling Guidelines

```tsx
// Use design tokens instead of arbitrary values
<div className="p-4 rounded-lg bg-secondary-50"> ✅
<div className="p-[16px] rounded-[8px] bg-gray-100"> ❌

// Responsive design with mobile-first approach
<div className="text-sm md:text-base lg:text-lg"> ✅

// Use semantic color names
<Button variant="destructive"> ✅
<Button className="bg-red-500"> ❌
```

### File Organization

```
src/
├── components/
│   ├── ui/              # Base design system components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── ...
│   └── feature/         # Feature-specific components
├── lib/
│   ├── ui/
│   │   ├── theme.ts     # Design tokens
│   │   └── utils.ts     # Utility functions
└── styles/
    └── globals.css      # Global styles and CSS variables
```

### Testing Strategy

1. **Unit Tests**: Jest + React Testing Library for component logic
2. **Visual Tests**: Storybook for component states and variations
3. **E2E Tests**: Playwright for user workflows
4. **Accessibility Tests**: axe-core integration for a11y validation

### Performance Considerations

- **Tree Shaking**: Import only needed components
- **CSS Optimization**: Tailwind purging and critical CSS
- **Bundle Size**: Monitor component impact on bundle
- **Runtime Performance**: Minimize re-renders and optimize animations

## Component Reference

### Available Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| Button | Primary actions | Variants, sizes, states, icons |
| Input | Form inputs | Types, validation states, icons |
| Select | Dropdowns | Keyboard nav, search, groups |
| Dialog | Modals | Focus trap, backdrop, sizes |
| Sheet | Slide panels | Directions, sizes, persistent |
| Toast | Notifications | Auto-dismiss, actions, variants |
| Tooltip | Help text | Positioning, delays, rich content |
| Card | Content containers | Header/body/footer structure |
| Badge | Status indicators | Variants, sizes, interactive |

### Planned Components

- **DatePicker**: Calendar input with range support
- **Combobox**: Searchable select with custom options  
- **DataTable**: Advanced table with filtering and sorting
- **Navigation**: Breadcrumbs and navigation menus
- **Progress**: Loading and progress indicators
- **Skeleton**: Loading placeholders
- **Pagination**: Page navigation controls

---

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install @radix-ui/react-* lucide-react class-variance-authority
   ```

2. **Configure Tailwind** with the provided `tailwind.config.ts`

3. **Import theme** and use design tokens:
   ```tsx
   import { theme } from '@/lib/ui/theme'
   ```

4. **Use components** from the UI library:
   ```tsx
   import { Button, Input, Dialog } from '@/components/ui'
   ```

5. **Follow accessibility guidelines** and test with screen readers

6. **Add Storybook stories** for new components

For detailed implementation examples and component API documentation, see the individual component files and Storybook stories.

---

*This design system is continuously evolving. For questions or contributions, please refer to the development guidelines and create issues for improvements.*
  <Button>Hover for help</Button>
</Tooltip>
```

## 🧪 Testing & Quality Assurance

