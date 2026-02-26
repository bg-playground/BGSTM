import { chromium, FullConfig } from '@playwright/test';
import { login } from './helpers/auth';
import * as fs from 'fs';
import * as path from 'path';

async function globalSetup(config: FullConfig) {
  const baseURL = config.projects[0].use.baseURL ?? 'http://localhost:3000';
  const adminEmail = process.env.E2E_ADMIN_EMAIL ?? 'admin@test.com';
  const adminPassword = process.env.E2E_ADMIN_PASSWORD ?? 'password123';
  const browser = await chromium.launch();
  const page = await browser.newPage({ baseURL });

  await login(page, adminEmail, adminPassword);

  const authDir = path.join(__dirname, '.auth');
  fs.mkdirSync(authDir, { recursive: true });
  await page.context().storageState({ path: path.join(authDir, 'admin.json') });

  await browser.close();
}

export default globalSetup;
