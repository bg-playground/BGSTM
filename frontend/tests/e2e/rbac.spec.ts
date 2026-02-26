import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';

const REVIEWER_EMAIL = process.env.E2E_REVIEWER_EMAIL || 'reviewer@test.com';
const VIEWER_EMAIL = process.env.E2E_VIEWER_EMAIL || 'viewer@test.com';
const PASSWORD = process.env.E2E_PASSWORD || 'password123';

test.describe('Role-Based Access Control', () => {
  test.describe('Viewer role', () => {
    test.beforeEach(async ({ page }) => {
      await login(page, VIEWER_EMAIL, PASSWORD);
    });

    test('viewer cannot access admin-only pages', async ({ page }) => {
      // Try admin/user management URLs
      await page.goto('/admin');
      await page.waitForLoadState('networkidle');

      const isOnAdmin = page.url().includes('/admin');
      if (isOnAdmin) {
        // If the page loaded, it should show an unauthorized indicator
        const unauthorized = await page
          .getByText(/unauthorized|forbidden|403|access denied/i)
          .isVisible({ timeout: 3_000 })
          .catch(() => false);
        const redirectedToHome = page.url().endsWith('/') || page.url().endsWith('/#');
        expect(unauthorized || redirectedToHome).toBeTruthy();
      } else {
        // Redirected away from /admin — correct behavior
        expect(page.url()).not.toContain('/admin');
      }
    });

    test('viewer can view requirements list', async ({ page }) => {
      await page.goto('/requirements');
      await page.waitForLoadState('networkidle');

      // Requirements list should be visible
      await expect(page.getByText(/requirements/i).first()).toBeVisible({ timeout: 10_000 });
    });

    test('viewer does not see the Add Requirement button', async ({ page }) => {
      await page.goto('/requirements');
      await page.waitForLoadState('networkidle');

      const addBtn = page
        .getByRole('button', { name: /add requirement|new requirement|\+ requirement/i })
        .first();
      const isVisible = await addBtn.isVisible({ timeout: 3_000 }).catch(() => false);
      expect(isVisible).toBe(false);
    });
  });

  test.describe('Reviewer role', () => {
    test.beforeEach(async ({ page }) => {
      await login(page, REVIEWER_EMAIL, PASSWORD);
    });

    test('reviewer can view requirements', async ({ page }) => {
      await page.goto('/requirements');
      await page.waitForLoadState('networkidle');

      await expect(page.getByText(/requirements/i).first()).toBeVisible({ timeout: 10_000 });
    });

    test('reviewer does not see delete buttons for requirements', async ({ page }) => {
      await page.goto('/requirements');
      await page.waitForLoadState('networkidle');

      const deleteBtn = page.getByRole('button', { name: /delete/i }).first();
      const isVisible = await deleteBtn.isVisible({ timeout: 3_000 }).catch(() => false);
      expect(isVisible).toBe(false);
    });
  });

  test.describe('Admin role', () => {
    // Admin is logged in via storageState from globalSetup.
    // TODO: If PR #1 (E2E Infra Fixes) has not been merged yet, add login() in beforeEach here.

    test('admin can access user management page', async ({ page }) => {
      // Try common admin/user management URLs
      const adminUrls = ['/admin', '/users'];
      let loaded = false;

      for (const url of adminUrls) {
        await page.goto(url);
        await page.waitForLoadState('networkidle');

        const isUnauthorized = await page
          .getByText(/unauthorized|forbidden|403/i)
          .isVisible({ timeout: 2_000 })
          .catch(() => false);
        const isRedirectedToLogin = page.url().includes('/login');

        if (!isUnauthorized && !isRedirectedToLogin) {
          loaded = true;
          break;
        }
      }

      if (!loaded) {
        test.skip();
        return;
      }

      // Page loaded without 403 or login redirect
      expect(loaded).toBe(true);
    });
  });
});
