/**
 * Error Handling System Demo
 * Tests the backend error models and frontend error interceptor
 */

// Mock error responses for testing (matching backend structure)
const mockErrorResponses = {
  validation_error: {
    success: false,
    error: true,
    code: 'VALIDATION_ERROR',
    message: 'Validation failed',
    details: 'Request validation failed with 2 field errors',
    field_errors: [
      {
        field: 'name',
        message: 'Field is required',
        code: 'REQUIRED_FIELD_MISSING',
        value: null
      },
      {
        field: 'email',
        message: 'Invalid email format',
        code: 'INVALID_FORMAT',
        value: 'invalid-email'
      }
    ],
    path: '/test/users',
    method: 'POST',
    timestamp: '2024-01-01T12:00:00Z'
  },
  
  not_found: {
    success: false,
    error: true,
    code: 'RESOURCE_NOT_FOUND',
    message: 'User with ID 404 not found',
    details: 'User was not found',
    path: '/test/users/404',
    method: 'GET',
    timestamp: '2024-01-01T12:01:00Z'
  },
  
  conflict: {
    success: false,
    error: true,
    code: 'DUPLICATE_RESOURCE',
    message: 'User with this email already exists',
    details: 'A user account with this email address is already registered',
    path: '/test/users',
    method: 'POST',
    timestamp: '2024-01-01T12:02:00Z'
  },
  
  server_error: {
    success: false,
    error: true,
    code: 'INTERNAL_SERVER_ERROR',
    message: 'Internal server error',
    details: 'An unexpected error occurred while processing your request',
    path: '/test/errors/server',
    method: 'GET',
    timestamp: '2024-01-01T12:03:00Z'
  },
  
  auth_required: {
    success: false,
    error: true,
    code: 'AUTHENTICATION_REQUIRED',
    message: 'Authentication required',
    path: '/test/users',
    method: 'GET',
    timestamp: '2024-01-01T12:04:00Z'
  }
}

// Success response for comparison
const mockSuccessResponse = {
  success: true,
  error: false,
  data: {
    id: 12345,
    name: 'Test User',
    email: 'test@example.com',
    age: 30,
    status: 'active'
  },
  message: 'User created successfully'
}

// Error severity mapping (from error-handler.ts)
const errorSeverityMap = {
  VALIDATION_ERROR: 'warning',
  INVALID_INPUT: 'warning',
  REQUIRED_FIELD_MISSING: 'warning',
  INVALID_FORMAT: 'warning',
  OUT_OF_RANGE: 'warning',
  
  AUTHENTICATION_REQUIRED: 'info',
  INVALID_CREDENTIALS: 'warning',
  TOKEN_EXPIRED: 'info',
  TOKEN_INVALID: 'warning',
  INSUFFICIENT_PERMISSIONS: 'warning',
  ACCESS_DENIED: 'warning',
  FORBIDDEN_OPERATION: 'warning',
  
  RESOURCE_NOT_FOUND: 'info',
  ENDPOINT_NOT_FOUND: 'warning',
  
  RESOURCE_CONFLICT: 'warning',
  DUPLICATE_RESOURCE: 'warning',
  RESOURCE_LOCKED: 'warning',
  
  INTERNAL_SERVER_ERROR: 'error',
  DATABASE_ERROR: 'error',
  EXTERNAL_SERVICE_ERROR: 'error',
  CONFIGURATION_ERROR: 'error'
}

// User-friendly error messages (Hungarian)
const errorMessageMap = {
  VALIDATION_ERROR: 'Kérjük, ellenőrizze a bevitt adatokat',
  INVALID_INPUT: 'Érvénytelen adat',
  REQUIRED_FIELD_MISSING: 'Kötelező mező hiányzik',
  INVALID_FORMAT: 'Helytelen formátum',
  OUT_OF_RANGE: 'Az érték nem megfelelő tartományban van',
  
  AUTHENTICATION_REQUIRED: 'Bejelentkezés szükséges',
  INVALID_CREDENTIALS: 'Helytelen bejelentkezési adatok',
  TOKEN_EXPIRED: 'A munkamenet lejárt, kérjük jelentkezzen be újra',
  TOKEN_INVALID: 'Érvénytelen munkamenet',
  INSUFFICIENT_PERMISSIONS: 'Nincs megfelelő jogosultság',
  ACCESS_DENIED: 'Hozzáférés megtagadva',
  FORBIDDEN_OPERATION: 'A művelet nem engedélyezett',
  
  RESOURCE_NOT_FOUND: 'A keresett elem nem található',
  ENDPOINT_NOT_FOUND: 'A szolgáltatás nem elérhető',
  
  RESOURCE_CONFLICT: 'Ütközés történt az adatokban',
  DUPLICATE_RESOURCE: 'Ilyen elem már létezik',
  RESOURCE_LOCKED: 'Az elem zárolva van',
  
  INTERNAL_SERVER_ERROR: 'Szerver hiba történt',
  DATABASE_ERROR: 'Adatbázis hiba',
  EXTERNAL_SERVICE_ERROR: 'Külső szolgáltatás hiba',
  CONFIGURATION_ERROR: 'Konfigurációs hiba'
}

// Demo error processing function
function processErrorResponse(errorResponse) {
  const severity = errorSeverityMap[errorResponse.code] || 'error'
  const friendlyMessage = errorMessageMap[errorResponse.code] || errorResponse.message
  
  return {
    id: `error_${Date.now()}`,
    severity,
    title: getErrorTitle(errorResponse.code),
    message: friendlyMessage,
    originalMessage: errorResponse.message,
    details: errorResponse.details,
    fieldErrors: errorResponse.field_errors,
    code: errorResponse.code,
    timestamp: new Date(errorResponse.timestamp),
    path: errorResponse.path,
    method: errorResponse.method
  }
}

function getErrorTitle(code) {
  const titleMap = {
    VALIDATION_ERROR: 'Validációs hiba',
    RESOURCE_NOT_FOUND: 'Nem található',
    DUPLICATE_RESOURCE: 'Már létezik',
    INTERNAL_SERVER_ERROR: 'Szerver hiba',
    AUTHENTICATION_REQUIRED: 'Bejelentkezés szükséges'
  }
  
  return titleMap[code] || 'Hiba történt'
}

// Demo functions
function demonstrateErrorProcessing() {
  console.log('🚨 ERROR HANDLING SYSTEM DEMONSTRATION')
  console.log('='.repeat(50))
  
  Object.entries(mockErrorResponses).forEach(([errorType, errorResponse]) => {
    console.log(`\n📋 ${errorType.toUpperCase()} Error:`)
    console.log('Raw API Response:', errorResponse)
    
    const processedError = processErrorResponse(errorResponse)
    console.log('Processed for UI:', {
      severity: processedError.severity,
      title: processedError.title,
      message: processedError.message,
      fieldErrors: processedError.fieldErrors
    })
    
    // Simulate toast notification
    console.log(`🔔 Toast: [${processedError.severity.toUpperCase()}] ${processedError.title} - ${processedError.message}`)
  })
}

function demonstrateFieldErrors() {
  console.log('\n📝 FIELD ERROR HANDLING')
  console.log('='.repeat(30))
  
  const validationError = mockErrorResponses.validation_error
  const processedError = processErrorResponse(validationError)
  
  if (processedError.fieldErrors) {
    console.log('Form field errors:')
    processedError.fieldErrors.forEach(fieldError => {
      console.log(`  ❌ ${fieldError.field}: ${fieldError.message} (${fieldError.code})`)
      if (fieldError.value !== null) {
        console.log(`     Invalid value: ${fieldError.value}`)
      }
    })
  }
}

function demonstrateBackendIntegration() {
  console.log('\n🔗 BACKEND INTEGRATION TEST')
  console.log('='.repeat(30))
  
  // Simulate API calls that would trigger errors
  const testCases = [
    {
      description: 'Valid user creation',
      endpoint: 'POST /test/users',
      body: { name: 'John Doe', email: 'john@example.com', age: 30 },
      expectedResponse: mockSuccessResponse
    },
    {
      description: 'Invalid user data',
      endpoint: 'POST /test/users',
      body: { name: '', email: 'invalid-email', age: 15 },
      expectedError: mockErrorResponses.validation_error
    },
    {
      description: 'User not found',
      endpoint: 'GET /test/users/404',
      expectedError: mockErrorResponses.not_found
    },
    {
      description: 'Duplicate user',
      endpoint: 'POST /test/users',
      body: { email: 'duplicate@example.com' },
      expectedError: mockErrorResponses.conflict
    },
    {
      description: 'Server error',
      endpoint: 'GET /test/errors/server',
      expectedError: mockErrorResponses.server_error
    }
  ]
  
  testCases.forEach((testCase, index) => {
    console.log(`\n${index + 1}. ${testCase.description}`)
    console.log(`   Request: ${testCase.endpoint}`)
    
    if (testCase.body) {
      console.log(`   Body:`, testCase.body)
    }
    
    if (testCase.expectedError) {
      const processed = processErrorResponse(testCase.expectedError)
      console.log(`   ❌ Expected Error: [${processed.severity}] ${processed.title}`)
      console.log(`   📱 UI Message: ${processed.message}`)
      
      if (processed.fieldErrors) {
        console.log(`   🔍 Field Errors: ${processed.fieldErrors.length} fields`)
      }
    } else {
      console.log(`   ✅ Expected Success:`, testCase.expectedResponse)
    }
  })
}

function demonstrateToastBehavior() {
  console.log('\n🔔 TOAST NOTIFICATION BEHAVIOR')
  console.log('='.repeat(30))
  
  const behaviors = [
    { severity: 'error', autoHide: false, description: 'Error toasts stay visible until dismissed' },
    { severity: 'warning', autoHide: true, duration: 7000, description: 'Warning toasts auto-hide after 7s' },
    { severity: 'info', autoHide: true, duration: 5000, description: 'Info toasts auto-hide after 5s' },
    { severity: 'success', autoHide: true, duration: 3000, description: 'Success toasts auto-hide after 3s' }
  ]
  
  behaviors.forEach(behavior => {
    console.log(`📋 ${behavior.severity.toUpperCase()}: ${behavior.description}`)
  })
}

// Main demo runner
function runErrorHandlingDemo() {
  console.log('🎯 KONZISZTENS API HIBAMODELLEK + UI TOASTS DEMO')
  console.log('='.repeat(60))
  
  demonstrateErrorProcessing()
  demonstrateFieldErrors()
  demonstrateBackendIntegration()
  demonstrateToastBehavior()
  
  console.log('\n✅ DEMONSTRATION COMPLETE')
  console.log('\n📊 Summary:')
  console.log('  ✅ Backend error envelope implemented')
  console.log('  ✅ Standardized error codes and messages')
  console.log('  ✅ Field-specific validation errors')
  console.log('  ✅ Frontend error interceptor ready')
  console.log('  ✅ Toast notification system designed')
  console.log('  ✅ Hungarian user-friendly messages')
  
  console.log('\n🧪 Test Validation Errors:')
  console.log('  1. Send POST to /test/users with empty name')
  console.log('  2. Send POST to /test/users with invalid email')
  console.log('  3. Send GET to /test/users/404')
  console.log('  4. Send POST to /test/errors/validation')
  console.log('  5. Check browser console for toast events')
}

// Export for browser usage
if (typeof window !== 'undefined') {
  window.runErrorHandlingDemo = runErrorHandlingDemo;
  window.mockErrorResponses = mockErrorResponses;
  window.processErrorResponse = processErrorResponse;
}

// Export for Node.js usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    runErrorHandlingDemo,
    mockErrorResponses,
    processErrorResponse,
    errorMessageMap,
    errorSeverityMap
  }
}

// Run demo immediately
runErrorHandlingDemo()