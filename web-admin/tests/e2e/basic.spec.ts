import { test, expect } from '@playwright/test'

test.describe('Basic Application Tests', () => {
  test('should load homepage', async ({ page }) => {
    // Navigate to the login page (since app redirects to login)
    await page.goto('/')
    
    // Check that we're redirected to login or the page contains login elements
    await expect(page).toHaveURL(/login|auth/)
    
    // Check for basic elements
    await expect(page.locator('body')).toBeVisible()
  })

  test('should show login form', async ({ page }) => {
    await page.goto('/login')
    
    // Check for login form elements
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })
})