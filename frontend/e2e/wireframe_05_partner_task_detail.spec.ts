import { test, expect } from './_pipeline_guard';

test.describe('Partner Task Detail (wireframe_05)', () => {
  test('logs in, opens task TSK-DXB-1187, submits acknowledgement and evidence', async ({ page }) => {
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
    
    // Click on first task (should be TSK-DXB-1187)
    const firstTaskLink = page.locator('tbody tr').first().getByRole('link', { name: /open task/i });
    await firstTaskLink.click();
    
    // Should navigate to task detail page
    await expect(page).toHaveURL(/\/partner\/tasks\/(TSK-[A-Z]+-\d+|[a-f0-9-]+)/, { timeout: 5000 });
    
    // Verify task header shows task ID
    await expect(page.getByRole('heading', { level: 1 })).toContainText('TSK-DXB');
    
    // Verify deadline display
    await expect(page.getByText(/due in/i)).toBeVisible();
    
    // Verify "Your view of the case" section
    await expect(page.getByRole('heading', { name: /your view of the case/i })).toBeVisible();
    await expect(page.getByText(/bag reference/i)).toBeVisible();
    
    // Verify "Hidden from your role" notice
    await expect(page.getByText(/hidden from your role/i)).toBeVisible();
    await expect(page.getByText(/passenger name and booking reference/i)).toBeVisible();
    
    // Verify Instructions section
    await expect(page.getByRole('heading', { name: /instructions/i })).toBeVisible();
    
    // If status is assigned, acknowledge button should be visible
    const acknowledgeButton = page.getByRole('button', { name: /acknowledge task/i });
    const hasAcknowledgeButton = await acknowledgeButton.isVisible().catch(() => false);
    
    if (hasAcknowledgeButton) {
      // Click acknowledge button
      await acknowledgeButton.click();
      
      // Wait for page to reload/update
      await page.waitForTimeout(1000);
      
      // After acknowledgement, the button should disappear
      await expect(acknowledgeButton).not.toBeVisible({ timeout: 5000 });
    }
    
    // Verify evidence form is present
    await expect(page.getByRole('heading', { name: /record evidence/i })).toBeVisible();
    
    // Fill evidence form
    await page.locator('select#ety').selectOption('scan_confirmation');
    await page.locator('input#er').fill('SCAN-DXB-TA-TEST-' + Date.now());
    await page.locator('textarea#en').fill('Test evidence submission from E2E test');
    
    // Submit evidence
    const submitButton = page.getByRole('button', { name: /submit evidence/i });
    await submitButton.click();
    
    // Wait for page to reload/update (evidence form should still be visible after submit)
    await page.waitForTimeout(1000);
    
    // Verify the page still shows the task header
    await expect(page.getByRole('heading', { level: 1 })).toContainText('TSK-DXB');
    
    // Verify breadcrumb navigation works
    await page.getByRole('link', { name: /my tasks/i }).first().click();
    await expect(page).toHaveURL(/\/partner\/tasks$/, { timeout: 5000 });
  });
});
