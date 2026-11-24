import { describe, it, expect } from 'vitest';
import TaskDetailPage from '../../pages/partner/TaskDetailPage';

describe('TaskDetailPage', () => {
  it('component is defined', () => {
    expect(TaskDetailPage).toBeDefined();
  });

  it('is a function component', () => {
    expect(typeof TaskDetailPage).toBe('function');
  });
});
