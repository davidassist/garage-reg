# GarageReg Design System & Web Admin

A comprehensive design system and modern web-based administration panel built with Next.js, React, and TypeScript.

## 🎨 Design System

### Core Principles
- **OKLCH-based color palette** for perceptual uniformity and better gamut coverage
- **Automatic light/dark theme support** with semantic color tokens
- **High contrast accessibility** (WCAG AA compliance)
- **Focus-visible rings** on all interactive elements
- **Keyboard navigation** support throughout

### Design Tokens

#### Color Scales (OKLCH)
```css
/* Gray Scale */
--gray-50: oklch(98% 0.005 285);
--gray-100: oklch(95% 0.010 285);
--gray-500: oklch(57% 0.030 285);  /* True gray */
--gray-900: oklch(15% 0.010 285);

/* Primary (Brand Blue) */
--primary-50: oklch(97% 0.020 240);
--primary-500: oklch(56% 0.120 240);  /* Main brand */
--primary-900: oklch(24% 0.060 240);

/* Semantic Colors */
--success-500: oklch(60% 0.130 145);  /* Green */
--warning-500: oklch(70% 0.150 85);   /* Orange */
--error-500: oklch(55% 0.180 25);     /* Red */
--info-500: oklch(60% 0.120 220);     /* Blue */
```

## 🏗️ Web Admin Features

- 🔐 Authentication & Authorization
- 🚪 Gate Management Dashboard  
- 🔧 Maintenance Scheduling & Tracking
- 👥 User Management
- 📊 Analytics & Reporting
- 📱 Responsive Design
- 🌙 Dark/Light Mode Support
- 🌍 Internationalization (HU/EN)
- ♿ Full Accessibility Support

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI Library**: Custom Design System + Radix UI + Tailwind CSS
- **Authentication**: NextAuth.js
- **State Management**: Zustand
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Development Setup

1. **Install dependencies**:
   ```bash
   cd web-admin
   npm install
   ```

2. **Setup environment**:
   ```bash
   cp .env.example .env.local
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

4. **Open browser**: http://localhost:3000

## Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript check

# Testing
npm run test         # Run tests
npm run test:watch   # Run tests in watch mode
npm run test:coverage # Run tests with coverage
```

## Project Structure

```
web-admin/
├── app/                    # Next.js app directory
│   ├── (auth)/            # Authentication pages
│   ├── (dashboard)/       # Dashboard pages
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx          # Home page
├── components/            # Reusable components
│   ├── ui/               # UI components (shadcn/ui)
│   └── forms/            # Form components
├── lib/                  # Utility libraries
│   ├── api.ts           # API client
│   ├── auth.ts          # Authentication config
│   └── utils.ts         # Utility functions
├── hooks/                # Custom React hooks
├── stores/               # Zustand stores
├── types/                # TypeScript type definitions
└── public/              # Static assets
```

## Environment Variables

See `.env.example` for all available environment variables.

## Deployment

The application is containerized and can be deployed using Docker:

```bash
# Build Docker image
docker build -t garagereg-web-admin .

# Run container
docker run -p 3000:3000 garagereg-web-admin
```