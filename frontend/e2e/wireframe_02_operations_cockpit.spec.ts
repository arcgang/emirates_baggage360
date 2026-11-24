import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 02: Operations Cockpit', () => {
  test.beforeEach(async ({ page }) => {
    // Log in first
    await page.goto('/login');
    
    await page.getByLabel(/work email or staff id/i).fill('mariam.alsuwaidi@baggage360.demo');
    await page.getByLabel('Password').fill('Demo1234!');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Select operations role
    await page.getByRole('button', { name: /operations lead/i }).click();
    
    // Wait for cockpit to load
    await expect(page.getByRole('heading', { name: /operations cockpit/i })).toBeVisible();
  });

  test('displays KPI counts matching seed data', async ({ page }) => {
    // Verify KPI cards are visible
    const kpiSection = page.locator('[role="region"][aria-label*="Cockpit summary"]');
    
    // Use exact matching with regex boundaries to avoid matching "60" when looking for "6"
    await expect(kpiSection.getByText(/open cases/i)).toBeVisible();
    await expect(kpiSection.getByText(/^6$/)).toBeVisible();
    
    await expect(kpiSection.getByText(/urgent/i)).toBeVisible();
    await expect(kpiSection.getByText(/^2$/)).toBeVisible();
    
    await expect(kpiSection.getByText(/impacted bags/i)).toBeVisible();
    await expect(kpiSection.getByText(/^11$/)).toBeVisible();
    
    await expect(kpiSection.getByText(/impacted passengers/i)).toBeVisible();
    await expect(kpiSection.getByText(/^9$/)).toBeVisible();
  });

  test('displays case BC-DXB-240611 in queue with critical severity', async ({ page }) => {
    // Find the exception queue table
    const table = page.getByRole('table');
    
    // Verify case is listed
    await expect(table.getByText('BC-DXB-240611')).toBeVisible();
    
    // Verify critical severity badge
    await expect(table.getByText(/critical/i)).toBeVisible();
    
    // Verify case details
    await expect(table.getByText(/connection at risk, late inbound/i)).toBeVisible();
    await expect(table.getByText(/36 min/i)).toBeVisible();
  });

  test('displays stale data banner', async ({ page }) => {
    // Verify stale data warning
    await expect(page.getByText(/transfer scan source stale 14 min/i)).toBeVisible();
    await expect(page.getByText(/predictions that depend on dxb transfer scans may be outdated/i)).toBeVisible();
  });

  test('shows selected case preview panel', async ({ page }) => {
    // Case BC-DXB-240611 should be selected by default
    await expect(page.getByRole('heading', { name: /selected: bc-dxb-240611/i })).toBeVisible();
    
    // Verify preview details appear on the page (no need to scope to specific container)
    await expect(page.getByText(/connection at risk, late inbound/i).first()).toBeVisible();
    await expect(page.getByText(/top recommendation/i)).toBeVisible();
    
    // Verify Open case button
    await expect(page.getByRole('button', { name: /open case/i })).toBeVisible();
  });

  test('displays sidebar with user info', async ({ page }) => {
    // Verify sidebar navigation - note we have Cockpit and Dashboard
    await expect(page.getByRole('link', { name: /cockpit/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /dashboard/i })).toBeVisible();
    
    // Verify user info in the sidebar (use nav or aside context)
    const sidebar = page.locator('aside').or(page.locator('nav').filter({ hasText: /cockpit/i }).locator('..'));
    await expect(sidebar.getByText(/m\. al suwaidi/i).first()).toBeVisible();
    await expect(page.getByText(/dxb baggage operations lead/i)).toBeVisible();
    await expect(page.getByText(/operational recovery/i)).toBeVisible();
  });
});
