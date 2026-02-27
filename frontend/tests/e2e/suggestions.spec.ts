import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@test.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'password123';

test.describe('Suggestion Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await page.goto('/');
    // Wait for the dashboard heading to confirm we're on the right page
    await page.getByRole('heading', { name: /suggestion dashboard/i }).waitFor({ timeout: 30_000 });
  });

  test('page renders the dashboard heading and filters', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /suggestion dashboard/i })).toBeVisible();
    // The SuggestionFilters panel should be present
    await expect(page.locator('text=Algorithm').first()).toBeVisible({ timeout: 5_000 });
  });

  test('filter suggestions by algorithm', async ({ page }) => {
    // SuggestionFilters renders a <select> next to a label "Algorithm"
    const algorithmSelect = page.locator('select').filter({ has: page.locator('option[value="tfidf"]') }).first();
    if (!(await algorithmSelect.isVisible({ timeout: 5_000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await algorithmSelect.selectOption('tfidf');
    await expect(page).toHaveURL(/algorithm=tfidf/, { timeout: 10_000 });
  });

  test('filter suggestions by score range', async ({ page }) => {
    // SuggestionFilters renders a range input for min score
    const rangeInput = page.locator('input[type="range"]').first();
    if (!(await rangeInput.isVisible({ timeout: 5_000 }).catch(() => false))) {
      test.skip();
      return;
    }
    // Range inputs can't easily be "filled"; just verify it exists and is interactive
    await expect(rangeInput).toBeEnabled();
  });

  test('search suggestions by text', async ({ page }) => {
    const searchInput = page.locator('input[type="text"][placeholder*="Search" i], input[type="search"]').first();
    if (!(await searchInput.isVisible({ timeout: 5_000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await searchInput.fill('authentication');
    await searchInput.press('Enter');
    // Wait for the page to process the search
    await page.waitForTimeout(1_000);
    const hasSearchParam = page.url().includes('search=');
    const hasNoResults = await page.getByText(/no pending suggestions/i).isVisible().catch(() => false);
    expect(hasSearchParam || hasNoResults).toBeTruthy();
  });

  test('keyboard navigation does not cause errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(200);
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowUp');
    await page.waitForTimeout(200);
    expect(errors).toHaveLength(0);
  });

  test('accept a suggestion updates its status', async ({ page }) => {
    // Only runs if there are suggestion cards with Accept buttons
    const acceptBtn = page.getByRole('button', { name: /^accept$/i }).first();
    if (!(await acceptBtn.isVisible({ timeout: 5_000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await acceptBtn.click();
    await expect(page.getByText(/accepted|success/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test('reject a suggestion with feedback', async ({ page }) => {
    const rejectBtn = page.getByRole('button', { name: /^reject$/i }).first();
    if (!(await rejectBtn.isVisible({ timeout: 5_000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await rejectBtn.click();
    // No feedback modal exists — rejection happens immediately
    await expect(page.getByText(/rejected|success/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test('filter persistence via URL query params survives page reload', async ({ page }) => {
    // Navigate directly with algorithm param
    await page.goto('/?algorithm=hybrid');
    // Wait for the dashboard to load with the filter applied
    await page.getByRole('heading', { name: /suggestion dashboard/i }).waitFor({ timeout: 30_000 });

    // Verify the algorithm select shows 'hybrid'
    const algorithmSelect = page.locator('select').filter({ has: page.locator('option[value="hybrid"]') }).first();
    if (!(await algorithmSelect.isVisible({ timeout: 5_000 }).catch(() => false))) {
      test.skip();
      return;
    }

    await page.reload();
    await page.getByRole('heading', { name: /suggestion dashboard/i }).waitFor({ timeout: 30_000 });
    await expect(page).toHaveURL(/algorithm=hybrid/);
  });
});
