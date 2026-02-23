import { type Page } from '@playwright/test';

export const TEST_USERS = {
  admin: { email: 'e2e-admin@bgstm.test', password: 'Admin1234!', name: 'E2E Admin' },
  reviewer: { email: 'e2e-reviewer@bgstm.test', password: 'Reviewer1234!', name: 'E2E Reviewer' },
  viewer: { email: 'e2e-viewer@bgstm.test', password: 'Viewer1234!', name: 'E2E Viewer' },
} as const;

const TOKEN_STORAGE_KEY = 'bgstm-auth-token';
const API_URL = process.env.API_URL ?? 'http://localhost:8000';
const API_PREFIX = '/api/v1';

/** Log in via the API and inject the JWT into the browser's localStorage. */
export async function loginAs(
  page: Page,
  user: (typeof TEST_USERS)[keyof typeof TEST_USERS],
): Promise<void> {
  const res = await fetch(`${API_URL}${API_PREFIX}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: user.email, password: user.password }),
  });
  if (!res.ok) {
    throw new Error(`Login failed for ${user.email}: ${res.status}`);
  }
  const { access_token } = (await res.json()) as { access_token: string };

  // Inject token before navigating so the app considers the user logged in
  await page.goto('/');
  await page.evaluate(
    ([key, token]) => localStorage.setItem(key, token),
    [TOKEN_STORAGE_KEY, access_token],
  );
}

/** Navigate to a protected page after setting the auth token. */
export async function gotoProtected(
  page: Page,
  user: (typeof TEST_USERS)[keyof typeof TEST_USERS],
  path = '/',
): Promise<void> {
  await loginAs(page, user);
  await page.goto(path);
}
