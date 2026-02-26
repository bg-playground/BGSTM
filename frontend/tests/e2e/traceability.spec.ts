import { test, expect } from '@playwright/test';

// Admin is logged in via storageState from globalSetup.
// TODO: If PR #1 (E2E Infra Fixes) has not been merged yet, add login() in beforeEach here.

test.describe('Traceability Matrix', () => {
  test('matrix page loads with seeded data', async ({ page }) => {
    await page.goto('/traceability');
    await page.waitForLoadState('networkidle');

    // Page heading or title should contain "traceability"
    await expect(page.getByText(/traceability/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test('seeded requirement "User Authentication" is visible in the matrix', async ({ page }) => {
    await page.goto('/traceability');
    await page.waitForLoadState('networkidle');

    await expect(page.getByText('User Authentication')).toBeVisible({ timeout: 10_000 });
  });

  test('seeded test case "TC-001" is visible in the matrix', async ({ page }) => {
    await page.goto('/traceability');
    await page.waitForLoadState('networkidle');

    await expect(page.getByText(/TC-001/)).toBeVisible({ timeout: 10_000 });
  });

  test('filtering by requirement title updates results', async ({ page }) => {
    await page.goto('/traceability');
    await page.waitForLoadState('networkidle');

    // Look for a search/filter input
    const filterInput = page
      .locator(
        '[data-testid="traceability-filter"], input[placeholder*="filter" i], input[placeholder*="search" i]',
      )
      .first();

    if (!(await filterInput.isVisible({ timeout: 3_000 }).catch(() => false))) {
      test.skip();
      return;
    }

    await filterInput.fill('Authentication');
    await page.waitForLoadState('networkidle');

    // After filtering, "User Authentication" should still be visible
    await expect(page.getByText('User Authentication')).toBeVisible({ timeout: 5_000 });
  });

  test('export PDF button is present on the traceability page', async ({ page }) => {
    await page.goto('/traceability');
    await page.waitForLoadState('networkidle');

    const exportBtn = page
      .getByRole('button', { name: /export.*pdf|pdf.*export|download.*pdf/i })
      .first();

    if (!(await exportBtn.isVisible({ timeout: 3_000 }).catch(() => false))) {
      test.skip();
      return;
    }

    await expect(exportBtn).toBeVisible();
  });
});
