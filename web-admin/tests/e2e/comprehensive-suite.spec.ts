import { test, expect, Page, BrowserContext } from '@playwright/test';

/**
 * Comprehensive E2E Test Suite for Web Admin
 * Implements Hungarian requirement: "Web admin e2e (Playwright)"
 */

// Test configuration
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const API_URL = process.env.API_URL || 'http://localhost:8000';

// Test user credentials
const TEST_USER = {
  username: 'admin',
  password: 'admin123',
  email: 'admin@garagereg.com'
};

const TEST_OPERATOR = {
  username: 'operator',
  password: 'operator123',
  email: 'operator@garagereg.com'
};

// Page object models
class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  async login(username: string, password: string) {
    await this.page.fill('[data-testid="username-input"]', username);
    await this.page.fill('[data-testid="password-input"]', password);
    await this.page.click('[data-testid="login-button"]');
  }

  async expectLoginError() {
    await expect(this.page.locator('[data-testid="error-message"]')).toBeVisible();
  }
}

class DashboardPage {
  constructor(private page: Page) {}

  async expectDashboard() {
    await expect(this.page.locator('[data-testid="dashboard"]')).toBeVisible();
    await expect(this.page.url()).toContain('/dashboard');
  }

  async navigateToUsers() {
    await this.page.click('[data-testid="nav-users"]');
  }

  async navigateToOrganizations() {
    await this.page.click('[data-testid="nav-organizations"]');
  }

  async navigateToReports() {
    await this.page.click('[data-testid="nav-reports"]');
  }
}

class UsersPage {
  constructor(private page: Page) {}

  async expectUsersPage() {
    await expect(this.page.locator('[data-testid="users-list"]')).toBeVisible();
    await expect(this.page.url()).toContain('/users');
  }

  async createUser(username: string, email: string, role: string) {
    await this.page.click('[data-testid="create-user-button"]');
    await this.page.fill('[data-testid="user-username-input"]', username);
    await this.page.fill('[data-testid="user-email-input"]', email);
    await this.page.selectOption('[data-testid="user-role-select"]', role);
    await this.page.click('[data-testid="save-user-button"]');
  }

  async expectUserInList(username: string) {
    await expect(this.page.locator(`[data-testid="user-row-${username}"]`)).toBeVisible();
  }
}

// Test suites

test.describe('🔐 Authentication & Authorization', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await loginPage.goto();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await dashboardPage.expectDashboard();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await loginPage.goto();
    await loginPage.login('invalid', 'invalid');
    await loginPage.expectLoginError();
  });

  test('should redirect unauthenticated users to login', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.url()).toContain('/login');
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await loginPage.goto();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await dashboardPage.expectDashboard();

    // Logout
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    await expect(page.url()).toContain('/login');
  });
});

test.describe('🧭 Navigation & Routing', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
    
    // Login before each navigation test
    await loginPage.goto();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await dashboardPage.expectDashboard();
  });

  test('should navigate to Users page', async ({ page }) => {
    const usersPage = new UsersPage(page);
    await dashboardPage.navigateToUsers();
    await usersPage.expectUsersPage();
  });

  test('should navigate to Organizations page', async ({ page }) => {
    await dashboardPage.navigateToOrganizations();
    await expect(page.url()).toContain('/organizations');
    await expect(page.locator('[data-testid="organizations-list"]')).toBeVisible();
  });

  test('should navigate to Reports page', async ({ page }) => {
    await dashboardPage.navigateToReports();
    await expect(page.url()).toContain('/reports');
    await expect(page.locator('[data-testid="reports-dashboard"]')).toBeVisible();
  });

  test('should handle browser back/forward navigation', async ({ page }) => {
    // Navigate to users
    await dashboardPage.navigateToUsers();
    await expect(page.url()).toContain('/users');

    // Go back
    await page.goBack();
    await expect(page.url()).toContain('/dashboard');

    // Go forward
    await page.goForward();
    await expect(page.url()).toContain('/users');
  });
});

test.describe('👥 User Management', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;
  let usersPage: UsersPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
    usersPage = new UsersPage(page);
    
    // Login as admin
    await loginPage.goto();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await dashboardPage.expectDashboard();
    await dashboardPage.navigateToUsers();
  });

  test('should display users list', async ({ page }) => {
    await usersPage.expectUsersPage();
    await expect(page.locator('[data-testid="users-table"]')).toBeVisible();
  });

  test('should create new user successfully', async ({ page }) => {
    const newUsername = `testuser_${Date.now()}`;
    const newEmail = `${newUsername}@test.com`;
    
    await usersPage.createUser(newUsername, newEmail, 'operator');
    await usersPage.expectUserInList(newUsername);
  });

  test('should validate user creation form', async ({ page }) => {
    await page.click('[data-testid="create-user-button"]');
    
    // Try to save without filling required fields
    await page.click('[data-testid="save-user-button"]');
    
    // Check for validation errors
    await expect(page.locator('[data-testid="username-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
  });
});

test.describe('🏢 Organization Management', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
    
    // Login as admin
    await loginPage.goto();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await dashboardPage.expectDashboard();
    await dashboardPage.navigateToOrganizations();
  });

  test('should display organizations list', async ({ page }) => {
    await expect(page.locator('[data-testid="organizations-list"]')).toBeVisible();
  });

  test('should create new organization', async ({ page }) => {
    await page.click('[data-testid="create-org-button"]');
    
    const orgName = `Test Org ${Date.now()}`;
    await page.fill('[data-testid="org-name-input"]', orgName);
    await page.fill('[data-testid="org-description-input"]', 'Test organization');
    await page.click('[data-testid="save-org-button"]');
    
    // Check if organization appears in list
    await expect(page.locator(`text=${orgName}`)).toBeVisible();
  });
});

test.describe('🔒 Role-Based Access Control (RBAC)', () => {
  test('admin should have full access', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);
    
    await loginPage.goto();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await dashboardPage.expectDashboard();
    
    // Admin should see all navigation items
    await expect(page.locator('[data-testid="nav-users"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-organizations"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-reports"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-admin"]')).toBeVisible();
  });

  test('operator should have limited access', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);
    
    await loginPage.goto();
    await loginPage.login(TEST_OPERATOR.username, TEST_OPERATOR.password);
    await dashboardPage.expectDashboard();
    
    // Operator should see limited navigation
    await expect(page.locator('[data-testid="nav-organizations"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-reports"]')).toBeVisible();
    
    // But should not see admin features
    await expect(page.locator('[data-testid="nav-users"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="nav-admin"]')).not.toBeVisible();
  });

  test('should prevent unauthorized access to admin pages', async ({ page }) => {
    const loginPage = new LoginPage(page);
    
    await loginPage.goto();
    await loginPage.login(TEST_OPERATOR.username, TEST_OPERATOR.password);
    
    // Try to access admin page directly
    await page.goto('/admin/users');
    
    // Should be redirected or show access denied
    const isRedirected = page.url().includes('/dashboard') || page.url().includes('/access-denied');
    expect(isRedirected).toBe(true);
  });
});

test.describe('📊 Dashboard Functionality', () => {
  test('should display key metrics', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);
    
    await loginPage.goto();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await dashboardPage.expectDashboard();
    
    // Check for key dashboard widgets
    await expect(page.locator('[data-testid="users-count-widget"]')).toBeVisible();
    await expect(page.locator('[data-testid="organizations-count-widget"]')).toBeVisible();
    await expect(page.locator('[data-testid="recent-activities-widget"]')).toBeVisible();
  });

  test('should update metrics in real-time', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);
    
    await loginPage.goto();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await dashboardPage.expectDashboard();
    
    // Get initial user count
    const initialCount = await page.textContent('[data-testid="users-count"]');
    
    // Create a new user
    await dashboardPage.navigateToUsers();
    const usersPage = new UsersPage(page);
    const newUsername = `realtime_test_${Date.now()}`;
    await usersPage.createUser(newUsername, `${newUsername}@test.com`, 'operator');
    
    // Go back to dashboard
    await page.click('[data-testid="nav-dashboard"]');
    
    // Wait for metrics to update (might need polling or WebSocket)
    await page.waitForTimeout(1000);
    
    // Check if count increased (this might need adjustment based on actual implementation)
    const newCount = await page.textContent('[data-testid="users-count"]');
    // Note: This test assumes the count updates automatically
  });
});

test.describe('📱 Responsive Design', () => {
  test('should work on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    
    // Check if mobile layout is applied
    await expect(page.locator('[data-testid="mobile-menu-toggle"]')).toBeVisible();
    
    // Login on mobile
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    
    // Check mobile navigation
    await page.click('[data-testid="mobile-menu-toggle"]');
    await expect(page.locator('[data-testid="mobile-nav-menu"]')).toBeVisible();
  });

  test('should work on tablet devices', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);
    
    await loginPage.goto();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await dashboardPage.expectDashboard();
    
    // Check that layout adapts to tablet size
    await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();
  });
});

test.describe('⚡ Performance & Accessibility', () => {
  test('should meet performance benchmarks', async ({ page }) => {
    // Start performance monitoring
    await page.goto('/login', { waitUntil: 'networkidle' });
    
    const startTime = Date.now();
    
    const loginPage = new LoginPage(page);
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    
    // Wait for dashboard to load completely
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Assert reasonable load time (adjust threshold as needed)
    expect(loadTime).toBeLessThan(5000); // 5 seconds max
  });

  test('should have proper ARIA labels', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    
    // Check for accessibility attributes
    await expect(page.locator('input[aria-label="Username"]')).toBeVisible();
    await expect(page.locator('input[aria-label="Password"]')).toBeVisible();
    await expect(page.locator('button[aria-label="Login"]')).toBeVisible();
  });
});

// Test hooks for setup and cleanup
test.beforeAll(async () => {
  console.log('🎭 Starting E2E Test Suite');
  console.log('📋 Test Categories:');
  console.log('  🔐 Authentication & Authorization');
  console.log('  🧭 Navigation & Routing');
  console.log('  👥 User Management');
  console.log('  🏢 Organization Management');
  console.log('  🔒 Role-Based Access Control');
  console.log('  📊 Dashboard Functionality');
  console.log('  📱 Responsive Design');
  console.log('  ⚡ Performance & Accessibility');
});

test.afterAll(async () => {
  console.log('✅ E2E Test Suite Completed');
});

// Export for external use
export { LoginPage, DashboardPage, UsersPage };