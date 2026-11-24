import { test, expect } from './_pipeline_guard';

test.describe('Partner Task Queue (wireframe_04)', () => {
  test('logs in with ahmed.hassan@dnata.ae and verifies task queue', async ({ page }) => {
    // Navigate to login
    await page.goto('/');
    
    // Fill login form with partner credentials
    await page.getByLabel(/work email or staff id/i).clear();
    await page.getByLabel(/work email or staff id/i).fill('ahmed.hassan@dnata.ae');
    
    await page.getByLabel(/password/i).clear();
    await page.getByLabel(/password/i).fill('Demo1234!');
    
    // Submit login
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for role selection and select partner
    await expect(page.getByText(/demo role entry/i)).toBeVisible({ timeout: 5000 });
    await page.getByRole('button', { name: /partner handler/i }).click();
    
    // Should navigate to partner task queue
    await expect(page).toHaveURL(/\/partner\/tasks/, { timeout: 5000 });
    
    // Verify page title
    await expect(page.getByRole('heading', { name: /my tasks/i, level: 1 })).toBeVisible();
    
    // Verify scoping banner
    await expect(page.getByText(/you see only tasks assigned to your role/i)).toBeVisible();
    
    // Verify status tabs
    await expect(page.getByRole('tab', { name: /assigned/i })).toBeVisible();
    await expect(page.getByRole('tab', { name: /acknowledged/i })).toBeVisible();
    await expect(page.getByRole('tab', { name: /in progress/i })).toBeVisible();
    await expect(page.getByRole('tab', { name: /completed/i })).toBeVisible();
    
    // Verify assigned tab is active by default
    await expect(page.getByRole('tab', { name: /assigned/i })).toHaveAttribute('aria-current', 'true');
    
    // Verify seed tasks TSK-DXB-1187 and TSK-DXB-1189 appear in assigned tab
    // These are the two assigned tasks from the seed data
    await expect(page.locator('tbody').getByText('TSK-DXB-1187')).toBeVisible();
    await expect(page.locator('tbody').getByText('TSK-DXB-1189')).toBeVisible();
    
    // Verify deadline emphasis on first task (should be critical/warning)
    const firstTaskRow = page.locator('tbody tr').first();
    await expect(firstTaskRow.getByText(/due in/i)).toBeVisible();
    
    // Verify Open task button exists
    await expect(firstTaskRow.getByRole('link', { name: /open task/i })).toBeVisible();
  });
});
