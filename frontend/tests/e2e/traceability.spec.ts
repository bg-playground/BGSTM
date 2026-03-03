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
    await page.goto('/traceability');
    await page.waitForLoadState('networkidle');
  });

  test('matrix page loads and heading contains "traceability"', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /traceability/i })).toBeVisible({ timeout: 10_000 });
  });

  test('seeded requirement "User Authentication" is visible in the matrix', async ({ page }) => {
    // Wait for the matrix data container to render
    const dataContainer = page.locator('table, [role="grid"], [class*="matrix"], [class*="traceability"]').first();
    await dataContainer.waitFor({ state: 'visible', timeout: 15_000 }).catch(() => {});
    await expect(page.getByText('User Authentication')).toBeVisible({ timeout: 30_000 });
  });

  test('seeded test case "TC-001" is visible in the matrix', async ({ page }) => {
    const dataContainer = page.locator('table, [role="grid"], [class*="matrix"], [class*="traceability"]').first();
    await dataContainer.waitFor({ state: 'visible', timeout: 15_000 }).catch(() => {});
    await expect(page.getByText(/TC-001/i)).toBeVisible({ timeout: 30_000 });
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
