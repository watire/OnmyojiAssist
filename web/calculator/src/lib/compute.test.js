import { describe, expect, it } from 'vitest';
import { compute } from './compute.js';

describe('compute', () => {
  it('supports addition', () => {
    expect(compute(1, '+', 2)).toBe(3);
  });

  it('supports subtraction', () => {
    expect(compute(5, '-', 8)).toBe(-3);
  });

  it('supports multiplication', () => {
    expect(compute(6, '×', 7)).toBe(42);
  });

  it('supports division', () => {
    expect(compute(8, '÷', 2)).toBe(4);
  });

  it('throws on divide by zero', () => {
    expect(() => compute(8, '÷', 0)).toThrow(/不能除以 0/u);
  });
});
