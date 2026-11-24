/**
 * E2E test for passenger delayed-bag case status (wireframe_passenger_delayed_case.html)
 */
import { test, expect } from './_pipeline_guard';

test.describe('Passenger Delayed-Bag Case Status', () => {
  test('displays case status with confirmed and estimated progress steps', async ({ page }) => {
    // Log in with passenger credentials
    await page.goto('/login');
    await page.getByLabel(/email/i).clear();
    await page.getByLabel(/email/i).fill('sara.johnson@example.com');
    await page.getByLabel(/password/i).clear();
    await page.getByLabel(/password/i).fill('Demo1234!');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for login to complete (passenger users have role pre-assigned, no role selection needed)
    await page.waitForTimeout(1000);

    // Navigate to passenger case status page
    await page.goto('/passenger/cases/BC-DXB-240611');

    // Wait for loading to complete
    await page.waitForLoadState('networkidle');

    // Verify page loaded (look for case reference or status text)
    await expect(page.locator('body')).toContainText(/bc-dxb-240611|working on your bag|baggage360/i);

    // Verify case progress section exists
    const hasProgress = await page.getByText(/progress|reported|review|recovery/i).count();
    expect(hasProgress).toBeGreaterThan(0);

    // Verify confirmed status section exists
    const hasConfirmed = await page.getByText(/confirmed|latest confirmed/i).count();
    expect(hasConfirmed).toBeGreaterThan(0);

    // Verify what this means section exists
    const hasMeaning = await page.getByText(/what this means|nothing you need/i).count();
    expect(hasMeaning).toBeGreaterThan(0);

    // Verify no internal notes visible (passenger-safe view)
    const hasInternal = await page.getByText(/internal.*note|risk.*score/i).count();
    expect(hasInternal).toBe(0);
  });

  test('displays error state for case not found', async ({ page, apiGuard }) => {
    // Allow 404 for non-existent case - this is the expected behavior
    apiGuard.allow(404, '/api/v1/passenger/cases/BC-INVALID-999');
    
    // Log in with passenger credentials
    await page.goto('/login');
    await page.getByLabel(/email/i).clear();
    await page.getByLabel(/email/i).fill('sara.johnson@example.com');
    await page.getByLabel(/password/i).clear();
    await page.getByLabel(/password/i).fill('Demo1234!');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for login to complete (passenger users have role pre-assigned, no role selection needed)
    await page.waitForTimeout(1000);

    // Navigate to non-existent case
    await page.goto('/passenger/cases/BC-INVALID-999');

    // Wait for loading to complete
    await page.waitForLoadState('networkidle');

    // Verify error message
    const hasError = await page.getByText(/couldn't find|not found|error/i).count();
    expect(hasError).toBeGreaterThan(0);
  });
});
