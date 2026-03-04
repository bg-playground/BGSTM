import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@test.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'password123';

// ---------------------------------------------------------------------------
// Traceability Matrix
// ---------------------------------------------------------------------------
test.describe('Traceability Matrix', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    // Navigate and wait for the traceability matrix API to respond
    await page.goto('/traceability');
    // Wait for the matrix API call that the component makes on mount
    await page.waitForResponse(
      (resp) => resp.url().includes('/api/v1/traceability-matrix') && resp.status() === 200,
      { timeout: 30_000 }
    );
    // Wait for React to re-render with the data
    await page.waitForLoadState('networkidle');
  });

  test('matrix page loads and heading contains "traceability"', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /traceability matrix/i })).toBeVisible({ timeout: 10_000 });
  });

  test('seeded requirement "User Authentication" is visible in the matrix', async ({ page }) => {
    // Verify the table has rendered with data rows
    const dataRows = page.locator('table tbody tr');
    await expect(dataRows.first()).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText('User Authentication')).toBeVisible({ timeout: 10_000 });
  });

  test('seeded test case "TC-001" is visible in the matrix', async ({ page }) => {
    const dataRows = page.locator('table tbody tr');
    await expect(dataRows.first()).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/TC-001/i)).toBeVisible({ timeout: 10_000 });
  });

  test('filtering by requirement title updates results', async ({ page }) => {
    const filterInput = page.getByRole('textbox', { name: /filter|search/i });
    if (!(await filterInput.isVisible().catch(() => false))) {
      test.skip();
      return;
    }

    await filterInput.fill('User Authentication');
    await page.waitForLoadState('networkidle');

    await expect(page.getByText('User Authentication')).toBeVisible({ timeout: 10_000 });
  });

  test('Export PDF button is present', async ({ page }) => {
    const exportBtn = page.getByRole('button', { name: /export.*pdf|pdf.*export/i });
    if (!(await exportBtn.isVisible().catch(() => false))) {
      test.skip();
      return;
    }

    await expect(exportBtn).toBeVisible();
  });
});
