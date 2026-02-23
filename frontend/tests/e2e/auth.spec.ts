import { test, expect } from '@playwright/test';
import { TEST_USERS, loginAs } from './helpers';

const TOKEN_KEY = 'bgstm-auth-token';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Start each test from the login page with no stored token
    await page.goto('/login');
    await page.evaluate((key) => localStorage.removeItem(key), TOKEN_KEY);
  });

  // ── Registration ──────────────────────────────────────────────────────────

  test('register a new user → redirect to dashboard', async ({ page }) => {
    const unique = `e2e-reg-${Date.now()}`;
    await page.goto('/register');

    await page.getByLabel('Email address').fill(`${unique}@bgstm.test`);
    await page.getByLabel('Password', { exact: false }).first().fill('Register1234!');
    await page.getByLabel('Confirm password').fill('Register1234!');
    await page.getByRole('button', { name: 'Create account' }).click();

    // After successful registration the app redirects to the dashboard (/)
    await expect(page).toHaveURL('/', { timeout: 10_000 });
  });

  test('register with mismatched passwords → shows error', async ({ page }) => {
    await page.goto('/register');

    await page.getByLabel('Email address').fill('bad-reg@bgstm.test');
    await page.getByLabel('Password', { exact: false }).first().fill('Password1234!');
    await page.getByLabel('Confirm password').fill('DifferentPassword!');
    await page.getByRole('button', { name: 'Create account' }).click();

    await expect(page.getByText('Passwords do not match')).toBeVisible();
  });

  // ── Login ─────────────────────────────────────────────────────────────────

  test('login with valid credentials → redirect to dashboard', async ({ page }) => {
    await page.getByLabel('Email address').fill(TEST_USERS.admin.email);
    await page.getByLabel('Password').fill(TEST_USERS.admin.password);
    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page).toHaveURL('/', { timeout: 10_000 });
    // Token should now be stored
    const token = await page.evaluate((key) => localStorage.getItem(key), TOKEN_KEY);
    expect(token).toBeTruthy();
  });

  test('login with invalid credentials → shows error message', async ({ page }) => {
    await page.getByLabel('Email address').fill('nobody@bgstm.test');
    await page.getByLabel('Password').fill('WrongPassword!');
    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page.getByText('Invalid email or password')).toBeVisible({ timeout: 5_000 });
    // URL should remain on /login
    await expect(page).toHaveURL('/login');
  });

  // ── Logout ────────────────────────────────────────────────────────────────

  test('logout → redirect to login page', async ({ page }) => {
    // Log in first via API shortcut
    await loginAs(page, TEST_USERS.admin);
    await page.goto('/');
    await expect(page).not.toHaveURL('/login');

    // Click the logout button in the navigation
    await page.getByRole('button', { name: /logout/i }).click();

    await expect(page).toHaveURL('/login', { timeout: 5_000 });
    // Token should be removed
    const token = await page.evaluate((key) => localStorage.getItem(key), TOKEN_KEY);
    expect(token).toBeNull();
  });

  // ── Protected routes ──────────────────────────────────────────────────────

  test('access protected route while unauthenticated → redirect to login', async ({ page }) => {
    // Ensure no token is stored
    await page.evaluate((key) => localStorage.removeItem(key), TOKEN_KEY);
    await page.goto('/requirements');

    await expect(page).toHaveURL('/login', { timeout: 5_000 });
  });

  test('access /traceability while unauthenticated → redirect to login', async ({ page }) => {
    await page.evaluate((key) => localStorage.removeItem(key), TOKEN_KEY);
    await page.goto('/traceability');

    await expect(page).toHaveURL('/login', { timeout: 5_000 });
  });
});
