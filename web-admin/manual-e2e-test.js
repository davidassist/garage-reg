#!/usr/bin/env node

/**
 * GarageReg Admin Application E2E Smoke Test
 * Manual test runner for validating core functionality
 */

const http = require('http')
const https = require('https')
const { spawn } = require('child_process')

console.log('🚀 GarageReg Admin Application E2E Smoke Test')
console.log('=' .repeat(50))

// Test scenarios
const testScenarios = [
  {
    name: 'Authentication System',
    tests: [
      'Login page loads',
      'Invalid credentials show error',
      'Valid credentials redirect to dashboard',
      'Logout functionality works'
    ]
  },
  {
    name: 'RBAC & Protected Routes',
    tests: [
      'Unauthenticated users redirected to login',
      'Admin users can access all pages',
      'Manager users have limited access',
      'Permission guards work correctly'
    ]
  },
  {
    name: 'Core CRUD Operations',
    tests: [
      'Clients page loads with data',
      'Sites filtering by client works',
      'Buildings filtering by site works',
      'Gates filtering by building works'
    ]
  },
  {
    name: 'User Interface',
    tests: [
      'Navigation menu functions correctly',
      'Mobile responsive design',
      'Search and filters work',
      'Error states display properly'
    ]
  }
]

// Test user accounts
const testUsers = {
  admin: {
    email: 'admin@garagereg.com',
    password: 'password123',
    expectedAccess: ['clients', 'sites', 'buildings', 'gates', 'dashboard']
  },
  manager: {
    email: 'manager@garagereg.com', 
    password: 'manager123',
    expectedAccess: ['clients', 'sites', 'dashboard']
  },
  user: {
    email: 'user@garagereg.com',
    password: 'user123',
    expectedAccess: ['dashboard']
  }
}

function checkServerRunning(port = 3000) {
  return new Promise((resolve) => {
    const req = http.get(`http://localhost:${port}`, (res) => {
      resolve(true)
    })
    
    req.on('error', () => {
      resolve(false)
    })
    
    req.setTimeout(2000, () => {
      req.destroy()
      resolve(false)
    })
  })
}

async function runManualTest() {
  console.log('\n📋 Pre-flight Checks')
  console.log('-' .repeat(30))
  
  // Check if dev server is running
  const serverRunning = await checkServerRunning(3000)
  
  if (!serverRunning) {
    console.log('❌ Dev server not running on port 3000')
    console.log('   Please run: npm run dev')
    process.exit(1)
  }
  
  console.log('✅ Dev server is running on port 3000')
  
  // Display test scenarios
  console.log('\n🧪 Test Scenarios to Validate Manually')
  console.log('-' .repeat(40))
  
  testScenarios.forEach((scenario, index) => {
    console.log(`\n${index + 1}. ${scenario.name}`)
    scenario.tests.forEach((test, testIndex) => {
      console.log(`   ${String.fromCharCode(97 + testIndex)}. ${test}`)
    })
  })
  
  // Display test users
  console.log('\n👥 Test User Accounts')
  console.log('-' .repeat(25))
  
  Object.entries(testUsers).forEach(([role, user]) => {
    console.log(`\n${role.toUpperCase()}:`)
    console.log(`   Email: ${user.email}`)
    console.log(`   Password: ${user.password}`)
    console.log(`   Expected Access: ${user.expectedAccess.join(', ')}`)
  })
  
  // Manual test steps
  console.log('\n📝 Manual Test Steps')
  console.log('-' .repeat(25))
  
  const steps = [
    '1. Open browser and navigate to http://localhost:3000',
    '2. Verify redirect to login page',
    '3. Try invalid credentials - should show error',
    '4. Login with admin credentials',
    '5. Verify dashboard loads with statistics',
    '6. Navigate to Clients page',
    '7. Verify client list loads',
    '8. Click on a client\'s sites count',
    '9. Verify sites page with filtered data',
    '10. Click on a site\'s buildings',
    '11. Verify buildings page with filtered data',
    '12. Click on a building\'s gates',
    '13. Verify gates page with filtered data',
    '14. Test navigation breadcrumbs',
    '15. Test responsive design (resize window)',
    '16. Test logout functionality',
    '17. Repeat with manager and user accounts',
    '18. Verify access restrictions per role'
  ]
  
  steps.forEach(step => console.log(`   ${step}`))
  
  // Expected results
  console.log('\n✅ Expected Results')
  console.log('-' .repeat(20))
  
  const expectedResults = [
    'Login page displays with form fields',
    'Invalid login shows error message',
    'Valid login redirects to dashboard',
    'Dashboard shows statistics cards',
    'Navigation between pages works smoothly',
    'Data filtering works correctly',
    'RBAC permissions are enforced',
    'Responsive design works on mobile',
    'No console errors in browser',
    'All pages load within reasonable time'
  ]
  
  expectedResults.forEach((result, index) => {
    console.log(`   ${index + 1}. ${result}`)
  })
  
  console.log('\n🎯 Success Criteria')
  console.log('-' .repeat(20))
  console.log('   ✅ All authentication flows work')
  console.log('   ✅ RBAC correctly restricts access')
  console.log('   ✅ Data hierarchy navigation functions')
  console.log('   ✅ UI is responsive and accessible')
  console.log('   ✅ No critical errors in console')
  
  console.log('\n🔗 Useful Links')
  console.log('-' .repeat(16))
  console.log('   Application: http://localhost:3000')
  console.log('   Login: http://localhost:3000/login') 
  console.log('   Dashboard: http://localhost:3000/dashboard')
  console.log('   Clients: http://localhost:3000/clients')
  console.log('   Sites: http://localhost:3000/sites')
  console.log('   Buildings: http://localhost:3000/buildings')
  console.log('   Gates: http://localhost:3000/gates')
  
  console.log('\n' + '=' .repeat(50))
  console.log('🎉 Manual E2E Test Guide Complete!')
  console.log('   Follow the steps above to validate the application.')
  console.log('   Report any issues or unexpected behavior.')
  console.log('=' .repeat(50))
}

// Run the test
runManualTest().catch(console.error)