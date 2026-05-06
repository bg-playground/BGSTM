import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@test.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'password123';
const ITEM_ROW_SELECTOR = 'tr, [data-testid*="row"], div.bg-white.rounded-lg.shadow-md.p-6';

// ---------------------------------------------------------------------------
// Requirements CRUD
// ---------------------------------------------------------------------------
test.describe('Requirements CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await page.goto('/requirements');
    await page.waitForLoadState('networkidle');
  });

  test('create a new requirement', async ({ page }) => {
    await page.getByRole('button', { name: /add requirement|new requirement|\+ requirement/i }).click();

    await page.getByLabel(/title/i).fill('E2E Test Requirement');
    await page.getByLabel(/description/i).fill('Created by Playwright end-to-end test.');

    await page.getByRole('button', { name: /save|create|submit/i }).click();

    // Wait for the modal to close before checking for toast
    const dialog = page.locator('[role="dialog"]');
    if (await dialog.isVisible().catch(() => false)) {
      await dialog.waitFor({ state: 'hidden', timeout: 10_000 });
    }

    await expect(page.getByText('E2E Test Requirement')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/created successfully|saved successfully/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test('edit an existing requirement', async ({ page }) => {
    const seedTitle = `E2E Edit Req Target ${Date.now()}`;

    await page.getByRole('button', { name: /add requirement|new requirement|\+ requirement/i }).click();
    await page.getByLabel(/title/i).fill(seedTitle);
    await page.getByLabel(/description/i).fill('Throwaway requirement target for edit test.');
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    const createDialog = page.locator('[role="dialog"]');
    if (await createDialog.isVisible().catch(() => false)) {
      await createDialog.waitFor({ state: 'hidden', timeout: 10_000 });
    }

    const requirementRow = page.locator(ITEM_ROW_SELECTOR).filter({ hasText: seedTitle }).first();
    await expect(requirementRow).toBeVisible({ timeout: 10_000 });
    await requirementRow.getByRole('button', { name: /edit/i }).click();

    const titleInput = page.getByLabel(/title/i);
    const updatedTitle = `${seedTitle} (edited)`;
    await titleInput.clear();
    await titleInput.fill(updatedTitle);

    await page.getByRole('button', { name: /save|update|submit/i }).click();

    await expect(page.getByText(updatedTitle)).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/updated successfully|saved successfully/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test('delete a requirement', async ({ page }) => {
    const seedTitle = `E2E Delete Req Target ${Date.now()}`;

    await page.getByRole('button', { name: /add requirement|new requirement|\+ requirement/i }).click();
    await page.getByLabel(/title/i).fill(seedTitle);
    await page.getByLabel(/description/i).fill('Throwaway requirement target for delete test.');
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    const createDialog = page.locator('[role="dialog"]');
    if (await createDialog.isVisible().catch(() => false)) {
      await createDialog.waitFor({ state: 'hidden', timeout: 10_000 });
    }

    const requirementRow = page.locator(ITEM_ROW_SELECTOR).filter({ hasText: seedTitle }).first();
    await expect(requirementRow).toBeVisible({ timeout: 10_000 });
    const deleteBtn = requirementRow.getByRole('button', { name: /delete/i });

    // Handle the native confirm() dialog BEFORE clicking delete
    page.once('dialog', async (dialog) => {
      await dialog.accept();
    });

    await deleteBtn.click();

    await expect(page.getByText(/deleted successfully/i)).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(seedTitle, { exact: true })).toHaveCount(0);
  });
});

// ---------------------------------------------------------------------------
// Test Cases CRUD
// ---------------------------------------------------------------------------
test.describe('Test Cases CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await page.goto('/test-cases');
    await page.waitForLoadState('networkidle');
  });

  test('create a new test case', async ({ page }) => {
    await page.getByRole('button', { name: /add test case|new test case|\+ test case/i }).click();

    await page.getByLabel(/title/i).fill('E2E Test Case');
    await page.getByLabel(/description/i).fill('Created by Playwright end-to-end test.');

    await page.getByRole('button', { name: /save|create|submit/i }).click();

    // Wait for the modal to close before checking for toast
    const dialog = page.locator('[role="dialog"]');
    if (await dialog.isVisible().catch(() => false)) {
      await dialog.waitFor({ state: 'hidden', timeout: 10_000 });
    }

    await expect(page.getByText('E2E Test Case')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/created successfully|saved successfully/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test('edit an existing test case', async ({ page }) => {
    const seedTitle = `E2E Edit TC Target ${Date.now()}`;

    await page.getByRole('button', { name: /add test case|new test case|\+ test case/i }).click();
    await page.getByLabel(/title/i).fill(seedTitle);
    await page.getByLabel(/description/i).fill('Throwaway test case target for edit test.');
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    const createDialog = page.locator('[role="dialog"]');
    if (await createDialog.isVisible().catch(() => false)) {
      await createDialog.waitFor({ state: 'hidden', timeout: 10_000 });
    }

    const testCaseRow = page.locator(ITEM_ROW_SELECTOR).filter({ hasText: seedTitle }).first();
    await expect(testCaseRow).toBeVisible({ timeout: 10_000 });
    await testCaseRow.getByRole('button', { name: /edit/i }).click();

    const titleInput = page.getByLabel(/title/i);
    const updatedTitle = `${seedTitle} (edited)`;
    await titleInput.clear();
    await titleInput.fill(updatedTitle);

    await page.getByRole('button', { name: /save|update|submit/i }).click();

    await expect(page.getByText(updatedTitle)).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/updated successfully|saved successfully/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test('delete a test case', async ({ page }) => {
    const seedTitle = `E2E Delete TC Target ${Date.now()}`;

    await page.getByRole('button', { name: /add test case|new test case|\+ test case/i }).click();
    await page.getByLabel(/title/i).fill(seedTitle);
    await page.getByLabel(/description/i).fill('Throwaway test case target for delete test.');
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    const createDialog = page.locator('[role="dialog"]');
    if (await createDialog.isVisible().catch(() => false)) {
      await createDialog.waitFor({ state: 'hidden', timeout: 10_000 });
    }

    const testCaseRow = page.locator(ITEM_ROW_SELECTOR).filter({ hasText: seedTitle }).first();
    await expect(testCaseRow).toBeVisible({ timeout: 10_000 });
    const deleteBtn = testCaseRow.getByRole('button', { name: /delete/i });

    // Handle the native confirm() dialog BEFORE clicking delete
    page.once('dialog', async (dialog) => {
      await dialog.accept();
    });

    await deleteBtn.click();

    await expect(page.getByText(/deleted successfully/i)).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(seedTitle, { exact: true })).toHaveCount(0);
  });
});
