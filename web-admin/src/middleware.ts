import { NextRequest, NextResponse } from 'next/server'
import { jwtVerify } from 'jose'

// Define protected routes
const protectedRoutes = [
  '/dashboard',
  '/users', 
  '/vehicles',
  '/registrations',
  '/analytics',
  '/settings',
  '/audit',
  '/clients',
  '/sites',
  '/buildings',
  '/gates'
]

// Define admin-only routes
const adminRoutes = [
  '/users',
  '/settings',
  '/audit'
]

// Define super admin routes  
const superAdminRoutes = [
  '/settings/system'
]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Skip middleware for public routes
  if (
    pathname.startsWith('/api/') ||
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/favicon') ||
    pathname === '/login' ||
    pathname === '/unauthorized'
  ) {
    return NextResponse.next()
  }

  // Check if route is protected
  const isProtectedRoute = protectedRoutes.some(route => 
    pathname.startsWith(route)
  )

  if (!isProtectedRoute) {
    return NextResponse.next()
  }

  // Get auth token from httpOnly cookie
  const token = request.cookies.get('auth-token')?.value

  if (!token) {
    // No token, redirect to login
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('callbackUrl', pathname)
    return NextResponse.redirect(loginUrl)
  }

  try {
    // Verify JWT token
    const secret = new TextEncoder().encode(
      process.env.JWT_SECRET || 'your-secret-key'
    )

    const { payload } = await jwtVerify(token, secret)
    
    // Extract user data from token
    const user = payload.user as any
    
    if (!user) {
      throw new Error('Invalid token payload')
    }

    // Check role-based access
    const userRoles = user.roles?.map((role: any) => role.name) || []

    // Check admin routes
    if (adminRoutes.some(route => pathname.startsWith(route))) {
      const hasAdminAccess = userRoles.includes('admin') || userRoles.includes('super_admin')
      if (!hasAdminAccess) {
        return NextResponse.redirect(new URL('/unauthorized', request.url))
      }
    }

    // Check super admin routes
    if (superAdminRoutes.some(route => pathname.startsWith(route))) {
      const hasSuperAdminAccess = userRoles.includes('super_admin')
      if (!hasSuperAdminAccess) {
        return NextResponse.redirect(new URL('/unauthorized', request.url))
      }
    }

    // Add user info to headers for server components
    const requestHeaders = new Headers(request.headers)
    requestHeaders.set('x-user-id', user.id)
    requestHeaders.set('x-user-email', user.email)
    requestHeaders.set('x-user-roles', JSON.stringify(userRoles))

    return NextResponse.next({
      request: {
        headers: requestHeaders
      }
    })

  } catch (error) {
    console.error('Auth middleware error:', error)
    
    // Invalid token, redirect to login
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('callbackUrl', pathname)
    return NextResponse.redirect(loginUrl)
  }
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}