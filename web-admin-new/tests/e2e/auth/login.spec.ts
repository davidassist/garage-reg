import { test, expect } from '@playwright/test';

/**
 * Authentication E2E Tests
 * Tests user authentication flows in the web admin interface
 */

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test('should display login page', async ({ page }) => {
    // Check if login form is visible
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
    
    // Check form elements
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
    
    // Check page title
    await expect(page).toHaveTitle(/GarageReg.*Login/);
  });

  test('should show validation errors for empty form', async ({ page }) => {
    // Click submit without filling form
    await page.click('button[type="submit"]');
    
    // Check for validation errors
    await expect(page.locator('[data-testid="username-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Fill form with invalid credentials
    await page.fill('input[name="username"]', 'invaliduser');
    await page.fill('input[name="password"]', 'wrongpassword');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check for authentication error
    await expect(page.locator('[data-testid="auth-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="auth-error"]')).toContainText('Invalid');
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    // Fill form with valid test credentials
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Check for dashboard elements
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test('should show loading state during login', async ({ page }) => {
    // Intercept login API call to add delay
    await page.route('**/api/v1/auth/login', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1s delay
      await route.continue();
    });
    
    // Fill and submit form
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Check for loading state
    await expect(page.locator('[data-testid="login-loading"]')).toBeVisible();
    
    // Wait for loading to complete
    await expect(page.locator('[data-testid="login-loading"]')).toBeHidden();
  });

  test('should remember login state after page refresh', async ({ page, context }) => {
    // Login first
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Refresh page
    await page.reload();
    
    // Should still be on dashboard (not redirected to login)
    await expect(page).toHaveURL(/.*\/dashboard/);
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Click user menu
    await page.click('[data-testid="user-menu"]');
    
    // Click logout
    await page.click('[data-testid="logout-button"]');
    
    // Should redirect to login page
    await expect(page).toHaveURL(/.*\/login/);
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    // Try to access dashboard directly without login
    await page.goto('/dashboard');
    
    // Should redirect to login
    await expect(page).toHaveURL(/.*\/login/);
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });

  test('should handle session expiration', async ({ page }) => {
    // Login first
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Mock expired token response
    await page.route('**/api/v1/**', async (route) => {
      if (route.request().headers().authorization) {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Token expired' })
        });
      } else {
        await route.continue();
      }
    });
    
    // Try to make an API call (e.g., click on a menu item)
    await page.click('[data-testid="organizations-menu"]');
    
    // Should redirect to login due to expired token
    await expect(page).toHaveURL(/.*\/login/);
    await expect(page.locator('[data-testid="session-expired-message"]')).toBeVisible();
  });

  test('should show password strength indicator', async ({ page }) => {
    // Navigate to registration page (if exists)
    await page.goto('/register');
    
    // If register page doesn't exist, skip this test
    const registerForm = page.locator('[data-testid="register-form"]');
    if (!(await registerForm.isVisible())) {
      test.skip('Registration page not available');
    }
    
    const passwordField = page.locator('input[name="password"]');
    const strengthIndicator = page.locator('[data-testid="password-strength"]');
    
    // Test weak password
    await passwordField.fill('123');
    await expect(strengthIndicator).toContainText('Weak');
    
    // Test medium password
    await passwordField.fill('password123');
    await expect(strengthIndicator).toContainText('Medium');
    
    // Test strong password
    await passwordField.fill('SecurePassword123!');
    await expect(strengthIndicator).toContainText('Strong');
  });

  test('should handle forgot password flow', async ({ page }) => {
    // Click forgot password link
    const forgotPasswordLink = page.locator('[data-testid="forgot-password-link"]');
    
    if (await forgotPasswordLink.isVisible()) {
      await forgotPasswordLink.click();
      
      // Should navigate to forgot password page
      await expect(page).toHaveURL(/.*\/forgot-password/);
      
      // Check forgot password form
      await expect(page.locator('[data-testid="forgot-password-form"]')).toBeVisible();
      await expect(page.locator('input[name="email"]')).toBeVisible();
      
      // Test form submission
      await page.fill('input[name="email"]', 'test@example.com');
      await page.click('button[type="submit"]');
      
      // Check success message
      await expect(page.locator('[data-testid="forgot-password-success"]')).toBeVisible();
    } else {
      test.skip('Forgot password feature not available');
    }
  });
});

test.describe('Authentication Security', () => {
  test('should prevent XSS in login form', async ({ page }) => {
    // Try to inject script in username field
    const xssPayload = '<script>alert("XSS")</script>';
    
    await page.fill('input[name="username"]', xssPayload);
    await page.fill('input[name="password"]', 'password');
    await page.click('button[type="submit"]');
    
    // Check that script was not executed
    page.on('dialog', async dialog => {
      // If XSS worked, this would trigger
      expect(dialog.message()).not.toBe('XSS');
      await dialog.dismiss();
    });
    
    // Verify the input was sanitized
    const usernameValue = await page.inputValue('input[name="username"]');
    expect(usernameValue).not.toContain('<script>');
  });

  test('should prevent SQL injection attempts', async ({ page }) => {
    // Try SQL injection patterns
    const sqlInjectionPayloads = [
      "' OR '1'='1",
      "'; DROP TABLE users; --",
      "admin'--"
    ];
    
    for (const payload of sqlInjectionPayloads) {
      await page.fill('input[name="username"]', payload);
      await page.fill('input[name="password"]', 'password');
      await page.click('button[type="submit"]');
      
      // Should show normal authentication error, not database error
      await expect(page.locator('[data-testid="auth-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="auth-error"]')).not.toContainText('database');
      await expect(page.locator('[data-testid="auth-error"]')).not.toContainText('SQL');
      
      // Clear form for next test
      await page.fill('input[name="username"]', '');
    }
  });

  test('should enforce rate limiting on login attempts', async ({ page }) => {
    const maxAttempts = 5;
    
    // Make multiple failed login attempts
    for (let i = 0; i < maxAttempts + 2; i++) {
      await page.fill('input[name="username"]', 'testuser');
      await page.fill('input[name="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');
      
      // Wait a bit between attempts
      await page.waitForTimeout(500);
    }
    
    // Should show rate limit error after too many attempts
    await expect(page.locator('[data-testid="rate-limit-error"]')).toBeVisible();
    
    // Login button should be disabled
    await expect(page.locator('button[type="submit"]')).toBeDisabled();
  });

  test('should secure token storage', async ({ page, context }) => {
    // Login to get token
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Wait for login to complete
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Check that token is not visible in localStorage (should be httpOnly cookie or secure storage)
    const localStorage = await page.evaluate(() => {
      return JSON.stringify(window.localStorage);
    });
    
    // Token should not be stored in localStorage as plain text
    expect(localStorage).not.toContain('access_token');
    expect(localStorage).not.toContain('bearer');
  });
});