import { test, expect, type Page } from '@playwright/test'

// Test user credentials
const testUsers = {
  admin: {
    email: 'admin@garagereg.com',
    password: 'password123',
    role: 'super_admin',
    permissions: ['*:*']
  },
  manager: {
    email: 'manager@garagereg.com', 
    password: 'manager123',
    role: 'manager',
    permissions: ['vehicles:*', 'registrations:*', 'analytics:read']
  },
  user: {
    email: 'user@garagereg.com',
    password: 'user123', 
    role: 'user',
    permissions: ['vehicles:read']
  }
}

// Helper functions
async function login(page: Page, userType: keyof typeof testUsers = 'admin') {
  const user = testUsers[userType]
  
  await page.goto('/login')
  
  // Fill login form
  await page.fill('input[name="email"]', user.email)
  await page.fill('input[name="password"]', user.password)
  await page.click('button[type="submit"]')
  
  // Wait for redirect to dashboard
  await page.waitForURL(/\/dashboard/)
}

async function logout(page: Page) {
  // Look for user menu or logout button
  await page.click('[data-testid="user-menu"]')
  await page.click('[data-testid="logout-button"]')
  
  // Wait for redirect to login
  await page.waitForURL(/\/login/)
}

test.describe('Authentication Flow', () => {
  test('should allow valid user to login', async ({ page }) => {
    await page.goto('/login')
    
    // Check login form is visible
    await expect(page.locator('h1')).toContainText(['Bejelentkezés', 'Login'])
    await expect(page.locator('input[name="email"]')).toBeVisible()
    await expect(page.locator('input[name="password"]')).toBeVisible()
    
    // Login with admin user
    await login(page, 'admin')
    
    // Should be redirected to dashboard
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.locator('h1')).toContainText(['Dashboard', 'Irányítópult'])
  })

  test('should reject invalid credentials', async ({ page }) => {
    await page.goto('/login')
    
    // Try invalid credentials
    await page.fill('input[name="email"]', 'invalid@example.com')
    await page.fill('input[name="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')
    
    // Should stay on login page with error
    await expect(page).toHaveURL(/\/login/)
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible({ timeout: 5000 })
  })

  test('should logout successfully', async ({ page }) => {
    await login(page, 'admin')
    
    // Should be on dashboard
    await expect(page).toHaveURL(/\/dashboard/)
    
    await logout(page)
    
    // Should be redirected to login
    await expect(page).toHaveURL(/\/login/)
  })
})

test.describe('Protected Routes & RBAC', () => {
  test('should redirect unauthenticated users to login', async ({ page }) => {
    // Try to access protected routes without authentication
    const protectedRoutes = ['/dashboard', '/clients', '/sites', '/buildings', '/gates']
    
    for (const route of protectedRoutes) {
      await page.goto(route)
      await expect(page).toHaveURL(/\/login/)
    }
  })

  test('admin should access all pages', async ({ page }) => {
    await login(page, 'admin')
    
    // Test navigation to all main sections
    const adminRoutes = [
      { path: '/dashboard', title: ['Dashboard', 'Irányítópult'] },
      { path: '/clients', title: ['Ügyfelek', 'Clients'] },
      { path: '/sites', title: ['Telephelyek', 'Sites'] },
      { path: '/buildings', title: ['Épületek', 'Buildings'] },
      { path: '/gates', title: ['Kapuk', 'Gates'] }
    ]
    
    for (const route of adminRoutes) {
      await page.goto(route.path)
      await expect(page).toHaveURL(new RegExp(route.path))
      
      // Check that we're not redirected to unauthorized page
      await expect(page).not.toHaveURL(/\/unauthorized/)
      
      // Check page content loads
      await page.waitForLoadState('networkidle')
      await expect(page.locator('body')).toContainText(route.title)
    }
  })

  test('manager should access vehicle and registration pages', async ({ page }) => {
    await login(page, 'manager')
    
    // Manager should access these pages
    const allowedRoutes = ['/dashboard', '/clients', '/sites']
    
    for (const route of allowedRoutes) {
      await page.goto(route)
      await expect(page).toHaveURL(new RegExp(route))
      await expect(page).not.toHaveURL(/\/unauthorized/)
    }
  })

  test('regular user should have limited access', async ({ page }) => {
    await login(page, 'user')
    
    // User should only access dashboard and read-only pages
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/\/dashboard/)
    
    // Try to access admin-only sections - should be redirected or show error
    const restrictedRoutes = ['/buildings', '/gates']
    
    for (const route of restrictedRoutes) {
      await page.goto(route)
      
      // Should either redirect to unauthorized or show access denied
      const isUnauthorized = await page.locator('text=unauthorized').isVisible({ timeout: 3000 }).catch(() => false)
      const isAccessDenied = await page.locator('text=nincs jogosultsága').isVisible({ timeout: 3000 }).catch(() => false)
      
      expect(isUnauthorized || isAccessDenied).toBeTruthy()
    }
  })
})

test.describe('Dashboard Smoke Test', () => {
  test('should load dashboard with key metrics', async ({ page }) => {
    await login(page, 'admin')
    
    // Check dashboard elements
    await expect(page.locator('h1')).toContainText(['Dashboard', 'Irányítópult'])
    
    // Check for statistics cards
    const expectedCards = ['Ügyfelek', 'Telephelyek', 'Épületek', 'Kapuk']
    
    for (const cardTitle of expectedCards) {
      await expect(page.locator(`text=${cardTitle}`)).toBeVisible({ timeout: 10000 })
    }
    
    // Check for charts or activity feed
    const hasCharts = await page.locator('[data-testid="chart"]').count() > 0
    const hasActivity = await page.locator('[data-testid="activity-feed"]').count() > 0
    
    expect(hasCharts || hasActivity).toBeTruthy()
  })

  test('should show expiring inspections alert', async ({ page }) => {
    await login(page, 'admin')
    
    // Look for inspection alerts or upcoming tasks
    const hasExpiringAlerts = await page.locator('text=lejáró').isVisible().catch(() => false)
    const hasUpcoming = await page.locator('text=közelgő').isVisible().catch(() => false)
    const hasInspections = await page.locator('text=ellenőrzés').isVisible().catch(() => false)
    
    // At least one inspection-related element should be visible
    expect(hasExpiringAlerts || hasUpcoming || hasInspections).toBeTruthy()
  })
})

test.describe('Navigation & UI', () => {
  test('should have working navigation menu', async ({ page }) => {
    await login(page, 'admin')
    
    // Check main navigation is present
    await expect(page.locator('nav')).toBeVisible()
    
    // Test navigation links
    const navLinks = ['Dashboard', 'Ügyfelek', 'Telephelyek', 'Épületek', 'Kapuk']
    
    for (const linkText of navLinks) {
      const link = page.locator(`nav a:has-text("${linkText}")`)
      if (await link.isVisible()) {
        await link.click()
        await page.waitForLoadState('networkidle')
        
        // Should navigate successfully
        await expect(page).not.toHaveURL(/\/login/)
      }
    }
  })

  test('should be responsive on mobile', async ({ page, browserName }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    await login(page, 'admin')
    
    // Check mobile navigation (hamburger menu)
    const mobileMenuButton = page.locator('[data-testid="mobile-menu-button"]')
    if (await mobileMenuButton.isVisible()) {
      await mobileMenuButton.click()
      
      // Mobile menu should open
      await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible()
    }
  })
})

test.describe('Error Handling', () => {
  test('should handle network errors gracefully', async ({ page }) => {
    await login(page, 'admin')
    
    // Simulate network failure by going offline
    await page.context().setOffline(true)
    
    // Try to navigate to a page
    await page.goto('/clients')
    
    // Should show appropriate error message
    const hasErrorMessage = await page.locator('text=hiba').isVisible().catch(() => false)
    const hasOfflineMessage = await page.locator('text=kapcsolat').isVisible().catch(() => false)
    
    expect(hasErrorMessage || hasOfflineMessage).toBeTruthy()
    
    // Restore connection
    await page.context().setOffline(false)
  })

  test('should show 404 page for invalid routes', async ({ page }) => {
    await login(page, 'admin')
    
    await page.goto('/nonexistent-page')
    
    // Should show 404 or not found page
    await expect(page.locator('text=404')).toBeVisible({ timeout: 5000 })
  })
})