/**
 * E2E test for wireframe_08_executive_overview
 * Tests executive overview screen with KPIs, trend chart, and category breakdown
 */
import { test, expect } from './_pipeline_guard';

test.describe('Executive Overview - Wireframe 08', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Login as executive user
    await page.getByLabel(/work email or staff id/i).fill('fatima.albanna@emirates.ae');
    await page.getByLabel(/password/i).fill('Demo1234!');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for role selection screen
    await expect(page.getByRole('button', { name: /operations lead/i }).first()).toBeVisible();
    
    // Select executive role by clicking the last button in the grid (Executive is 4th)
    await page.getByRole('button').filter({ hasText: /^Executive/ }).click();
    
    // Wait for executive overview to load
    await expect(page.getByRole('heading', { name: /baggage operations overview/i })).toBeVisible({ timeout: 10000 });
  });
  
  test('displays executive overview with KPIs, trend chart, and category breakdown', async ({ page }) => {
    // Verify KPI cards are displayed (7 cards)
    const kpiSection = page.locator('section[aria-label="Key metrics"]');
    await expect(kpiSection).toBeVisible();
    
    const kpiCards = kpiSection.locator('> div');
    await expect(kpiCards).toHaveCount(7);
    
    // Verify KPI labels are present in the KPI section specifically
    await expect(kpiSection.getByText(/exception rate.*per.*bags/i).first()).toBeVisible();
    await expect(kpiSection.getByText(/recovered within cutoff/i).first()).toBeVisible();
    await expect(kpiSection.getByText(/mean time to decision/i).first()).toBeVisible();
    await expect(kpiSection.getByText(/passengers impacted/i).first()).toBeVisible();
    await expect(kpiSection.getByText(/open case ageing/i).first()).toBeVisible();
    await expect(kpiSection.getByText(/data freshness|cases with stale data/i).first()).toBeVisible();
    
    // Verify trend indicators are present (some trend direction shown)
    await expect(page.getByText(/flat.*vs prior 14 days|flat/i).first()).toBeVisible();
    
    // Verify trend chart section
    await expect(page.getByRole('heading', { name: /exceptions and recoveries per day/i })).toBeVisible();
    
    // Verify chart legend mentions exceptions and recoveries
    await expect(page.getByText(/exceptions.*bags/i).first()).toBeVisible();
    await expect(page.getByText(/recovered.*bags/i).first()).toBeVisible();
    
    // Verify category breakdown section
    await expect(page.getByRole('heading', { name: /passenger impact by exception category/i })).toBeVisible();
    
    // Verify category bars with labels (structure test, not exact counts)
    await expect(page.getByText(/connection risk/i)).toBeVisible();
    await expect(page.getByText(/missing scan/i)).toBeVisible();
    await expect(page.getByText(/misroute/i)).toBeVisible();
    await expect(page.getByText(/customs hold/i)).toBeVisible();
    
    // Verify provenance and freshness section
    await expect(page.getByText(/wasla/i)).toBeVisible();
    await expect(page.getByText(/handler feed|stale/i).first()).toBeVisible();
    
    // Verify interpretation limits notice
    await expect(page.getByText(/demo dataset.*simulated/i)).toBeVisible();
  });
  
  test('displays freshness warning when sources are stale', async ({ page }) => {
    // Verify freshness warning chip is displayed
    await expect(page.getByText(/sources fresh.*of/i)).toBeVisible();
  });
  
  test('allows date range selection', async ({ page }) => {
    // Verify date range controls are present
    const dateInputs = page.locator('input[type="date"]');
    await expect(dateInputs).toHaveCount(2);
    
    // Verify "Last 14 days" preset is shown
    await expect(page.getByText(/last 14 days/i)).toBeVisible();
  });
});
