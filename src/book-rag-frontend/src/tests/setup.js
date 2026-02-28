// src/tests/setup.js
import '@testing-library/jest-dom';

// Mock для ResizeObserver (нужен для Ant Design)
global.ResizeObserver = class ResizeObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe() {
    this.callback([], this);
  }
  unobserve() {}
  disconnect() {}
};

// Mock для scrollIntoView
Element.prototype.scrollIntoView = vi.fn();

// Mock для window.scrollTo
window.scrollTo = vi.fn();

// Mock для matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock для localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;