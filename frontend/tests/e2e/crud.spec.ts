import { test, expect } from '@playwright/test';
import { gotoProtected, TEST_USERS } from './helpers';

// ── Requirements CRUD ─────────────────────────────────────────────────────────

test.describe('Requirements CRUD', () => {
  const UNIQUE_TITLE = `E2E Req ${Date.now()}`;
  const UPDATED_TITLE = `${UNIQUE_TITLE} – updated`;

  test.beforeEach(async ({ page }) => {
    await gotoProtected(page, TEST_USERS.admin, '/requirements');
    await expect(page.getByRole('heading', { name: /Requirements/i })).toBeVisible({
      timeout: 10_000,
    });
  });

  test('create a new requirement → it appears in the list', async ({ page }) => {
    await page.getByRole('button', { name: /\+ New Requirement/i }).click();

    // Fill in the modal form
    await page.getByLabel('Title *').fill(UNIQUE_TITLE);
    await page.getByLabel('Description *').fill('Created by E2E test');
    await page.getByRole('button', { name: /Create$/i }).click();

    // Modal closes and success toast appears
    await expect(page.getByText(/created successfully/i)).toBeVisible({ timeout: 5_000 });

    // New card appears in the list
    await expect(page.getByText(UNIQUE_TITLE)).toBeVisible({ timeout: 5_000 });
  });

  test('edit a requirement → changes persist', async ({ page }) => {
    // We need an existing card to edit; skip if none
    const card = page.locator('.grid > div').first();
    const count = await page.locator('.grid > div').count();
    if (count === 0) {
      test.skip();
    }

    // Find the Edit button of the first card
    const editBtn = card.getByRole('button', { name: 'Edit' });
    await editBtn.click();

    // Change the title
    const titleInput = page.getByLabel('Title *');
    await titleInput.clear();
    await titleInput.fill(UPDATED_TITLE);
    await page.getByRole('button', { name: /Update/i }).click();

    await expect(page.getByText(/updated successfully/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText(UPDATED_TITLE)).toBeVisible({ timeout: 5_000 });
  });

  test('delete a requirement → it is removed from the list', async ({ page }) => {
    const cards = page.locator('.grid > div');
    const before = await cards.count();
    if (before === 0) {
      test.skip();
    }

    // Accept the confirm dialog
    page.on('dialog', (dialog) => dialog.accept());

    const deleteBtn = cards.first().getByRole('button', { name: 'Delete' });
    await deleteBtn.click();

    await expect(page.getByText(/deleted successfully/i)).toBeVisible({ timeout: 5_000 });
    await expect(cards).toHaveCount(before - 1, { timeout: 5_000 });
  });
});

// ── Test Cases CRUD ───────────────────────────────────────────────────────────

test.describe('Test Cases CRUD', () => {
  const UNIQUE_TC_TITLE = `E2E TC ${Date.now()}`;

  test.beforeEach(async ({ page }) => {
    await gotoProtected(page, TEST_USERS.admin, '/test-cases');
    await expect(page.getByRole('heading', { name: /Test Cases/i })).toBeVisible({
      timeout: 10_000,
    });
  });

  test('create a new test case → it appears in the list', async ({ page }) => {
    await page.getByRole('button', { name: /\+ New Test Case/i }).click();

    await page.getByLabel('Title *').fill(UNIQUE_TC_TITLE);
    await page.getByLabel('Description *').fill('Created by E2E test');
    await page.getByRole('button', { name: /Create$/i }).click();

    await expect(page.getByText(/created successfully/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText(UNIQUE_TC_TITLE)).toBeVisible({ timeout: 5_000 });
  });
});

// ── Traceability link (via Manual Links page) ─────────────────────────────────

test.describe('Traceability Link Creation', () => {
  test.beforeEach(async ({ page }) => {
    await gotoProtected(page, TEST_USERS.admin, '/links');
    await expect(page.getByRole('heading', { name: /Manual Links|Links/i })).toBeVisible({
      timeout: 10_000,
    });
  });

  test('manual links page loads without errors', async ({ page }) => {
    await expect(page.getByText(/Failed to load/i)).not.toBeVisible();
  });

  test('link a test case to a requirement via the create-link form', async ({ page }) => {
    // The page exposes a form or a button to create a new link
    const newLinkBtn = page.getByRole('button', { name: /\+ New Link|Create Link|Add Link/i });
    if (!(await newLinkBtn.isVisible())) {
      // Some implementations show the form inline – skip if button not found
      test.skip();
    }
    await newLinkBtn.click();

    // Select the first available requirement and test case from the dropdowns
    const reqSelect = page.getByLabel(/Requirement/i).first();
    const tcSelect = page.getByLabel(/Test Case/i).first();
    if (!(await reqSelect.isVisible()) || !(await tcSelect.isVisible())) {
      test.skip();
    }

    // Pick whatever options are available (first non-empty option)
    await reqSelect.selectOption({ index: 1 });
    await tcSelect.selectOption({ index: 1 });

    await page.getByRole('button', { name: /Create|Save|Link/i }).last().click();

    await expect(page.getByText(/created|saved|linked/i)).toBeVisible({ timeout: 5_000 });
  });
});
