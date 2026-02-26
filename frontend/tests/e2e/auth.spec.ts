import { test, expect } from '@playwright/test';
import { login, logout } from './helpers/auth';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@test.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'password123';

test.describe('Authentication', () => {
  // Auth tests verify login/logout flows and must start from an unauthenticated state.
  test.use({ storageState: { cookies: [], origins: [] } });

  test('register a new user', async ({ page }) => {
    const uniqueEmail = `e2e-reg-${Date.now()}@test.com`;

    await page.goto('/register');
    await expect(page.getByRole('heading', { name: /bgstm traceability/i })).toBeVisible();

    await page.getByLabel(/full name/i).fill('E2E Test User');
    await page.getByLabel('Email address').fill(uniqueEmail);
    // Use password field by index to distinguish password vs confirm-password
    const passwordInputs = page.getByLabel(/^password/i);
    await passwordInputs.nth(0).fill('password123');
    await page.getByLabel(/confirm password/i).fill('password123');

    await page.getByRole('button', { name: /create account/i }).click();

    // After registration user should be redirected to the dashboard
    await expect(page).not.toHaveURL(/\/register/);
  });

  test('login with valid credentials', async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    // Dashboard is the root protected route
    await expect(page).toHaveURL('/');
    await expect(page.getByText(/suggestion dashboard/i)).toBeVisible();
  });

  test('login with invalid credentials shows error', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email address').fill('nobody@example.com');
    await page.getByLabel('Password').fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page.getByText(/invalid email or password/i)).toBeVisible();
    await expect(page).toHaveURL(/\/login/);
  });

  test('accessing a protected page while unauthenticated redirects to login', async ({ page }) => {
    // Navigate directly to a protected route without logging in
    await page.goto('/requirements');
    await expect(page).toHaveURL(/\/login/);
  });

  test('logout redirects to login and protected pages are no longer accessible', async ({
    page,
  }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await expect(page).toHaveURL('/');

    await logout(page);
    await expect(page).toHaveURL(/\/login/);

    // After logout, navigating to a protected route should redirect back to login
    await page.goto('/requirements');
    await expect(page).toHaveURL(/\/login/);
  });
});
