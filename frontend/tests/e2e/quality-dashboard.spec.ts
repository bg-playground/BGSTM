import { expect, test } from '@playwright/test';

import { login } from './helpers/auth';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@test.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'password123';

test.describe('Quality KPI Dashboard', () => {
  test('admin can view KPI charts and navigate back to release readiness', async ({ page }) => {
    const pageErrors: string[] = [];
    page.on('pageerror', (error) => pageErrors.push(error.message));

    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await page.goto('/quality-dashboard');
    await page.waitForLoadState('networkidle');

    await expect(page.getByTestId('quality-dashboard-tile-mttr')).toBeVisible();
    await expect(page.getByTestId('quality-dashboard-chart-defect-trend')).toBeVisible();
    await expect(page.getByTestId('quality-dashboard-chart-pass-rate')).toBeVisible();
    await expect(page.getByTestId('quality-dashboard-chart-defects-by-module')).toBeVisible();
    await expect(page.getByTestId('quality-dashboard-chart-automation-coverage')).toBeVisible();

    await page.getByTestId('quality-dashboard-window-7').click();
    await expect(page.getByTestId('quality-dashboard-chart-defect-trend')).toBeVisible();
    expect(pageErrors).toEqual([]);

    await page.getByRole('link', { name: '← Back to Release Readiness' }).click();
    await expect(page).toHaveURL(/\/release-readiness$/);
  });
});
