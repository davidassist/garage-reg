import { test, expect } from '@playwright/test';

/**
 * Admin Dashboard E2E Tests
 * Tests admin functionality and user management
 */

test.describe('Admin Dashboard', () => {
  // Login before each test
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    
    // Login as admin
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);
  });

  test('should display dashboard overview', async ({ page }) => {
    // Check dashboard elements
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="dashboard-stats"]')).toBeVisible();
    
    // Check navigation menu
    await expect(page.locator('[data-testid="nav-organizations"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-users"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-clients"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-sites"]')).toBeVisible();
  });

  test('should display correct statistics', async ({ page }) => {
    // Check that stats cards are visible and have data
    await expect(page.locator('[data-testid="stat-organizations"]')).toBeVisible();
    await expect(page.locator('[data-testid="stat-users"]')).toBeVisible();
    await expect(page.locator('[data-testid="stat-clients"]')).toBeVisible();
    await expect(page.locator('[data-testid="stat-sites"]')).toBeVisible();
    
    // Check that stats have numeric values
    const orgCount = await page.textContent('[data-testid="stat-organizations-count"]');
    expect(parseInt(orgCount || '0')).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Organization Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Navigate to organizations
    await page.click('[data-testid="nav-organizations"]');
    await expect(page).toHaveURL(/.*\/organizations/);
  });

  test('should list organizations', async ({ page }) => {
    // Check organizations list
    await expect(page.locator('[data-testid="organizations-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="organization-item"]').first()).toBeVisible();
    
    // Check table headers
    await expect(page.locator('th:has-text("Name")')).toBeVisible();
    await expect(page.locator('th:has-text("Type")')).toBeVisible();
    await expect(page.locator('th:has-text("Status")')).toBeVisible();
    await expect(page.locator('th:has-text("Actions")')).toBeVisible();
  });

  test('should create new organization', async ({ page }) => {
    // Click create button
    await page.click('[data-testid="create-organization-btn"]');
    
    // Fill organization form
    await expect(page.locator('[data-testid="organization-form"]')).toBeVisible();
    
    await page.fill('input[name="name"]', 'Test E2E Organization');
    await page.fill('input[name="display_name"]', 'Test E2E Org Display');
    await page.selectOption('select[name="organization_type"]', 'company');
    await page.fill('textarea[name="description"]', 'Created via E2E test');
    await page.fill('input[name="address_line_1"]', '123 E2E Test Street');
    await page.fill('input[name="city"]', 'E2E City');
    await page.fill('input[name="country"]', 'E2E Country');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    
    // Verify organization appears in list
    await expect(page.locator('[data-testid="organization-item"]:has-text("Test E2E Organization")')).toBeVisible();
  });

  test('should edit organization', async ({ page }) => {
    // Click edit on first organization
    await page.click('[data-testid="organization-item"] [data-testid="edit-btn"]');
    
    // Update organization
    await expect(page.locator('[data-testid="organization-form"]')).toBeVisible();
    
    await page.fill('input[name="display_name"]', 'Updated E2E Org Display');
    await page.fill('textarea[name="description"]', 'Updated via E2E test');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    
    // Verify changes
    await expect(page.locator('[data-testid="organization-item"]:has-text("Updated E2E Org Display")')).toBeVisible();
  });

  test('should delete organization', async ({ page }) => {
    // Click delete on organization
    await page.click('[data-testid="organization-item"]:last-child [data-testid="delete-btn"]');
    
    // Confirm deletion
    await expect(page.locator('[data-testid="confirm-dialog"]')).toBeVisible();
    await page.click('[data-testid="confirm-delete-btn"]');
    
    // Check success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });

  test('should validate organization form', async ({ page }) => {
    // Click create button
    await page.click('[data-testid="create-organization-btn"]');
    
    // Submit empty form
    await page.click('button[type="submit"]');
    
    // Check validation errors
    await expect(page.locator('[data-testid="name-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="organization-type-error"]')).toBeVisible();
  });
});

test.describe('User Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Navigate to users
    await page.click('[data-testid="nav-users"]');
    await expect(page).toHaveURL(/.*\/users/);
  });

  test('should list users', async ({ page }) => {
    // Check users list
    await expect(page.locator('[data-testid="users-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="user-item"]').first()).toBeVisible();
    
    // Check table headers
    await expect(page.locator('th:has-text("Username")')).toBeVisible();
    await expect(page.locator('th:has-text("Email")')).toBeVisible();
    await expect(page.locator('th:has-text("Role")')).toBeVisible();
    await expect(page.locator('th:has-text("Status")')).toBeVisible();
  });

  test('should create new user', async ({ page }) => {
    // Click create button
    await page.click('[data-testid="create-user-btn"]');
    
    // Fill user form
    await expect(page.locator('[data-testid="user-form"]')).toBeVisible();
    
    await page.fill('input[name="username"]', 'e2euser');
    await page.fill('input[name="email"]', 'e2euser@example.com');
    await page.fill('input[name="first_name"]', 'E2E');
    await page.fill('input[name="last_name"]', 'User');
    await page.fill('input[name="password"]', 'E2EPassword123!');
    await page.fill('input[name="confirm_password"]', 'E2EPassword123!');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    
    // Verify user appears in list
    await expect(page.locator('[data-testid="user-item"]:has-text("e2euser")')).toBeVisible();
  });

  test('should validate password requirements', async ({ page }) => {
    // Click create button
    await page.click('[data-testid="create-user-btn"]');
    
    // Fill form with weak password
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', '123');
    
    // Check password strength indicator
    await expect(page.locator('[data-testid="password-strength"]:has-text("Weak")')).toBeVisible();
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check validation error
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
  });

  test('should deactivate user', async ({ page }) => {
    // Click deactivate on a user
    await page.click('[data-testid="user-item"]:last-child [data-testid="deactivate-btn"]');
    
    // Confirm deactivation
    await expect(page.locator('[data-testid="confirm-dialog"]')).toBeVisible();
    await page.click('[data-testid="confirm-deactivate-btn"]');
    
    // Check success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    
    // Verify user status changed
    await expect(page.locator('[data-testid="user-item"]:last-child [data-testid="status-inactive"]')).toBeVisible();
  });
});

test.describe('Client Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Navigate to clients
    await page.click('[data-testid="nav-clients"]');
    await expect(page).toHaveURL(/.*\/clients/);
  });

  test('should list clients', async ({ page }) => {
    // Check clients list
    await expect(page.locator('[data-testid="clients-list"]')).toBeVisible();
    
    // Check table headers
    await expect(page.locator('th:has-text("Name")')).toBeVisible();
    await expect(page.locator('th:has-text("Client Code")')).toBeVisible();
    await expect(page.locator('th:has-text("Type")')).toBeVisible();
    await expect(page.locator('th:has-text("Contact")')).toBeVisible();
  });

  test('should create new client', async ({ page }) => {
    // Click create button
    await page.click('[data-testid="create-client-btn"]');
    
    // Fill client form
    await expect(page.locator('[data-testid="client-form"]')).toBeVisible();
    
    await page.fill('input[name="name"]', 'E2E Test Client');
    await page.fill('input[name="display_name"]', 'E2E Test Client Corp');
    await page.fill('input[name="client_code"]', 'E2E001');
    await page.selectOption('select[name="client_type"]', 'commercial');
    await page.fill('input[name="contact_name"]', 'John E2E');
    await page.fill('input[name="contact_email"]', 'john@e2eclient.com');
    await page.fill('input[name="contact_phone"]', '+1-555-0199');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    
    // Verify client appears in list
    await expect(page.locator('[data-testid="client-item"]:has-text("E2E Test Client")')).toBeVisible();
  });

  test('should validate unique client code', async ({ page }) => {
    // Try to create client with existing code
    await page.click('[data-testid="create-client-btn"]');
    
    await page.fill('input[name="name"]', 'Duplicate Client');
    await page.fill('input[name="client_code"]', 'TC001'); // Assume this exists
    await page.selectOption('select[name="client_type"]', 'commercial');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check validation error
    await expect(page.locator('[data-testid="client-code-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="client-code-error"]')).toContainText('already exists');
  });

  test('should search clients', async ({ page }) => {
    // Use search functionality
    await page.fill('input[name="search"]', 'Test');
    
    // Wait for search results
    await page.waitForTimeout(500);
    
    // All visible clients should contain "Test" in name
    const clientItems = page.locator('[data-testid="client-item"]');
    const count = await clientItems.count();
    
    for (let i = 0; i < count; i++) {
      const clientText = await clientItems.nth(i).textContent();
      expect(clientText?.toLowerCase()).toContain('test');
    }
  });
});

test.describe('Data Export/Import', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Navigate to data export/import
    await page.click('[data-testid="nav-data-transfer"]');
    await expect(page).toHaveURL(/.*\/data-transfer/);
  });

  test('should export data', async ({ page }) => {
    // Configure export
    await page.click('[data-testid="export-tab"]');
    await expect(page.locator('[data-testid="export-form"]')).toBeVisible();
    
    // Select format
    await page.selectOption('select[name="format"]', 'jsonl');
    
    // Select tables
    await page.check('input[name="include_tables"][value="organizations"]');
    await page.check('input[name="include_tables"][value="users"]');
    await page.check('input[name="include_tables"][value="clients"]');
    
    // Start export
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-btn"]');
    
    // Wait for download
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/export.*\.jsonl/);
    
    // Check success message
    await expect(page.locator('[data-testid="export-success"]')).toBeVisible();
  });

  test('should import data', async ({ page }) => {
    // Switch to import tab
    await page.click('[data-testid="import-tab"]');
    await expect(page.locator('[data-testid="import-form"]')).toBeVisible();
    
    // Mock file upload
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test-import.jsonl',
      mimeType: 'application/x-jsonl',
      buffer: Buffer.from('{"_metadata": {"export_id": "test"}}\n{"_table": "organizations", "id": 999, "name": "Test Import Org"}')
    });
    
    // Select import strategy
    await page.selectOption('select[name="strategy"]', 'overwrite');
    
    // Enable dry run
    await page.check('input[name="dry_run"]');
    
    // Start import
    await page.click('[data-testid="import-btn"]');
    
    // Check validation results
    await expect(page.locator('[data-testid="import-preview"]')).toBeVisible();
    await expect(page.locator('[data-testid="import-stats"]')).toBeVisible();
    
    // Confirm import (disable dry run)
    await page.uncheck('input[name="dry_run"]');
    await page.click('[data-testid="confirm-import-btn"]');
    
    // Check success message
    await expect(page.locator('[data-testid="import-success"]')).toBeVisible();
  });

  test('should validate import file', async ({ page }) => {
    // Switch to import tab
    await page.click('[data-testid="import-tab"]');
    
    // Upload invalid file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'invalid.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('invalid content')
    });
    
    // Try to import
    await page.click('[data-testid="import-btn"]');
    
    // Check validation error
    await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="validation-error"]')).toContainText('Invalid file format');
  });
});

test.describe('Performance and Responsiveness', () => {
  test('should load pages quickly', async ({ page }) => {
    await page.goto('/');
    
    // Login
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    
    const startTime = Date.now();
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);
    const loadTime = Date.now() - startTime;
    
    // Should load within reasonable time
    expect(loadTime).toBeLessThan(5000); // 5 seconds
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/');
    
    // Login
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Check mobile navigation
    await expect(page.locator('[data-testid="mobile-menu-btn"]')).toBeVisible();
    
    // Open mobile menu
    await page.click('[data-testid="mobile-menu-btn"]');
    await expect(page.locator('[data-testid="mobile-nav"]')).toBeVisible();
    
    // Test navigation
    await page.click('[data-testid="mobile-nav-organizations"]');
    await expect(page).toHaveURL(/.*\/organizations/);
  });

  test('should handle large data sets', async ({ page }) => {
    await page.goto('/');
    
    // Login
    await page.fill('input[name="username"]', 'testadmin');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Navigate to a list with pagination
    await page.click('[data-testid="nav-clients"]');
    
    // Check pagination controls
    if (await page.locator('[data-testid="pagination"]').isVisible()) {
      // Test pagination
      await page.click('[data-testid="next-page-btn"]');
      await expect(page.locator('[data-testid="page-info"]')).toContainText('Page 2');
      
      // Test different page sizes
      await page.selectOption('select[name="page_size"]', '50');
      await page.waitForTimeout(1000); // Wait for reload
      
      // Should show more items per page
      const itemCount = await page.locator('[data-testid="client-item"]').count();
      expect(itemCount).toBeLessThanOrEqual(50);
    }
  });
});