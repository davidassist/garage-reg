import { defineConfig, devices } from '@playwright/test';

/**
 * Headless Playwright Configuration for Automated Testing
 * No webServer dependency - focuses on test logic validation
 */
export default defineConfig({
  testDir: './tests/e2e',
  
  /* Test output directory */
  outputDir: './test-results',
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  
  /* Global timeout for each test */
  timeout: 30000,
  
  /* Global timeout for expect assertions */
  expect: {
    timeout: 5000,
  },
  
  /* Reporter configuration */
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list'],
  ],
  
  /* Shared settings for all projects */
  use: {
    /* Base URL - not used in headless mode */
    baseURL: 'http://localhost:3000',
    
    /* Browser context options */
    viewport: { width: 1280, height: 720 },
    
    /* Collect trace when retrying the failed test */
    trace: 'on-first-retry',
    
    /* Record video on failure */
    video: 'retain-on-failure',
    
    /* Take screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Ignore HTTPS errors */
    ignoreHTTPSErrors: true,
    
    /* Action timeout */
    actionTimeout: 10000,
    
    /* Navigation timeout */
    navigationTimeout: 15000,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  /* No webServer - tests run independently */
});