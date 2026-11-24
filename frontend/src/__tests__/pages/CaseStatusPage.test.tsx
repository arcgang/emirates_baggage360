/**
 * CaseStatusPage tests
 */
import { describe, it, expect } from 'vitest';
import CaseStatusPage from '../../pages/passenger/CaseStatusPage';

describe('CaseStatusPage', () => {
  it('component is defined', () => {
    expect(CaseStatusPage).toBeDefined();
  });

  it('is a function component', () => {
    expect(typeof CaseStatusPage).toBe('function');
  });
});
