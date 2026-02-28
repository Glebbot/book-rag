import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import BookTable from './index';

// Mock для API
vi.mock('../../api/books', () => ({
  getBooks: vi.fn(() => Promise.resolve({
    data: [
      {
        id: '1',
        name: 'Война и мир',
        year: 1869,
        genres: ['Роман', 'Исторический'],
        author: 'Лев Толстой',
      },
      {
        id: '2',
        name: 'Преступление и наказание',
        year: 1866,
        genres: ['Роман', 'Психологический'],
        author: 'Фёдор Достоевский',
      },
    ],
  })),
  uploadBook: vi.fn(() => Promise.resolve({ data: {}, status: 201 })),
  updateBook: vi.fn(() => Promise.resolve({ data: {}, status: 200 })),
  deleteBook: vi.fn(() => Promise.resolve({ status: 204 })),
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('BookTable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('должен рендерить таблицу с книгами', async () => {
    renderWithRouter(<BookTable />);

    await waitFor(() => {
      expect(screen.getByText('Война и мир')).toBeInTheDocument();
      expect(screen.getByText('Преступление и наказание')).toBeInTheDocument();
    });
  });

  it('должен показывать кнопку добавления книги', () => {
    renderWithRouter(<BookTable />);
    expect(screen.getByText(/добавить книгу/i)).toBeInTheDocument();
  });

  it('должен показывать поиск', () => {
    renderWithRouter(<BookTable />);
    expect(screen.getByPlaceholderText(/поиск по названию или автору/i)).toBeInTheDocument();
  });

  it('должен фильтровать книги по поиску', async () => {
    renderWithRouter(<BookTable />);

    await waitFor(() => {
      expect(screen.getByText('Война и мир')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/поиск по названию или автору/i);
    fireEvent.change(searchInput, { target: { value: 'Толстой' } });

    await waitFor(() => {
      expect(screen.getByText('Война и мир')).toBeInTheDocument();
      expect(screen.queryByText('Преступление и наказание')).not.toBeInTheDocument();
    });
  });

  it('должен показывать кнопки действий для каждой книги', async () => {
    renderWithRouter(<BookTable />);

    await waitFor(() => {
      expect(screen.getAllByText(/чат/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/редактировать/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/удалить/i).length).toBeGreaterThan(0);
    });
  });
});