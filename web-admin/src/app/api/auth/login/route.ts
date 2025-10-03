import { NextRequest, NextResponse } from 'next/server'
import { User, UserRole, PermissionResource, PermissionAction } from '@/lib/auth/types'

// Mock user database
const mockUsers = [
  {
    id: '1',
    email: 'admin@garagereg.com',
    password: 'password123', // In real app, this would be hashed
    name: 'Admin User',
    role: {
      id: '1',
      name: 'super_admin',
      displayName: 'Super Administrator',
      permissions: [
        { id: '1', name: 'all', resource: '*', action: '*' }
      ]
    },
    permissions: [
      { id: '1', name: 'all', resource: '*', action: '*' }
    ],
    twoFactorEnabled: true,
    webauthnEnabled: false,
    lastLoginAt: new Date(),
  },
  {
    id: '2',
    email: 'manager@garagereg.com',
    password: 'manager123',
    name: 'Manager User',
    role: {
      id: '2',
      name: 'manager',
      displayName: 'Manager',
      permissions: [
        { id: '2', name: 'vehicles_manage', resource: 'vehicles', action: '*' },
        { id: '3', name: 'registrations_manage', resource: 'registrations', action: '*' },
        { id: '4', name: 'analytics_read', resource: 'analytics', action: 'read' },
      ]
    },
    permissions: [
      { id: '2', name: 'vehicles_manage', resource: 'vehicles', action: '*' },
      { id: '3', name: 'registrations_manage', resource: 'registrations', action: '*' },
      { id: '4', name: 'analytics_read', resource: 'analytics', action: 'read' },
    ],
    twoFactorEnabled: false,
    webauthnEnabled: true,
    lastLoginAt: new Date(),
  }
]

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    // Find user
    const user = mockUsers.find(u => u.email === email)
    
    if (!user || user.password !== password) {
      return NextResponse.json(
        { error: 'Invalid email or password' },
        { status: 401 }
      )
    }

    // Check if 2FA is required
    if (user.twoFactorEnabled) {
      // Create a temporary session for 2FA
      const tempSessionId = 'temp_session_' + Math.random().toString(36).substr(2, 9)
      
      // In a real app, store this in Redis/database with expiration
      const response = NextResponse.json({
        requiresTwoFactor: true,
        sessionId: tempSessionId,
      })
      
      // Set temporary auth cookie
      response.cookies.set('temp_auth_session', tempSessionId, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 300, // 5 minutes
      })
      
      return response
    }

    // Check if WebAuthn is required
    if (user.webauthnEnabled) {
      const tempSessionId = 'temp_webauthn_' + Math.random().toString(36).substr(2, 9)
      
      const response = NextResponse.json({
        requiresWebAuthn: true,
        sessionId: tempSessionId,
      })
      
      response.cookies.set('temp_auth_session', tempSessionId, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 300, // 5 minutes
      })
      
      return response
    }

    // Direct login (no 2FA/WebAuthn)
    const sessionToken = 'session_' + Math.random().toString(36).substr(2, 16)
    
    const response = NextResponse.json({
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        permissions: user.permissions,
        twoFactorEnabled: user.twoFactorEnabled,
        webauthnEnabled: user.webauthnEnabled,
        lastLoginAt: user.lastLoginAt,
      }
    })
    
    // Set auth cookie
    response.cookies.set('auth_token', sessionToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 86400, // 24 hours
    })
    
    return response
    
  } catch (error) {
    console.error('Login error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}