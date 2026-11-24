/**
 * BagStatusPage tests
 */
import { describe, it, expect } from 'vitest';
import BagStatusPage from '../../pages/passenger/BagStatusPage';

describe('BagStatusPage', () => {
  it('component is defined', () => {
    expect(BagStatusPage).toBeDefined();
  });

  it('is a function component', () => {
    expect(typeof BagStatusPage).toBe('function');
  });
});
