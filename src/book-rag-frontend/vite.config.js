import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.js',
    include: ['**/*.{test,spec}.{js,jsx}'],
    // Настройка покрытия
    coverage: {
      provider: 'v8', // Используем v8 для точных данных
      reporter: ['text', 'json', 'html'], // Форматы отчета
      exclude: [
        'node_modules/',
        'src/tests/',
        '**/*.config.js',
        '**/mocks.js',
      ],
    },
  },
});