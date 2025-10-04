import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from '@/lib/providers'
import '@/styles/globals.css'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: {
    template: '%s | GarageReg Admin',
    default: 'GarageReg Admin - Vehicle Registration Management',
  },
  description: 'Comprehensive vehicle registration management system for garages and automotive businesses.',
  keywords: ['vehicle registration', 'garage management', 'automotive', 'admin panel'],
  authors: [{ name: 'GarageReg Team' }],
  creator: 'GarageReg',
  publisher: 'GarageReg',
  
  // Open Graph / Facebook
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
    siteName: 'GarageReg Admin',
    title: 'GarageReg Admin - Vehicle Registration Management',
    description: 'Comprehensive vehicle registration management system for garages and automotive businesses.',
    images: [
      {
        url: '/images/og-image.png',
        width: 1200,
        height: 630,
        alt: 'GarageReg Admin Dashboard',
      },
    ],
  },
  
  // Twitter
  twitter: {
    card: 'summary_large_image',
    title: 'GarageReg Admin - Vehicle Registration Management',
    description: 'Comprehensive vehicle registration management system for garages and automotive businesses.',
    images: ['/images/twitter-image.png'],
    creator: '@garagereg',
  },
  
  // Progressive Web App
  manifest: '/manifest.json',
  
  // Theme colors
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0f172a' },
  ],
  
  // Viewport
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
  },
  
  // Icons
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
    other: [
      {
        rel: 'mask-icon',
        url: '/safari-pinned-tab.svg',
        color: '#2563eb',
      },
    ],
  },
  
  // Robots
  robots: {
    index: false, // Admin panel should not be indexed
    follow: false,
    nocache: true,
    googleBot: {
      index: false,
      follow: false,
      noimageindex: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  
  // Additional meta tags
  other: {
    'msapplication-TileColor': '#2563eb',
    'msapplication-config': '/browserconfig.xml',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        {/* Preconnect to improve performance */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        
        {/* Security headers */}
        <meta httpEquiv="X-Content-Type-Options" content="nosniff" />
        <meta httpEquiv="X-Frame-Options" content="DENY" />
        <meta httpEquiv="X-XSS-Protection" content="1; mode=block" />
        
        {/* DNS prefetch for API domain */}
        <link rel="dns-prefetch" href={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'} />
        
        {/* Favicon */}
        <link rel="shortcut icon" href="/favicon.ico" />
        
        {/* Theme color for mobile browsers */}
        <meta name="theme-color" content="#2563eb" />
        <meta name="msapplication-navbutton-color" content="#2563eb" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        
        {/* Prevent zoom on iOS */}
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0" />
      </head>
      <body className={`${inter.className} font-sans antialiased`}>
        {/* Skip to main content for accessibility */}
        <a 
          href="#main-content" 
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary-600 text-white px-4 py-2 rounded-md z-50"
        >
          Skip to main content
        </a>
        
        {/* React Query and other providers */}
        <Providers>
          <div id="main-content">
            {children}
          </div>
        </Providers>
        
        {/* Development tools */}
        {process.env.NODE_ENV === 'development' && (
          <div id="development-tools" />
        )}
        
        {/* Analytics placeholder */}
        {process.env.NODE_ENV === 'production' && (
          <>
            {/* Add your analytics script here */}
            <script
              dangerouslySetInnerHTML={{
                __html: `
                  // Analytics initialization
                  console.log('Production environment detected');
                `,
              }}
            />
          </>
        )}
      </body>
    </html>
  )
}