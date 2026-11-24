/**
 * Smoke test: Login flow with seed credentials.
 */
import { test, expect } from './_pipeline_guard';

test.describe('Login Flow', () => {
  test('should log in with seed credentials and show dashboard', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Verify login page loads
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();

    // Type credentials into the form (do not rely on pre-filled values)
    const emailInput = page.locator('input#email');
    const passwordInput = page.locator('input#password');
    
    await emailInput.clear();
    await emailInput.fill('mariam.alsuwaidi@baggage360.demo');
    
    await passwordInput.clear();
    await passwordInput.fill('Demo1234!');

    // Submit the form
    await page.locator('button[type="submit"]').click();

    // Wait for role selection screen
    await expect(page.getByText(/demo role entry/i)).toBeVisible({ timeout: 10000 });

    // Select operations role
    await page.getByRole('button', { name: /operations lead/i }).click();

    // Wait for navigation to operations cockpit
    await page.waitForURL(/\/operations\/cockpit/, { timeout: 10000 });

    // Verify operations cockpit page loaded
    await expect(page.getByRole('heading', { name: /operations cockpit/i })).toBeVisible();
    
    // Verify sidebar shows role-specific navigation (link, not heading)
    await expect(page.getByRole('link', { name: 'Cockpit' })).toBeVisible();
    
    // Verify sign out link is present
    await expect(page.getByRole('link', { name: /sign out/i })).toBeVisible();
  });
});
