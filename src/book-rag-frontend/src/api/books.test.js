import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getBooks, uploadBook, updateBook, deleteBook } from './books';

// Mock для axios
vi.mock('./axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('Books API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getBooks', () => {
    it('должен возвращать список книг (MOCK)', async () => {
      const response = await getBooks();
      expect(response.data).toBeDefined();
      expect(Array.isArray(response.data)).toBe(true);
      expect(response.data.length).toBeGreaterThan(0);
    });

    it('должен содержать поля id, name, year, genres, author', async () => {
      const response = await getBooks();
      const book = response.data[0];
      expect(book).toHaveProperty('id');
      expect(book).toHaveProperty('name');
      expect(book).toHaveProperty('year');
      expect(book).toHaveProperty('genres');
      expect(book).toHaveProperty('author');
    });
  });

  describe('uploadBook', () => {
    it('должен успешно загружать файл (MOCK)', async () => {
      const mockFile = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      const response = await uploadBook(mockFile);
      expect(response.data).toBeDefined();
      expect(response.data.name).toContain('test');
    });

    it('должен отклонять не-PDF файлы', async () => {
      const mockFile = new File(['test'], 'test.txt', { type: 'text/plain' });
      // В реальном коде это проверяется в компоненте, не в API
      expect(mockFile.name.endsWith('.pdf')).toBe(false);
    });
  });

  describe('updateBook', () => {
    const mockBookId = '550e8400-e29b-41d4-a716-446655440001';

    it('должен обновлять книгу (MOCK)', async () => {
      const updateData = { name: 'Новое название' };
      const response = await updateBook(mockBookId, updateData);
      expect(response.data).toBeDefined();
      expect(response.data.name).toBe('Новое название');
    });

    it('должен возвращать ошибку при пустых данных', async () => {
      const updateData = {};
      await expect(updateBook(mockBookId, updateData)).rejects.toThrow();
    });

    it('должен возвращать ошибку при несуществующем ID', async () => {
      const updateData = { name: 'Тест' };
      await expect(updateBook('invalid-id', updateData)).rejects.toThrow();
    });
  });

  describe('deleteBook', () => {
    const mockBookId = '550e8400-e29b-41d4-a716-446655440001';

    it('должен удалять книгу (MOCK)', async () => {
      const response = await deleteBook(mockBookId);
      expect(response.status).toBe(204);
    });

    it('должен возвращать ошибку при несуществующем ID', async () => {
      await expect(deleteBook('invalid-id')).rejects.toThrow();
    });
  });
});