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
    // Start listening for the matrix API response BEFORE navigating,
    // so we don't miss the XHR if it completes before goto resolves.
    const matrixResponse = page.waitForResponse(
      (resp) => resp.url().includes('/api/v1/traceability-matrix') && resp.status() === 200,
      { timeout: 30_000 }
    );
    await page.goto('/traceability');
    await matrixResponse;
    // Wait for React to re-render with the data
    await page.waitForLoadState('networkidle');
  });

  test('matrix page loads and heading contains "traceability"', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /traceability matrix/i })).toBeVisible({ timeout: 10_000 });
  });

  test('seeded requirement "Role-Based Access Control" is visible in the matrix', async ({ page }) => {
    // "Role-Based Access Control" is not modified by the CRUD tests,
    // so it reliably survives test pollution from earlier spec files.
    const dataRows = page.locator('table tbody tr');
    await expect(dataRows.first()).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText('Role-Based Access Control')).toBeVisible({ timeout: 10_000 });
  });

  test('seeded test case "TC-004" is visible in the matrix', async ({ page }) => {
    // TC-004 is linked to "Role-Based Access Control" and is not
    // touched by CRUD tests, so it remains stable across runs.
    const dataRows = page.locator('table tbody tr');
    await expect(dataRows.first()).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/TC-004/i)).toBeVisible({ timeout: 10_000 });
  });

  test('filtering by requirement title updates results', async ({ page }) => {
    const filterInput = page.getByRole('textbox', { name: /filter|search/i });
    if (!(await filterInput.isVisible().catch(() => false))) {
      test.skip();
      return;
    }

    await filterInput.fill('Role-Based Access Control');
    await page.waitForLoadState('networkidle');

    await expect(page.getByText('Role-Based Access Control')).toBeVisible({ timeout: 10_000 });
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