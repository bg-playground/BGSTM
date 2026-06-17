import { expect, test } from '@playwright/test';

import { login } from './helpers/auth';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@test.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'password123';

test.describe('Release Readiness Dashboard', () => {
  test('admin can sign off QA Lead and export markdown report', async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await page.goto('/release-readiness');
    await page.waitForLoadState('networkidle');

    await expect(page.getByTestId('release-readiness-status-banner')).toBeVisible();

    const qaSignoffPanel = page.getByTestId('release-readiness-signoff-qa_lead');
    await expect(qaSignoffPanel).toBeVisible();

    const signoffButton = qaSignoffPanel.getByRole('button', { name: /sign off|revoke/i });
    if ((await signoffButton.textContent())?.toLowerCase().includes('sign off')) {
      await signoffButton.click();
      await expect(qaSignoffPanel).toContainText(/signed off/i);
    }

    const downloadPromise = page.waitForEvent('download', { timeout: 30_000 });
    await page.locator('summary', { hasText: 'Export' }).click();
    await page.getByTestId('release-readiness-export-md').click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/\.md$/i);
  });
});
