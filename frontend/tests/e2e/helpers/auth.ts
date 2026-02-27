import type { Page } from '@playwright/test';

/**
 * Log in via the UI login form and wait for navigation to the dashboard.
 * Relies on the baseURL configured in playwright.config.ts.
 */
export async function login(page: Page, email: string, password: string): Promise<void> {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: /sign in/i }).click();
  // Wait until redirected away from the login page
  await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 30_000 });
}

/**
 * Log out by clicking the Sign Out button in the navigation bar.
 */
export async function logout(page: Page): Promise<void> {
  await page.getByRole('button', { name: /sign out/i }).click();
  await page.waitForURL('**/login', { timeout: 30_000 });
}