import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { code } = await request.json()
    const tempSession = request.cookies.get('temp_auth_session')?.value

    if (!tempSession) {
      return NextResponse.json(
        { error: 'No active authentication session' },
        { status: 401 }
      )
    }

    // Validate TOTP code (in real app, verify against user's TOTP secret)
    const validCodes = ['123456', '000000'] // Demo codes
    
    if (!validCodes.includes(code)) {
      return NextResponse.json(
        { error: 'Invalid verification code' },
        { status: 401 }
      )
    }

    // Complete authentication - create real session
    const sessionToken = 'session_' + Math.random().toString(36).substr(2, 16)
    
    const response = NextResponse.json({
      user: {
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
      },
      sessionId: sessionToken
    })
    
    // Remove temp session and set real auth cookie
    response.cookies.delete('temp_auth_session')
    response.cookies.set('auth_token', sessionToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 86400, // 24 hours
    })
    
    return response
    
  } catch (error) {
    console.error('TOTP verification error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}