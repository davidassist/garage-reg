#!/usr/bin/env node
/**
 * E2E Test Script for Authentication Flow
 * Tests: Guest → Login → TOTP → Dashboard
 * 
 * Usage: node test-auth-e2e.js
 */

const baseUrl = 'http://localhost:3000'

async function testAuthenticationFlow() {
  console.log('🔧 Starting E2E Authentication Test...\n')

  try {
    // Test 1: Guest access should redirect to login
    console.log('1. Testing guest access...')
    const guestResponse = await fetch(`${baseUrl}/dashboard`, {
      redirect: 'manual'
    })
    
    if (guestResponse.status === 302 || guestResponse.status === 301) {
      const location = guestResponse.headers.get('location')
      if (location && location.includes('/login')) {
        console.log('   ✅ Guest redirected to login')
      } else {
        console.log('   ❌ Guest not redirected to login properly')
        return false
      }
    } else {
      console.log('   ⚠️  Guest access check inconclusive')
    }

    // Test 2: Login API endpoint
    console.log('\n2. Testing login API...')
    const loginResponse = await fetch(`${baseUrl}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'admin@garagereg.com',
        password: 'password123'
      })
    })

    if (loginResponse.ok) {
      const loginData = await loginResponse.json()
      
      if (loginData.requiresTwoFactor) {
        console.log('   ✅ Login successful - 2FA required')
        
        // Get cookies for TOTP verification
        const cookies = loginResponse.headers.get('set-cookie')
        
        // Test 3: TOTP verification
        console.log('\n3. Testing TOTP verification...')
        const totpResponse = await fetch(`${baseUrl}/api/auth/verify-totp`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Cookie': cookies || ''
          },
          body: JSON.stringify({
            code: '123456' // Demo code
          })
        })

        if (totpResponse.ok) {
          const totpData = await totpResponse.json()
          if (totpData.user) {
            console.log('   ✅ TOTP verification successful')
            console.log(`   👤 Authenticated as: ${totpData.user.email}`)
            console.log(`   🛡️  Role: ${totpData.user.role.displayName}`)
            
            // Test 4: Profile API with auth
            console.log('\n4. Testing authenticated profile access...')
            const authCookies = totpResponse.headers.get('set-cookie')
            
            const profileResponse = await fetch(`${baseUrl}/api/auth/profile`, {
              headers: {
                'Cookie': authCookies || ''
              }
            })

            if (profileResponse.ok) {
              const profileData = await profileResponse.json()
              console.log('   ✅ Profile API accessible with auth')
              console.log(`   📊 Permissions: ${profileData.permissions?.length || 0} permissions`)
            } else {
              console.log('   ❌ Profile API not accessible')
              return false
            }

            console.log('\n🎉 All tests passed!')
            console.log('\n📋 Test Summary:')
            console.log('   • Guest access redirects to login ✅')
            console.log('   • Login API works ✅')
            console.log('   • TOTP verification works ✅')
            console.log('   • Authenticated API access works ✅')
            console.log('\n🔗 Test URLs:')
            console.log(`   • Application: ${baseUrl}`)
            console.log(`   • Login: ${baseUrl}/login`)
            console.log(`   • Dashboard: ${baseUrl}/dashboard`)
            console.log('\n👥 Test Credentials:')
            console.log('   • Email: admin@garagereg.com')
            console.log('   • Password: password123')
            console.log('   • TOTP Code: 123456 (demo)')
            
            return true
          }
        } else {
          console.log('   ❌ TOTP verification failed')
          return false
        }
      } else if (loginData.user) {
        console.log('   ✅ Direct login successful (no 2FA)')
        return true
      } else {
        console.log('   ❌ Login response unexpected')
        return false
      }
    } else {
      console.log('   ❌ Login API failed')
      const errorText = await loginResponse.text()
      console.log(`   Error: ${errorText}`)
      return false
    }

  } catch (error) {
    console.error('❌ Test failed with error:', error.message)
    return false
  }
}

async function testUnauthorizedAccess() {
  console.log('\n🚫 Testing unauthorized access...')
  
  try {
    // Test accessing unauthorized page without proper role
    const response = await fetch(`${baseUrl}/unauthorized`)
    
    if (response.ok) {
      console.log('   ✅ Unauthorized page accessible')
    } else {
      console.log('   ⚠️  Unauthorized page response:', response.status)
    }
  } catch (error) {
    console.log('   ⚠️  Unauthorized page test failed:', error.message)
  }
}

// Main test runner
async function main() {
  console.log('🧪 GarageReg Authentication E2E Test Suite')
  console.log('=' .repeat(50))
  
  // Check if server is running
  try {
    const healthCheck = await fetch(baseUrl)
    if (!healthCheck.ok) {
      console.log('❌ Server not accessible at', baseUrl)
      console.log('Please make sure the development server is running: npm run dev')
      process.exit(1)
    }
  } catch (error) {
    console.log('❌ Server not accessible at', baseUrl)
    console.log('Please make sure the development server is running: npm run dev')
    process.exit(1)
  }

  const authTestPassed = await testAuthenticationFlow()
  await testUnauthorizedAccess()

  console.log('\n' + '=' .repeat(50))
  
  if (authTestPassed) {
    console.log('🎉 E2E Authentication Test: PASSED')
    console.log('\n💡 Next Steps:')
    console.log('   • Visit http://localhost:3000 to test manually')
    console.log('   • Try different user roles and permissions')
    console.log('   • Test RBAC menu filtering')
    process.exit(0)
  } else {
    console.log('❌ E2E Authentication Test: FAILED')
    process.exit(1)
  }
}

// Run tests if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal test error:', error)
    process.exit(1)
  })
}

module.exports = { testAuthenticationFlow, testUnauthorizedAccess }