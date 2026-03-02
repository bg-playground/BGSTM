import type { Page } from '@playwright/test';

const AUTH_TIMEOUT_MS = 30_000;

/**
 * Log in via the UI login form and wait for navigation to the dashboard.
 * Relies on the baseURL configured in playwright.config.ts.
 */
export async function login(page: Page, email: string, password: string): Promise<void> {
  // Clear stale state before login
  await page.context().clearCookies();
  await page.goto('/login');
  await page.evaluate(() => localStorage.clear());

  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password').fill(password);

  // Wait for the login API response and button click together
  await Promise.all([
    page.waitForResponse(
      (resp) => resp.url().includes('/api/v1/auth/login') && resp.status() === 200,
      { timeout: AUTH_TIMEOUT_MS }
    ),
    page.getByRole('button', { name: /sign in/i }).click(),
  ]);

  // Wait for the /me call that AuthProvider makes after login
  await page.waitForResponse(
    (resp) => resp.url().includes('/api/v1/auth/me') && resp.status() === 200,
    { timeout: AUTH_TIMEOUT_MS }
  );

  // Wait until redirected away from the login page
  await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: AUTH_TIMEOUT_MS });
}

/**
 * Log out by clicking the Sign Out button in the navigation bar.
 */
export async function logout(page: Page): Promise<void> {
  await page.getByRole('button', { name: /sign out/i }).click();
  await page.waitForURL('**/login', { timeout: AUTH_TIMEOUT_MS });
  await page.evaluate(() => localStorage.clear());
}