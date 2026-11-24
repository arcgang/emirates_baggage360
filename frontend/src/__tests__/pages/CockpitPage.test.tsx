import { describe, it, expect } from 'vitest';
import CockpitPage from '../../pages/operations/CockpitPage';

describe('CockpitPage', () => {
  it('component is defined', () => {
    expect(CockpitPage).toBeDefined();
  });

  it('is a function component', () => {
    expect(typeof CockpitPage).toBe('function');
  });
});
