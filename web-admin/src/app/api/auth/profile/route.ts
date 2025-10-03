import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const authToken = request.cookies.get('auth_token')?.value

    if (!authToken) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      )
    }

    // In real app, validate JWT and get user from database
    // For demo, return mock user data
    const user = {
      id: '1',
      email: 'admin@garagereg.com',
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
    }
    
    return NextResponse.json(user)
    
  } catch (error) {
    console.error('Profile fetch error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}