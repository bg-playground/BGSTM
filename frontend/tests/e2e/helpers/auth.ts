import type { Page } from '@playwright/test';

const AUTH_TIMEOUT_MS = 30_000;

/**
 * Log in via the UI login form and wait for navigation to the dashboard.
 * Relies on the baseURL configured in playwright.config.ts.
 */
export async function login(page: Page, email: string, password: string): Promise<void> {
  // Clear any stale auth state from previous tests
  await page.context().clearCookies();

  await page.goto('/login');
  await page.waitForLoadState('load');

  // Clear localStorage after navigating to a real page (avoids SecurityError on about:blank)
  await page.evaluate(() => localStorage.clear());

  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password').fill(password);

  // Click sign in and wait for the API response
  await Promise.all([
    page.waitForResponse(
      (resp) => resp.url().includes('/api/v1/auth/login') && resp.status() === 200,
      { timeout: AUTH_TIMEOUT_MS },
    ),
    page.getByRole('button', { name: /sign in/i }).click(),
  ]);

  // Wait until redirected away from the login page
  await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: AUTH_TIMEOUT_MS });
}

/**
 * Log out by clicking the Sign Out button in the navigation bar.
 */
export async function logout(page: Page): Promise<void> {
  await page.getByRole('button', { name: /sign out/i }).click();
  await page.waitForURL('**/login', { timeout: AUTH_TIMEOUT_MS });
  // Clear auth state to prevent leakage
  await page.evaluate(() => localStorage.clear());
}