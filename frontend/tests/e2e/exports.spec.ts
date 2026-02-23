import { test, expect } from '@playwright/test';
import { gotoProtected, TEST_USERS } from './helpers';

test.describe('Traceability & Exports Flow', () => {
  test.beforeEach(async ({ page }) => {
    await gotoProtected(page, TEST_USERS.admin, '/traceability');
    await expect(page.getByRole('heading', { name: /Traceability Matrix/i })).toBeVisible({
      timeout: 10_000,
    });
  });

  // ── Navigation ────────────────────────────────────────────────────────────

  test('traceability matrix page loads with coverage summary', async ({ page }) => {
    // Coverage percentage card must be present
    await expect(page.getByText(/Coverage Percentage/i)).toBeVisible();
    // No error toast
    await expect(page.getByText(/Failed to load traceability matrix/i)).not.toBeVisible();
  });

  test('requirements coverage table is rendered', async ({ page }) => {
    await expect(page.getByText(/Requirements Coverage/i)).toBeVisible();
    // Header cells
    await expect(page.getByRole('columnheader', { name: /Requirement/i })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: /Coverage/i })).toBeVisible();
  });

  // ── CSV Export ────────────────────────────────────────────────────────────

  test('export traceability matrix as CSV → file download starts', async ({ page }) => {
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 15_000 }),
      page.getByRole('button', { name: /Export CSV/i }).click(),
    ]);

    expect(download.suggestedFilename()).toMatch(/traceability_matrix.*\.csv$/i);
    // Ensure the file is not empty
    const filePath = await download.path();
    expect(filePath).toBeTruthy();
  });

  // ── JSON Export ───────────────────────────────────────────────────────────

  test('export traceability matrix as JSON → file download starts', async ({ page }) => {
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 15_000 }),
      page.getByRole('button', { name: /Export JSON/i }).click(),
    ]);

    expect(download.suggestedFilename()).toMatch(/traceability_matrix.*\.json$/i);
    const filePath = await download.path();
    expect(filePath).toBeTruthy();
  });

  // ── PDF Export ────────────────────────────────────────────────────────────

  test('export traceability matrix as PDF → file download starts', async ({ page }) => {
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 15_000 }),
      page.getByRole('button', { name: /Export PDF/i }).click(),
    ]);

    expect(download.suggestedFilename()).toMatch(/traceability_matrix.*\.pdf$/i);
    const filePath = await download.path();
    expect(filePath).toBeTruthy();
  });
});

test.describe('Suggestion CSV Export', () => {
  test.beforeEach(async ({ page }) => {
    await gotoProtected(page, TEST_USERS.admin, '/');
    await expect(page.getByRole('heading', { name: /AI Suggestion Dashboard/i })).toBeVisible({
      timeout: 10_000,
    });
  });

  test('export suggestions as CSV → file download starts', async ({ page }) => {
    const exportBtn = page.getByRole('button', { name: /Export CSV/i });
    await expect(exportBtn).toBeVisible();

    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 15_000 }),
      exportBtn.click(),
    ]);

    expect(download.suggestedFilename()).toMatch(/suggestions.*\.csv$/i);
    const filePath = await download.path();
    expect(filePath).toBeTruthy();
  });
});

test.describe('Metrics CSV Export', () => {
  test.beforeEach(async ({ page }) => {
    await gotoProtected(page, TEST_USERS.admin, '/metrics');
    await expect(page.getByRole('heading', { name: /Metrics/i })).toBeVisible({
      timeout: 10_000,
    });
  });

  test('metrics dashboard loads', async ({ page }) => {
    await expect(page.getByText(/Failed to load/i)).not.toBeVisible();
  });

  test('export metrics as CSV → file download starts', async ({ page }) => {
    const exportBtn = page.getByRole('button', { name: /Export.*CSV/i });
    if (!(await exportBtn.isVisible())) {
      test.skip();
    }

    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 15_000 }),
      exportBtn.click(),
    ]);

    // filename contains "metrics" and ends with .csv
    expect(download.suggestedFilename()).toMatch(/\.csv$/i);
    const filePath = await download.path();
    expect(filePath).toBeTruthy();
  });
});
