import { describe, it, expect } from 'vitest';
import { config } from './index.js';

describe('Config', () => {
  it('должен экспортировать объект config', () => {
    expect(config).toBeDefined();
    expect(typeof config).toBe('object');
  });

  it('должен содержать USE_MOCK флаг', () => {
    expect(config).toHaveProperty('USE_MOCK');
    expect(typeof config.USE_MOCK).toBe('boolean');
  });

  it('должен содержать API_URL', () => {
    expect(config).toHaveProperty('API_URL');
    expect(typeof config.API_URL).toBe('string');
  });

  it('должен содержать MAX_MESSAGE_LENGTH', () => {
    expect(config).toHaveProperty('MAX_MESSAGE_LENGTH');
    expect(config.MAX_MESSAGE_LENGTH).toBeGreaterThan(0);
  });

  it('должен содержать MOCK_DELAY', () => {
    expect(config).toHaveProperty('MOCK_DELAY');
    expect(config.MOCK_DELAY).toBeGreaterThan(0);
  });
});