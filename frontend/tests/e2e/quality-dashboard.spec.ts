import { expect, test } from '@playwright/test';

import { login } from './helpers/auth';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@test.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'password123';
const DASHBOARD_HEADING = /quality kpi dashboard/i;

test.describe('Quality KPI Dashboard', () => {
  test('admin can view KPI charts and navigate back to release readiness', async ({ page }) => {
    const pageErrors: string[] = [];
    page.on('pageerror', (error) => pageErrors.push(error.message));

    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await page.goto('/quality-dashboard');
    await page.getByRole('heading', { name: DASHBOARD_HEADING }).waitFor({ timeout: 30_000 });

    await expect(page.getByTestId('quality-dashboard-tile-mttr')).toBeVisible();
    await expect(page.getByTestId('quality-dashboard-chart-defect-trend')).toBeVisible();
    await expect(page.getByTestId('quality-dashboard-chart-pass-rate')).toBeVisible();
    await expect(page.getByTestId('quality-dashboard-chart-defects-by-module')).toBeVisible();
    await expect(page.getByTestId('quality-dashboard-chart-automation-coverage')).toBeVisible();
    await expect(page.getByTestId('quality-dashboard-chart-coverage-vs-defects')).toBeVisible();
    await expect(page.getByTestId('quality-dashboard-chart-recurring-defects')).toBeVisible();

    await page.getByTestId('quality-dashboard-window-7').click();
    await expect(page).toHaveURL(/window=7/, { timeout: 10_000 });
    await expect(page.getByTestId('quality-dashboard-chart-defect-trend')).toBeVisible();
    expect(pageErrors).toEqual([]);

    await page.getByRole('link', { name: '← Back to Release Readiness' }).click();
    await expect(page).toHaveURL(/\/release-readiness$/);
  });

  test('window query param survives reload', async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await page.goto('/quality-dashboard?window=7');
    await page.getByRole('heading', { name: DASHBOARD_HEADING }).waitFor({ timeout: 30_000 });

    await expect(page.getByTestId('quality-dashboard-window-7')).toHaveClass(/bg-slate-900/);

    await page.reload();
    await page.getByRole('heading', { name: DASHBOARD_HEADING }).waitFor({ timeout: 30_000 });
    await expect(page).toHaveURL(/window=7/);
    await expect(page.getByTestId('quality-dashboard-window-7')).toHaveClass(/bg-slate-900/);
  });

  test('stored window is used when visiting without query params', async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await page.goto('/quality-dashboard');
    await page.getByRole('heading', { name: DASHBOARD_HEADING }).waitFor({ timeout: 30_000 });

    await page.getByTestId('quality-dashboard-window-90').click();
    await expect(page).toHaveURL(/window=90/, { timeout: 10_000 });

    await page.goto('/quality-dashboard');
    await page.getByRole('heading', { name: DASHBOARD_HEADING }).waitFor({ timeout: 30_000 });
    await expect(page).toHaveURL(/\/quality-dashboard$/);
    await expect(page.getByTestId('quality-dashboard-window-90')).toHaveClass(/bg-slate-900/);
  });

  test('invalid window param falls back to stored value', async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await page.goto('/quality-dashboard');
    await page.getByRole('heading', { name: DASHBOARD_HEADING }).waitFor({ timeout: 30_000 });

    await page.getByTestId('quality-dashboard-window-90').click();
    await expect(page).toHaveURL(/window=90/, { timeout: 10_000 });

    await page.goto('/quality-dashboard?window=999');
    await page.getByRole('heading', { name: DASHBOARD_HEADING }).waitFor({ timeout: 30_000 });
    await expect(page.getByTestId('quality-dashboard-window-90')).toHaveClass(/bg-slate-900/);
  });
});