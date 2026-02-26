import { test, expect } from '@playwright/test';

// ---------------------------------------------------------------------------
// Requirements CRUD
// ---------------------------------------------------------------------------
test.describe('Requirements CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/requirements');
    await page.waitForLoadState('networkidle');
  });

  test('create a new requirement', async ({ page }) => {
    await page.getByRole('button', { name: /add requirement|new requirement|\+ requirement/i }).click();

    await page.getByLabel(/title/i).fill('E2E Test Requirement');
    await page.getByLabel(/description/i).fill('Created by Playwright end-to-end test.');

    await page.getByRole('button', { name: /save|create|submit/i }).click();

    await expect(page.getByText('E2E Test Requirement')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/created successfully|saved successfully/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test('edit an existing requirement', async ({ page }) => {
    // Click the edit button on the first visible requirement
    const editBtn = page.getByRole('button', { name: /edit/i }).first();
    if (!(await editBtn.isVisible().catch(() => false))) {
      test.skip();
      return;
    }
    await editBtn.click();

    const titleInput = page.getByLabel(/title/i);
    await titleInput.clear();
    await titleInput.fill('Updated Requirement Title');

    await page.getByRole('button', { name: /save|update|submit/i }).click();

    await expect(page.getByText('Updated Requirement Title')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/updated successfully|saved successfully/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test('delete a requirement', async ({ page }) => {
    // Find a requirement row and click its delete button
    const deleteBtn = page.getByRole('button', { name: /delete/i }).first();
    if (!(await deleteBtn.isVisible().catch(() => false))) {
      test.skip();
      return;
    }

    // Grab the text of the item about to be deleted for later assertion
    const row = deleteBtn.locator('..').first();
    const itemText = await row.textContent().catch(() => '');

    await deleteBtn.click();

    // Confirm deletion if a dialog appears
    const confirmBtn = page.getByRole('button', { name: /confirm|yes|delete/i }).last();
    if (await confirmBtn.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await confirmBtn.click();
    }

    await expect(page.getByText(/deleted successfully/i)).toBeVisible({ timeout: 10_000 });
    if (itemText) {
      await expect(page.getByText(itemText.trim().slice(0, 30))).toHaveCount(0);
    }
  });
});

// ---------------------------------------------------------------------------
// Test Cases CRUD
// ---------------------------------------------------------------------------
test.describe('Test Cases CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/test-cases');
    await page.waitForLoadState('networkidle');
  });

  test('create a new test case', async ({ page }) => {
    await page.getByRole('button', { name: /add test case|new test case|\+ test case/i }).click();

    await page.getByLabel(/title/i).fill('E2E Test Case');
    await page.getByLabel(/description/i).fill('Created by Playwright end-to-end test.');

    await page.getByRole('button', { name: /save|create|submit/i }).click();

    await expect(page.getByText('E2E Test Case')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/created successfully|saved successfully/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test('edit an existing test case', async ({ page }) => {
    const editBtn = page.getByRole('button', { name: /edit/i }).first();
    if (!(await editBtn.isVisible().catch(() => false))) {
      test.skip();
      return;
    }
    await editBtn.click();

    const titleInput = page.getByLabel(/title/i);
    await titleInput.clear();
    await titleInput.fill('Updated Test Case Title');

    await page.getByRole('button', { name: /save|update|submit/i }).click();

    await expect(page.getByText('Updated Test Case Title')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/updated successfully|saved successfully/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test('delete a test case', async ({ page }) => {
    const deleteBtn = page.getByRole('button', { name: /delete/i }).first();
    if (!(await deleteBtn.isVisible().catch(() => false))) {
      test.skip();
      return;
    }

    await deleteBtn.click();

    const confirmBtn = page.getByRole('button', { name: /confirm|yes|delete/i }).last();
    if (await confirmBtn.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await confirmBtn.click();
    }

    await expect(page.getByText(/deleted successfully/i)).toBeVisible({ timeout: 10_000 });
  });
});
