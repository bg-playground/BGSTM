import { chromium, FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function globalSetup(config: FullConfig) {
  const baseURL = config.projects[0].use.baseURL ?? 'http://localhost:3000';
  const adminEmail = process.env.E2E_ADMIN_EMAIL ?? 'admin@test.com';
  const adminPassword = process.env.E2E_ADMIN_PASSWORD ?? 'password123';

  const browser = await chromium.launch();
  // baseURL must be set on the context, not on newPage()
  const context = await browser.newContext({ baseURL });
  const page = await context.newPage();

  // Wait for the frontend to be ready before attempting login
  // The CI health check loop ensures the container is up, but the app
  // may still be compiling/initialising — retry the login page until it responds.
  let loginReady = false;
  for (let i = 0; i < 12; i++) {
    try {
      const response = await page.goto('/login', { waitUntil: 'domcontentloaded', timeout: 10_000 });
      if (response && response.ok()) {
        loginReady = true;
        break;
      }
    } catch {
      // not ready yet
    }
    await page.waitForTimeout(5_000);
  }
  if (!loginReady) {
    throw new Error('Frontend /login page was not reachable after 60s — aborting global setup.');
  }

  // Fill in the login form
  await page.getByLabel('Email address').fill(adminEmail);
  await page.getByLabel('Password').fill(adminPassword);
  await page.getByRole('button', { name: /sign in/i }).click();

  // Wait for redirect away from /login with a generous timeout
  await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 30_000 });

  const authDir = path.join(__dirname, '.auth');
  fs.mkdirSync(authDir, { recursive: true });
  await context.storageState({ path: path.join(authDir, 'admin.json') });

  await browser.close();
}

export default globalSetup;