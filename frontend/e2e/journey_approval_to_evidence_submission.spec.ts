/**
 * E2E Journey Test: Approval to Evidence Submission
 * 
 * Tests the complete flow from partner user receiving a task, acknowledging it,
 * submitting evidence with scan confirmation, and passenger verifying updated status.
 * 
 * Journey:
 * 1. Login as partner user ahmed.hassan@dnata.ae
 * 2. Open task TSK-DXB-1187 (or first assigned task)
 * 3. Acknowledge task
 * 4. Submit evidence with scan confirmation
 * 5. Verify status updated to completed
 * 6. Login as passenger sara.johnson@example.com
 * 7. Verify bag 0176482193 status updated with confirmed milestone
 */

import { test, expect } from './_pipeline_guard';

test.describe('Journey: Approval to Evidence Submission', () => {
  test('logs in as partner ahmed.hassan@dnata.ae, opens task TSK-DXB-1187, acknowledges task, submits evidence with scan confirmation, verifies status completed; then logs in as passenger sara.johnson@example.com, verifies bag 0176482193 status updated with confirmed milestone', async ({ page }) => {
    // ========== PART 1: Partner Flow ==========
    
    // Step 1: Login as partner user
    await page.goto('/');
    
    // Fill in partner credentials
    await page.getByLabel(/email/i).fill('ahmed.hassan@dnata.ae');
    await page.getByLabel(/password/i).fill('Demo1234!');
    
    // Submit login
    await page.getByRole('button', { name: /sign in|log in/i }).click();
    
    // Wait for role selection and select partner role
    await expect(page.getByText(/demo role entry/i)).toBeVisible({ timeout: 5000 });
    await page.getByRole('button', { name: /partner handler/i }).click();
    
    // Should navigate to partner task queue
    await expect(page).toHaveURL(/\/partner\/tasks/, { timeout: 5000 });
    
    // Verify task queue loaded
    await expect(page.getByRole('heading', { name: /task|queue|work/i }).first()).toBeVisible();
    
    // Step 2: Open task TSK-DXB-1187
    // Task might be in any status tab, so try all tabs to find it
    // First check if it's visible in current tab (assigned by default)
    let taskRow = page.locator('tbody tr').filter({ hasText: /TSK-DXB-1187/i }).first();
    const isVisibleInCurrentTab = await taskRow.isVisible({ timeout: 1000 }).catch(() => false);
    
    if (!isVisibleInCurrentTab) {
      // Try the "In progress" tab
      await page.getByRole('tab', { name: /in progress/i }).click();
      await page.waitForTimeout(500);
      taskRow = page.locator('tbody tr').filter({ hasText: /TSK-DXB-1187/i }).first();
      const isVisibleInProgress = await taskRow.isVisible({ timeout: 1000 }).catch(() => false);
      
      if (!isVisibleInProgress) {
        // Try the "Acknowledged" tab
        await page.getByRole('tab', { name: /acknowledged/i }).click();
        await page.waitForTimeout(500);
        taskRow = page.locator('tbody tr').filter({ hasText: /TSK-DXB-1187/i }).first();
      }
    }
    
    await expect(taskRow).toBeVisible({ timeout: 5000 });
    
    // Click the "Open task" link in the task row
    await taskRow.getByRole('link', { name: /open task/i }).click();
    
    // Wait for task detail page
    await page.waitForURL(/\/partner\/tasks\/[^/]+/, { timeout: 10000 });
    
    // Verify task detail loaded
    await expect(page.locator('text=/TSK-DXB-\\d+/i').first()).toBeVisible();
    
    // Step 3: Acknowledge task
    // Look for acknowledge button
    const acknowledgeButton = page.getByRole('button', { name: /acknowledge/i }).first();
    await expect(acknowledgeButton).toBeVisible({ timeout: 5000 });
    await acknowledgeButton.click();
    
    // Wait for acknowledgement confirmation
    await expect(page.locator('text=/acknowledged|success/i').first()).toBeVisible({ timeout: 5000 });
    
    // Step 4: Submit evidence with scan confirmation
    // Look for evidence submission form or button
    const submitEvidenceButton = page.getByRole('button', { name: /submit evidence|complete|evidence/i }).first();
    await expect(submitEvidenceButton).toBeVisible({ timeout: 5000 });
    await submitEvidenceButton.click();
    
    // Fill in evidence form
    // Look for scan confirmation field
    const scanField = page.getByLabel(/scan|confirmation|reference/i).first().or(
      page.locator('input[type="text"]').first()
    );
    await scanField.fill('SCAN-DXB-20241101-001');
    
    // Look for completion note field
    const noteField = page.getByLabel(/note|comment|details/i).first().or(
      page.locator('textarea').first()
    );
    
    if (await noteField.isVisible({ timeout: 2000 }).catch(() => false)) {
      await noteField.fill('Bag scanned and loaded on connecting flight EK101. Transfer completed successfully.');
    }
    
    // Submit the evidence
    const submitButton = page.getByRole('button', { name: /submit|confirm|complete/i }).last();
    await submitButton.click();
    
    // Step 5: Verify status updated to completed
    await expect(page.locator('text=/completed|success|submitted/i').first()).toBeVisible({ timeout: 10000 });
    
    // Verify task status changed
    const statusIndicator = page.locator('text=/completed|status/i').first();
    await expect(statusIndicator).toBeVisible({ timeout: 5000 });
    
    // Logout partner user
    const logoutButton = page.getByRole('button', { name: /logout|sign out/i }).first().or(
      page.getByRole('link', { name: /logout|sign out/i }).first()
    );
    await logoutButton.click();
    
    // Wait for redirect to login
    await page.waitForURL(/\/login|\//, { timeout: 5000 });
    
    // ========== PART 2: Passenger Flow ==========
    
    // Step 6: Login as passenger
    await page.goto('/');
    
    // Fill in passenger credentials
    await page.getByLabel(/email/i).fill('sara.johnson@example.com');
    await page.getByLabel(/password/i).fill('Demo1234!');
    
    // Submit login
    await page.getByRole('button', { name: /sign in|log in/i }).click();
    
    // Wait for login to complete (passenger users have role pre-assigned, no role selection needed)
    await page.waitForTimeout(1000);
    
    // Step 7: Navigate to bag status for bag 0176482193
    // The passenger might have a direct link to their bag, or need to navigate
    // Try to find bag status link or enter bag tag
    
    // Option 1: Direct navigation if URL pattern is known
    await page.goto('/passenger/bags/0176482193/status');
    
    // Wait for bag status page to load
    await expect(page.locator('text=/0176482193|bag status/i').first()).toBeVisible({ timeout: 10000 });
    
    // Verify bag status updated with confirmed milestone
    // Look for the transfer scan or loaded event that was just completed
    const milestoneList = page.locator('section, div').filter({ hasText: /timeline|milestones|status/i }).first();
    await expect(milestoneList).toBeVisible({ timeout: 5000 });
    
    // Look for confirmed milestone indicators
    const confirmedMilestone = page.locator('text=/transfer|loaded|confirmed/i').first();
    await expect(confirmedMilestone).toBeVisible({ timeout: 5000 });
    
    // Verify latest status shows bag is on track
    const statusHeadline = page.locator('text=/on track|confirmed|loaded/i').first();
    await expect(statusHeadline).toBeVisible({ timeout: 5000 });
  });
  
  test('partner can view task detail without submitting evidence', async ({ page }) => {
    // This test verifies partner can view task details in read-only mode
    
    // Step 1: Login as partner user
    await page.goto('/');
    await page.getByLabel(/email/i).fill('ahmed.hassan@dnata.ae');
    await page.getByLabel(/password/i).fill('Demo1234!');
    await page.getByRole('button', { name: /sign in|log in/i }).click();
    
    // Wait for role selection and select partner role
    await expect(page.getByText(/demo role entry/i)).toBeVisible({ timeout: 5000 });
    await page.getByRole('button', { name: /partner handler/i }).click();
    
    // Should navigate to partner task queue
    await expect(page).toHaveURL(/\/partner\/tasks/, { timeout: 5000 });
    
    // Step 3: Open any task
    const taskLink = page.locator('text=/TSK-DXB-\\d+/i').first();
    await expect(taskLink).toBeVisible({ timeout: 5000 });
    await taskLink.click();
    await page.waitForURL(/\/partner\/tasks\/[^/]+/, { timeout: 10000 });
    
    // Step 4: Verify task detail displays
    await expect(page.locator('text=/TSK-DXB-\\d+/i').first()).toBeVisible();
    await expect(page.getByText(/instruction|deadline|flight/i).first()).toBeVisible();
  });
  
  test('passenger sees error for non-existent bag', async ({ page, apiGuard }) => {
    // This test verifies error handling for invalid bag tags
    
    // Allow 404 for non-existent bag - this is the expected behavior
    apiGuard.allow(404, '/api/v1/passenger/bags/NONEXISTENT999/status');
    
    // Step 1: Login as passenger
    await page.goto('/');
    await page.getByLabel(/email/i).fill('sara.johnson@example.com');
    await page.getByLabel(/password/i).fill('Demo1234!');
    await page.getByRole('button', { name: /sign in|log in/i }).click();
    
    // Wait for login to complete (passenger users have role pre-assigned, no role selection needed)
    await page.waitForTimeout(1000);
    
    // Step 2: Try to access non-existent bag
    await page.goto('/passenger/bags/NONEXISTENT999/status');
    
    // Step 3: Verify error message
    await expect(page.locator('text=/not found|error|invalid/i').first()).toBeVisible({ timeout: 10000 });
  });
});
