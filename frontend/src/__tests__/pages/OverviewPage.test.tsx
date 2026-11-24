/**
 * Unit tests for Executive OverviewPage
 */
import { describe, it, expect } from 'vitest';
import { OverviewPage } from '../../pages/executive/OverviewPage';

describe('OverviewPage', () => {
  it('component is defined', () => {
    expect(OverviewPage).toBeDefined();
  });
  
  it('component is a function', () => {
    expect(typeof OverviewPage).toBe('function');
  });
});
