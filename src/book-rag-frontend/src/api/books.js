import api from './axios';
import { config } from '../config';

// === МОК ДАННЫЕ (для тестирования без бекенда) ===
const MOCK_BOOKS = [
  {
    id: '550e8400-e29b-41d4-a716-446655440001',
    name: 'Война и мир',
    year: 1869,
    genres: ['Роман', 'Исторический'],
    author: 'Лев Толстой',
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440002',
    name: 'Преступление и наказание',
    year: 1866,
    genres: ['Роман', 'Психологический'],
    author: 'Фёдор Достоевский',
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440003',
    name: 'Мастер и Маргарита',
    year: 1967,
    genres: ['Роман', 'Фантастика'],
    author: 'Михаил Булгаков',
  },
];

// GET /books
export const getBooks = async () => {
  if (config.USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, config.MOCK_DELAY));
    return { data: MOCK_BOOKS };
  }
  return api.get('/books');
};

// POST /books (FormData)
export const uploadBook = async (file) => {
  if (config.USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    const newBook = {
      id: `550e8400-e29b-41d4-a716-${Date.now()}`,
      name: file.name.replace('.pdf', ''),
      year: new Date().getFullYear(),
      genres: ['Новый'],
      author: 'Неизвестный',
    };
    MOCK_BOOKS.push(newBook);
    return { data: newBook, status: 201 };
  }
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/books', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// PATCH /books/<bookId>
export const updateBook = async (bookId, data) => {
  if (config.USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, config.MOCK_DELAY));
    const index = MOCK_BOOKS.findIndex((b) => b.id === bookId);
    if (index === -1) {
      const error = new Error('Book not found');
      error.response = { status: 404, data: { errorCode: 'NotFound', userMessage: 'Книга не найдена' } };
      throw error;
    }
    if (Object.keys(data).length === 0) {
      const error = new Error('No fields to update');
      error.response = { status: 304, data: { errorCode: 'NotModified', userMessage: 'Нет полей для обновления' } };
      throw error;
    }
    MOCK_BOOKS[index] = { ...MOCK_BOOKS[index], ...data };
    return { data: MOCK_BOOKS[index], status: 200 };
  }
  return api.patch(`/books/${bookId}`, data);
};

// DELETE /books/<bookId>
export const deleteBook = async (bookId) => {
  if (config.USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, config.MOCK_DELAY));
    const index = MOCK_BOOKS.findIndex((b) => b.id === bookId);
    if (index === -1) {
      const error = new Error('Book not found');
      error.response = { status: 404, data: { errorCode: 'NotFound', userMessage: 'Книга не найдена' } };
      throw error;
    }
    MOCK_BOOKS.splice(index, 1);
    return { status: 204 };
  }
  return api.delete(`/books/${bookId}`);
};