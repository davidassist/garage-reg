import { test, expect } from '@playwright/test'

// Test data
const TEST_USER = {
  username: 'testuser',
  password: 'testpass123'
}

test.describe('Admin Authentication', () => {
  test('should show login form when not authenticated', async ({ page }) => {
    await page.goto('/')
    
    // Should see login form
    await expect(page.locator('h1')).toContainText('Bejelentkezés')
    await expect(page.locator('input[name="username"]')).toBeVisible()
    await expect(page.locator('input[name="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/')
    
    // Fill login form
    await page.fill('input[name="username"]', TEST_USER.username)
    await page.fill('input[name="password"]', TEST_USER.password)
    
    // Submit form
    await page.click('button[type="submit"]')
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.locator('h1')).toContainText('Dashboard')
  })

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/')
    
    // Fill login form with invalid credentials
    await page.fill('input[name="username"]', 'invalid')
    await page.fill('input[name="password"]', 'invalid')
    
    // Submit form
    await page.click('button[type="submit"]')
    
    // Should show error message
    await expect(page.locator('[role="alert"]')).toBeVisible()
    
    // Should stay on login page
    await expect(page.locator('h1')).toContainText('Bejelentkezés')
  })

  test('should logout successfully', async ({ page }) => {
    // First login
    await page.goto('/')
    await page.fill('input[name="username"]', TEST_USER.username)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')
    
    // Wait for dashboard to load
    await expect(page.locator('h1')).toContainText('Dashboard')
    
    // Click logout button
    await page.click('button:has-text("Kijelentkezés")')
    
    // Should redirect to login page
    await expect(page.locator('h1')).toContainText('Bejelentkezés')
  })
})