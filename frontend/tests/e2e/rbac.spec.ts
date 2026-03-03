import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@test.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'password123';
const REVIEWER_EMAIL = process.env.E2E_REVIEWER_EMAIL || 'reviewer@test.com';
const VIEWER_EMAIL = process.env.E2E_VIEWER_EMAIL || 'viewer@test.com';
const PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'password123';

// ---------------------------------------------------------------------------
// Viewer role
// ---------------------------------------------------------------------------
test.describe('RBAC – Viewer role', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, VIEWER_EMAIL, PASSWORD);
  });

  test('viewer cannot access admin-only page', async ({ page }) => {
    await page.goto('/admin/users');
    await page.waitForLoadState('networkidle');

    // Either redirected away from /admin, or an unauthorized message is shown (with auto-retry for React render)
    const isRedirected = !page.url().includes('/admin');
    if (!isRedirected) {
      await expect(page.getByText(/403|unauthorized|forbidden|access denied/i)).toBeVisible({
        timeout: 10_000,
      });
    }
  });

  test('viewer can view requirements list', async ({ page }) => {
    await page.goto('/requirements');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/requirements/);
  });

  test('viewer does not see Add Requirement button', async ({ page }) => {
    await page.goto('/requirements');
    await page.waitForLoadState('networkidle');

    const addBtn = page.getByRole('button', { name: /add requirement|new requirement|\+ requirement/i });
    const isVisible = await addBtn.isVisible().catch(() => false);
    expect(isVisible).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Reviewer role
// ---------------------------------------------------------------------------
test.describe('RBAC – Reviewer role', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, REVIEWER_EMAIL, PASSWORD);
  });

  test('reviewer can view requirements', async ({ page }) => {
    await page.goto('/requirements');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/requirements/);
  });

  test('reviewer does not see delete buttons for requirements', async ({ page }) => {
    await page.goto('/requirements');
    await page.waitForLoadState('networkidle');

    const deleteBtn = page.getByRole('button', { name: /delete/i }).first();
    const isVisible = await deleteBtn.isVisible().catch(() => false);
    expect(isVisible).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Admin role
// ---------------------------------------------------------------------------
test.describe('RBAC – Admin role', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
  });

  test('admin can access user management page without 403 or login redirect', async ({ page }) => {
    await page.goto('/admin/users');
    await page.waitForLoadState('networkidle');

    // Should NOT have been redirected to login
    expect(page.url()).not.toMatch(/\/login/);

    // Should NOT see a 403/forbidden page
    const isForbidden = await page.getByText(/403|forbidden|access denied/i).isVisible().catch(() => false);
    expect(isForbidden).toBe(false);
  });
});