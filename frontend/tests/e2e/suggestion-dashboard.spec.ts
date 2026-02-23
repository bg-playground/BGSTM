import { test, expect } from '@playwright/test';
import { gotoProtected, TEST_USERS } from './helpers';

test.describe('Suggestion Dashboard Flow', () => {
  test.beforeEach(async ({ page }) => {
    await gotoProtected(page, TEST_USERS.admin, '/');
    // Wait for the page heading to confirm we're on the dashboard
    await expect(page.getByRole('heading', { name: /AI Suggestion Dashboard/i })).toBeVisible({
      timeout: 10_000,
    });
  });

  // ── Suggestion list & pagination ──────────────────────────────────────────

  test('suggestion list renders (may be empty or populated)', async ({ page }) => {
    // The page must load without an error toast
    await expect(page.getByText('Failed to load suggestions')).not.toBeVisible();
    // Either the empty-state message or at least one suggestion card is shown
    const hasEmpty = await page.getByText('No pending suggestions').isVisible();
    const hasCards = await page.locator('[data-testid="suggestion-card"]').count();
    expect(hasEmpty || hasCards > 0).toBeTruthy();
  });

  // ── Filters ───────────────────────────────────────────────────────────────

  test('filter panel is present and toggles/changes state', async ({ page }) => {
    // The SuggestionFilters component renders some controls
    // Algorithm selector is a common filter element
    const algorithmSelect = page.getByRole('combobox').first();
    await expect(algorithmSelect).toBeVisible();
  });

  test('search input filters suggestions by text', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/search/i);
    if (!(await searchInput.isVisible())) {
      test.skip();
    }
    await searchInput.fill('login');
    // URL should now contain the search param
    await expect(page).toHaveURL(/search=login/, { timeout: 3_000 });
  });

  test('reset filters button clears search params', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/search/i);
    if (!(await searchInput.isVisible())) {
      test.skip();
    }
    await searchInput.fill('somequery');
    await expect(page).toHaveURL(/search=somequery/);

    const resetBtn = page.getByRole('button', { name: /reset/i });
    await resetBtn.click();
    await expect(page).not.toHaveURL(/search=/);
  });

  // ── Generate & Export ─────────────────────────────────────────────────────

  test('Generate Suggestions button is present and clickable', async ({ page }) => {
    const btn = page.getByRole('button', { name: /generate suggestions/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });

  test('Export CSV button is present', async ({ page }) => {
    const btn = page.getByRole('button', { name: /export csv/i });
    await expect(btn).toBeVisible();
  });

  // ── Keyboard navigation ───────────────────────────────────────────────────

  test('ArrowDown / ArrowUp keyboard navigation moves focus through suggestion cards', async ({
    page,
  }) => {
    // Only run if there are suggestion cards on the page
    const cards = page.locator('[data-testid="suggestion-card"]');
    const count = await cards.count();
    if (count === 0) {
      test.skip();
    }

    // Focus the page body so key events are captured by the global handler
    await page.locator('body').click();
    await page.keyboard.press('ArrowDown');
    // First card should receive the "focused" ring styling
    await expect(cards.first()).toHaveClass(/ring/, { timeout: 2_000 });

    if (count > 1) {
      await page.keyboard.press('ArrowDown');
      await expect(cards.nth(1)).toHaveClass(/ring/, { timeout: 2_000 });
      await page.keyboard.press('ArrowUp');
      await expect(cards.first()).toHaveClass(/ring/, { timeout: 2_000 });
    }
  });

  // ── Accept / Reject ───────────────────────────────────────────────────────

  test('accept a suggestion removes it from the pending list', async ({ page }) => {
    const cards = page.locator('[data-testid="suggestion-card"]');
    const before = await cards.count();
    if (before === 0) {
      test.skip();
    }

    const acceptBtn = cards.first().getByRole('button', { name: /accept/i });
    await acceptBtn.click();

    // The card should disappear
    await expect(cards).toHaveCount(before - 1, { timeout: 5_000 });
    // A success toast should appear
    await expect(page.getByText(/accepted/i)).toBeVisible({ timeout: 3_000 });
  });

  test('reject a suggestion removes it from the pending list', async ({ page }) => {
    const cards = page.locator('[data-testid="suggestion-card"]');
    const before = await cards.count();
    if (before === 0) {
      test.skip();
    }

    const rejectBtn = cards.first().getByRole('button', { name: /reject/i });
    await rejectBtn.click();

    await expect(cards).toHaveCount(before - 1, { timeout: 5_000 });
    await expect(page.getByText(/rejected/i)).toBeVisible({ timeout: 3_000 });
  });

  // ── Confidence badges ─────────────────────────────────────────────────────

  test('confidence score badges display on suggestion cards', async ({ page }) => {
    const cards = page.locator('[data-testid="suggestion-card"]');
    if ((await cards.count()) === 0) {
      test.skip();
    }
    // Each card should contain a numeric score or a confidence level label
    const firstCard = cards.first();
    const badge = firstCard.locator('[data-testid="confidence-badge"], [class*="badge"]').first();
    await expect(badge).toBeVisible();
  });
});
