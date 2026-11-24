import { describe, it, expect } from 'vitest';
import CaseDetailPage from '../../pages/operations/CaseDetailPage';

describe('CaseDetailPage', () => {
  it('component is defined', () => {
    expect(CaseDetailPage).toBeDefined();
  });

  it('is a function component', () => {
    expect(typeof CaseDetailPage).toBe('function');
  });
});
