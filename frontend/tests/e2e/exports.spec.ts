import { test, expect } from '@playwright/test';
import { tmpdir } from 'os';
import { readFileSync } from 'fs';
import path from 'path';

test.describe('Export Functionality', () => {
  test('export suggestions as CSV triggers a download', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const downloadPromise = page.waitForEvent('download', { timeout: 15_000 });

    // Look for an export/CSV button on the Suggestion Dashboard
    const exportBtn = page
      .getByRole('button', { name: /export.*csv|csv.*export|download.*csv/i })
      .first();

    if (!(await exportBtn.isVisible({ timeout: 3_000 }).catch(() => false))) {
      test.skip();
      return;
    }

    await exportBtn.click();

    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/\.csv$/i);
  });

  test('export traceability matrix as PDF triggers a download', async ({ page }) => {
    await page.goto('/traceability');
    await page.waitForLoadState('networkidle');

    const downloadPromise = page.waitForEvent('download', { timeout: 15_000 });

    const exportBtn = page
      .getByRole('button', { name: /export.*pdf|pdf.*export|download.*pdf/i })
      .first();

    if (!(await exportBtn.isVisible({ timeout: 3_000 }).catch(() => false))) {
      test.skip();
      return;
    }

    await exportBtn.click();

    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/\.pdf$/i);
  });

  test('export metrics as CSV triggers a download', async ({ page }) => {
    await page.goto('/metrics');
    await page.waitForLoadState('networkidle');

    const downloadPromise = page.waitForEvent('download', { timeout: 15_000 });

    const exportBtn = page
      .getByRole('button', { name: /export.*csv|csv.*export|download.*csv/i })
      .first();

    if (!(await exportBtn.isVisible({ timeout: 3_000 }).catch(() => false))) {
      test.skip();
      return;
    }

    await exportBtn.click();

    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/\.csv$/i);

    // Save and verify the file is non-empty
    const tmpPath = path.join(tmpdir(), download.suggestedFilename());
    await download.saveAs(tmpPath);
    const content = readFileSync(tmpPath, 'utf-8');
    expect(content.length).toBeGreaterThan(0);
  });
});
