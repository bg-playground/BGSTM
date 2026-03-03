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

  // Collect diagnostic info
  const errors: string[] = [];
  const requestFailures: string[] = [];

  const onPageError = (err: Error) => errors.push(`Page error: ${err.message}`);
  const onRequestFailed = (req: import('@playwright/test').Request) => {
    requestFailures.push(`Request failed: ${req.url()} - ${req.failure()?.errorText ?? 'unknown'}`);
  };

  page.on('pageerror', onPageError);
  page.on('requestfailed', onRequestFailed);

  try {
    await page.getByLabel('Email address').fill(email);
    await page.getByLabel('Password').fill(password);

    // Capture ANY response to the login endpoint (not just 200)
    const [loginResponse] = await Promise.all([
      page.waitForResponse(
        (resp) => resp.url().includes('/api/v1/auth/login'),
        { timeout: AUTH_TIMEOUT_MS }
      ),
      page.getByRole('button', { name: /sign in/i }).click(),
    ]);

    // Assert on the response — gives a clear error instead of a timeout
    const loginStatus = loginResponse.status();
    if (loginStatus !== 200) {
      let body = '';
      try { body = await loginResponse.text(); } catch { /* ignore */ }
      throw new Error(
        `Login failed: POST /api/v1/auth/login returned ${loginStatus}.\n` +
        `Response body: ${body}\n` +
        `Page errors: ${errors.join('; ') || 'none'}\n` +
        `Request failures: ${requestFailures.join('; ') || 'none'}`
      );
    }

    // Wait for the /me call that AuthProvider makes after login
    const meResponse = await page.waitForResponse(
      (resp) => resp.url().includes('/api/v1/auth/me'),
      { timeout: AUTH_TIMEOUT_MS }
    );

    const meStatus = meResponse.status();
    if (meStatus !== 200) {
      let body = '';
      try { body = await meResponse.text(); } catch { /* ignore */ }
      throw new Error(
        `Auth /me check failed: GET /api/v1/auth/me returned ${meStatus}.\n` +
        `Response body: ${body}\n` +
        `Page errors: ${errors.join('; ') || 'none'}\n` +
        `Request failures: ${requestFailures.join('; ') || 'none'}`
      );
    }

    // Wait until redirected away from the login page
    await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: AUTH_TIMEOUT_MS });
  } finally {
    page.off('pageerror', onPageError);
    page.off('requestfailed', onRequestFailed);
  }
}

/**
 * Log out by clicking the Sign Out button in the navigation bar.
 */
export async function logout(page: Page): Promise<void> {
  await page.getByRole('button', { name: /sign out/i }).click();
  await page.waitForURL('**/login', { timeout: AUTH_TIMEOUT_MS });
  await page.evaluate(() => localStorage.clear());
}