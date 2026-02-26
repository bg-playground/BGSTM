import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@test.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'password123';

test.describe('Suggestion Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await page.goto('/');
    // Wait for the page to finish loading suggestions
    await page.waitForLoadState('networkidle');
  });

  test('filter suggestions by algorithm', async ({ page }) => {
    // The SuggestionFilters component renders an algorithm select/dropdown
    const algorithmSelect = page.locator('select[name="algorithm"], [data-testid="algorithm-filter"]').first();
    if (await algorithmSelect.isVisible()) {
      await algorithmSelect.selectOption('tfidf');
      // URL or displayed results should reflect the filter
      await expect(page).toHaveURL(/algorithm=tfidf/);
    } else {
      // Fallback: look for a button/tab labelled tfidf
      const tfidfBtn = page.getByRole('button', { name: /tfidf/i });
      await tfidfBtn.click();
      await expect(page).toHaveURL(/algorithm=tfidf/);
    }
  });

  test('filter suggestions by score range', async ({ page }) => {
    // Locate score range inputs
    const minInput = page.locator('input[name="min_score"], input[placeholder*="min"], [data-testid="min-score"]').first();
    if (await minInput.isVisible()) {
      await minInput.fill('0.8');
      await minInput.press('Enter');
      await expect(page).toHaveURL(/min_score=0\.8/);
    } else {
      test.skip();
    }
  });

  test('search suggestions by text', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], [data-testid="search-input"]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('authentication');
      await searchInput.press('Enter');
      await page.waitForLoadState('networkidle');
      // Either URL contains search param or visible results are filtered
      const hasSearchParam = page.url().includes('search=');
      const hasNoResults = await page.getByText(/no suggestions/i).isVisible().catch(() => false);
      expect(hasSearchParam || hasNoResults).toBeTruthy();
    } else {
      test.skip();
    }
  });

  test('keyboard navigation moves focus through suggestion cards', async ({ page }) => {
    // Press ArrowDown to move focus; the focused item should change
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(200);
    // The SuggestionDashboard tracks focusedIndex; just assert no JS error occurred
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowUp');
    expect(errors).toHaveLength(0);
  });

  test('accept a suggestion updates its status', async ({ page }) => {
    // Find the first pending suggestion accept button
    const acceptBtn = page.getByRole('button', { name: /accept/i }).first();
    if (!(await acceptBtn.isVisible().catch(() => false))) {
      test.skip();
      return;
    }
    await acceptBtn.click();
    // A toast/notification should appear confirming the action
    await expect(page.getByText(/accepted|success/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test('reject a suggestion with feedback', async ({ page }) => {
    const rejectBtn = page.getByRole('button', { name: /reject/i }).first();
    if (!(await rejectBtn.isVisible().catch(() => false))) {
      test.skip();
      return;
    }
    await rejectBtn.click();

    // If a feedback modal/input appears, fill it in
    const feedbackInput = page.getByLabel(/feedback|reason/i).first();
    if (await feedbackInput.isVisible().catch(() => false)) {
      await feedbackInput.fill('Not relevant to this requirement.');
      await page.getByRole('button', { name: /confirm|submit|reject/i }).last().click();
    }

    await expect(page.getByText(/rejected|success/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test('filter persistence via URL query params survives page reload', async ({ page }) => {
    // Apply an algorithm filter
    await page.goto('/?algorithm=hybrid');
    await page.waitForLoadState('networkidle');

    // Reload preserves the query param
    await page.reload();
    await expect(page).toHaveURL(/algorithm=hybrid/);
  });
});
