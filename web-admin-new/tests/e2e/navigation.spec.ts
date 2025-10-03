import { test, expect } from '@playwright/test'

const TEST_USER = {
  username: 'testuser',
  password: 'testpass123'
}

// Helper function to login
async function login(page: any) {
  await page.goto('/')
  await page.fill('input[name="username"]', TEST_USER.username)
  await page.fill('input[name="password"]', TEST_USER.password)
  await page.click('button[type="submit"]')
  await expect(page.locator('h1')).toContainText('Dashboard')
}

test.describe('Protected Routes and RBAC', () => {
  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    await page.goto('/clients')
    
    // Should redirect to login
    await expect(page.locator('h1')).toContainText('Bejelentkezés')
  })

  test('should access dashboard after login', async ({ page }) => {
    await login(page)
    
    // Should be on dashboard
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.locator('h1')).toContainText('Dashboard')
    
    // Should show stats cards
    await expect(page.locator('text=Ügyfelek')).toBeVisible()
    await expect(page.locator('text=Telephelyek')).toBeVisible()
    await expect(page.locator('text=Épületek')).toBeVisible()
    await expect(page.locator('text=Kapuk')).toBeVisible()
  })

  test('should navigate to clients page with proper permissions', async ({ page }) => {
    await login(page)
    
    // Navigate to clients
    await page.click('text=Ügyfelek')
    
    // Should be on clients page
    await expect(page).toHaveURL(/\/clients/)
    await expect(page.locator('h1')).toContainText('Ügyfelek')
  })

  test('should navigate to sites page with proper permissions', async ({ page }) => {
    await login(page)
    
    // Navigate to sites
    await page.click('text=Telephelyek')
    
    // Should be on sites page
    await expect(page).toHaveURL(/\/sites/)
    await expect(page.locator('h1')).toContainText('Telephelyek')
  })

  test('should navigate to buildings page with proper permissions', async ({ page }) => {
    await login(page)
    
    // Navigate to buildings
    await page.click('text=Épületek')
    
    // Should be on buildings page
    await expect(page).toHaveURL(/\/buildings/)
    await expect(page.locator('h1')).toContainText('Épületek')
  })

  test('should navigate to gates page with proper permissions', async ({ page }) => {
    await login(page)
    
    // Navigate to gates
    await page.click('text=Kapuk')
    
    // Should be on gates page
    await expect(page).toHaveURL(/\/gates/)
    await expect(page.locator('h1')).toContainText('Kapuk')
  })

  test('should show proper navigation menu items', async ({ page }) => {
    await login(page)
    
    // Check that all expected nav items are visible
    await expect(page.locator('nav >> text=Dashboard')).toBeVisible()
    await expect(page.locator('nav >> text=Ügyfelek')).toBeVisible()
    await expect(page.locator('nav >> text=Telephelyek')).toBeVisible()
    await expect(page.locator('nav >> text=Épületek')).toBeVisible()
    await expect(page.locator('nav >> text=Kapuk')).toBeVisible()
  })

  test('should show user info in sidebar', async ({ page }) => {
    await login(page)
    
    // Should show user info
    await expect(page.locator('text=testuser')).toBeVisible()
    await expect(page.locator('button:has-text("Kijelentkezés")')).toBeVisible()
  })

  test('should handle mobile navigation', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    await login(page)
    
    // Mobile menu button should be visible
    await expect(page.locator('button[aria-label="menu"], button:has([data-lucide="menu"])')).toBeVisible()
    
    // Sidebar should be hidden initially on mobile
    await expect(page.locator('nav')).toHaveClass(/translate-x-\[-\w+\]/)
  })
})

test.describe('Dashboard Functionality', () => {
  test('should display dashboard stats', async ({ page }) => {
    await login(page)
    
    // Should show stats cards with numbers
    await expect(page.locator('text=Ügyfelek')).toBeVisible()
    await expect(page.locator('text=Telephelyek')).toBeVisible()
    await expect(page.locator('text=Épületek')).toBeVisible()
    await expect(page.locator('text=Kapuk')).toBeVisible()
    
    // Should show additional stats
    await expect(page.locator('text=Függő ellenőrzések')).toBeVisible()
    await expect(page.locator('text=Lejárt ellenőrzések')).toBeVisible()
    await expect(page.locator('text=Aktív munkarendelések')).toBeVisible()
    await expect(page.locator('text=Befejezett')).toBeVisible()
  })

  test('should display upcoming inspections section', async ({ page }) => {
    await login(page)
    
    // Should show upcoming inspections card
    await expect(page.locator('text=Közelgő ellenőrzések')).toBeVisible()
  })
})