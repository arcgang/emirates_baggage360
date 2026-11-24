import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 01: Login and Role Entry', () => {
  test('logs in with seed credentials and selects operations role', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Verify login form is visible
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();

    // Fill in credentials (matching seed data: mariam.alsuwaidi@baggage360.demo / Demo1234!)
    const emailInput = page.getByLabel(/work email or staff id/i);
    const passwordInput = page.getByLabel('Password');
    
    await emailInput.clear();
    await emailInput.fill('mariam.alsuwaidi@baggage360.demo');
    
    await passwordInput.clear();
    await passwordInput.fill('Demo1234!');

    // Submit login form
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for role selection screen
    await expect(page.getByText(/demo role entry/i)).toBeVisible();

    // Verify role cards are displayed using role buttons
    await expect(page.getByRole('button', { name: /operations lead/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /partner handler/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /^passenger/i })).toBeVisible();
    await expect(page.getByRole('button').filter({ hasText: /^Executive/ })).toBeVisible();

    // Select operations role
    const operationsCard = page.getByRole('button', { name: /operations lead/i });
    await operationsCard.click();

    // Verify redirect to /operations/cockpit
    await expect(page).toHaveURL(/\/operations\/cockpit/);
    
    // Verify operations cockpit page loaded
    await expect(page.getByRole('heading', { name: /operations cockpit/i })).toBeVisible();
  });

  test('shows validation error when email is empty', async ({ page }) => {
    await page.goto('/login');

    // Clear email field
    const emailInput = page.getByLabel(/work email or staff id/i);
    await emailInput.clear();

    // Try to submit
    await page.getByRole('button', { name: /sign in/i }).click();

    // Verify error message
    await expect(page.getByText(/enter your work email or staff id/i)).toBeVisible();
  });
});
