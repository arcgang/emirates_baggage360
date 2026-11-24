/**
 * E2E test for passenger bag status screen (wireframe_passenger_bag_status.html)
 */
import { test, expect } from './_pipeline_guard';

test.describe('Passenger Bag Status', () => {
  test('displays bag status with confirmed and estimated information', async ({ page }) => {
    // Log in with passenger credentials
    await page.goto('/login');
    await page.getByLabel(/email/i).clear();
    await page.getByLabel(/email/i).fill('sara.johnson@example.com');
    await page.getByLabel(/password/i).clear();
    await page.getByLabel(/password/i).fill('Demo1234!');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for login to complete (passenger users have role pre-assigned, no role selection needed)
    await page.waitForTimeout(1000);

    // Navigate to passenger bag status page
    await page.goto('/passenger/bags/0176482193/status');

    // Wait for loading to complete
    await page.waitForLoadState('networkidle');

    // Verify page loaded (look for bag tag or status headline)
    await expect(page.locator('body')).toContainText(/0176482193|your bag|baggage360/i);

    // Verify status headline exists
    const hasHeadline = await page.getByText(/prioritised|monitored|transit|arrived/i).count();
    expect(hasHeadline).toBeGreaterThan(0);

    // Verify confirmed milestone section exists
    const hasConfirmed = await page.getByText(/confirmed|last confirmed/i).count();
    expect(hasConfirmed).toBeGreaterThan(0);

    // Verify bag journey section exists
    const hasJourney = await page.getByText(/bag journey|checked in|loaded/i).count();
    expect(hasJourney).toBeGreaterThan(0);
  });

  test('displays error state for bag not found', async ({ page, apiGuard }) => {
    // Allow 404 for non-existent bag - this is the expected behavior
    apiGuard.allow(404, '/api/v1/passenger/bags/9999999999/status');
    
    // Log in with passenger credentials
    await page.goto('/login');
    await page.getByLabel(/email/i).clear();
    await page.getByLabel(/email/i).fill('sara.johnson@example.com');
    await page.getByLabel(/password/i).clear();
    await page.getByLabel(/password/i).fill('Demo1234!');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for login to complete (passenger users have role pre-assigned, no role selection needed)
    await page.waitForTimeout(1000);

    // Navigate to non-existent bag
    await page.goto('/passenger/bags/9999999999/status');

    // Wait for loading to complete
    await page.waitForLoadState('networkidle');

    // Verify error message
    const hasError = await page.getByText(/couldn't find|not found|error/i).count();
    expect(hasError).toBeGreaterThan(0);
  });
});
