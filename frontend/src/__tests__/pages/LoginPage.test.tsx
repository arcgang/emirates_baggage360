import { describe, it, expect } from 'vitest';
import LoginPage from '../../pages/LoginPage';

describe('LoginPage', () => {
  it('component is defined', () => {
    expect(LoginPage).toBeDefined();
  });

  it('is a function component', () => {
    expect(typeof LoginPage).toBe('function');
  });
});
