import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 03: Case Detail', () => {
  test.beforeEach(async ({ page }) => {
    // Log in and navigate to case detail
    await page.goto('/login');
    
    await page.getByLabel(/work email or staff id/i).fill('mariam.alsuwaidi@baggage360.demo');
    await page.getByLabel('Password').fill('Demo1234!');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Select operations role
    await page.getByRole('button', { name: /operations lead/i }).click();
    
    // Navigate to case detail page
    await page.goto('/operations/cases/BC-DXB-240611');
    
    // Wait for case detail to load
    await expect(page.getByRole('heading', { name: /bc-dxb-240611/i })).toBeVisible();
  });

  test('displays case header with metadata', async ({ page }) => {
    // Verify case reference and exception type
    await expect(page.getByRole('heading', { name: /bc-dxb-240611/i })).toBeVisible();
    await expect(page.getByText(/connection at risk, late inbound/i).first()).toBeVisible();
    
    // Verify severity badge (use first to avoid matching "critical" in rationale text)
    await expect(page.getByText(/critical/i).first()).toBeVisible();
    
    // Verify status
    await expect(page.getByText(/under_review/i)).toBeVisible();
    
    // Verify time to cutoff
    await expect(page.getByText(/time to baggage cutoff/i)).toBeVisible();
    await expect(page.getByText(/36 min/i).first()).toBeVisible();
  });

  test('displays bag timeline with observed events', async ({ page }) => {
    // Verify bag timeline section
    await expect(page.getByRole('heading', { name: /bag timeline/i })).toBeVisible();
    
    // Verify bag tabs
    await expect(page.getByRole('tab', { name: /0176 482193/i })).toBeVisible();
    
    // Verify milestones
    await expect(page.getByText(/accepted at origin check-in/i)).toBeVisible();
    await expect(page.getByText(/loaded on ek 0201/i)).toBeVisible();
    await expect(page.getByText(/arrived dxb/i)).toBeVisible();
    
    // Verify fact type badges
    await expect(page.getByText(/observed/i).first()).toBeVisible();
  });

  test('displays journey context with connection details', async ({ page }) => {
    // Verify journey context section
    await expect(page.getByRole('heading', { name: /journey context/i })).toBeVisible();
    
    // Verify inbound flight (use first to avoid multiple matches)
    await expect(page.getByText(/ek 0201/i).first()).toBeVisible();
    await expect(page.getByText(/arrived 19:58 gst/i)).toBeVisible();
    
    // Verify onward flight (use first to avoid multiple matches)
    await expect(page.getByText(/ek 0507/i).first()).toBeVisible();
    await expect(page.getByText(/departs 21:10 gst/i)).toBeVisible();
    
    // Verify connection window (use first to avoid multiple matches)
    await expect(page.getByText(/42 min/i).first()).toBeVisible();
    await expect(page.getByText(/60 min minimum/i).first()).toBeVisible();
  });

  test('displays recommendations with confidence scores', async ({ page }) => {
    // Verify recommendations section
    await expect(page.getByRole('heading', { name: /recommendations/i })).toBeVisible();
    
    // Verify R1 recommendation (use first to avoid matching options in select)
    await expect(page.getByText(/r1 · priority transfer to ek 0507/i).first()).toBeVisible();
    await expect(page.getByText(/confidence.*0\.78/i)).toBeVisible();
    
    // Verify evidence list (use first to avoid multiple matches)
    await expect(page.getByText(/ek 0201 arrived 19:58/i).first()).toBeVisible();
    await expect(page.getByText(/gate change b14.*b22/i)).toBeVisible();
  });

  test('displays approval form with decision options', async ({ page }) => {
    // Verify approval section
    await expect(page.getByRole('heading', { name: /approval decision/i })).toBeVisible();
    
    // Verify decision dropdown - use exact label text to avoid ambiguity
    const decisionSelect = page.getByLabel('Decision', { exact: true });
    await expect(decisionSelect).toBeVisible();
    
    // Verify rationale field
    const rationaleTextarea = page.getByLabel(/rationale/i);
    await expect(rationaleTextarea).toBeVisible();
    
    // Verify submit button
    await expect(page.getByRole('button', { name: /approve and dispatch tasks/i })).toBeVisible();
  });

  test('displays audit trail tab', async ({ page }) => {
    // Verify tabs
    await expect(page.getByRole('tab', { name: /overview/i })).toBeVisible();
    await expect(page.getByRole('tab', { name: /tasks/i })).toBeVisible();
    await expect(page.getByRole('tab', { name: /audit trail/i })).toBeVisible();
    
    // Audit trail should be active by default
    await expect(page.getByRole('tab', { name: /audit trail/i })).toHaveAttribute('aria-current', 'true');
    
    // Verify audit table headers
    await expect(page.getByRole('columnheader', { name: /time/i })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: /action/i })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: /actor/i })).toBeVisible();
  });

  test('submits approval decision (mock)', async ({ page }) => {
    // This test verifies the form submission flow
    // In a real scenario with backend, it would verify task creation
    
    // Fill rationale (pre-filled, but verify it's there)
    const rationaleTextarea = page.getByLabel(/rationale/i);
    await expect(rationaleTextarea).toHaveValue(/connection window/i);
    
    // Click approve button
    const approveButton = page.getByRole('button', { name: /approve and dispatch tasks/i });
    await approveButton.click();
    
    // Verify confirmation dialog appears
    await expect(page.getByText(/confirm approval/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /confirm/i })).toBeVisible();
    
    // Note: Actual submission would trigger API call and show success/error state
  });
});
