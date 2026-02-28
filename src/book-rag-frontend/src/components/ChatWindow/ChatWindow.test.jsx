import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ChatWindow from './index';

// Mock для API
vi.mock('../../api/search', () => ({
  sendMessage: vi.fn(() => Promise.resolve({
    data: {
      messages: [
        { role: 'user', content: 'Тест' },
        { role: 'assistant', content: 'Ответ ассистента' },
      ],
    },
  })),
  getBookById: vi.fn(() => Promise.resolve({
    data: { id: 'test-id', name: 'Тестовая книга' },
  })),
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ChatWindow', () => {
  const mockBookId = 'test-id';
  const mockBookName = 'Тестовая книга';

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('должен рендериться с названием книги', () => {
    renderWithRouter(<ChatWindow bookId={mockBookId} bookName={mockBookName} />);
    // Используем getAllByText так как текст в 2 местах (шапка + приветствие)
    const bookTitles = screen.getAllByText(mockBookName);
    expect(bookTitles.length).toBeGreaterThan(0);
  });

  it('должен показывать поле ввода сообщения', () => {
    renderWithRouter(<ChatWindow bookId={mockBookId} bookName={mockBookName} />);
    const input = screen.getByPlaceholderText(/написать сообщение/i);
    expect(input).toBeInTheDocument();
  });

  it('должен показывать кнопку отправки', () => {
    renderWithRouter(<ChatWindow bookId={mockBookId} bookName={mockBookName} />);
    // Используем aria-label который мы добавили
    const sendButton = screen.getByRole('button', { name: /отправить/i });
    expect(sendButton).toBeInTheDocument();
  });

  it('должен показывать приветственное сообщение когда нет сообщений', () => {
    renderWithRouter(<ChatWindow bookId={mockBookId} bookName={mockBookName} />);
    expect(screen.getByText(/задайте вопрос по книге/i)).toBeInTheDocument();
  });

  it('должен показывать кнопку очистки когда есть сообщения', async () => {
    const { sendMessage } = await import('../../api/search');
    sendMessage.mockResolvedValueOnce({
      data: {
        messages: [
          { role: 'user', content: 'Тест' },
          { role: 'assistant', content: 'Ответ' },
        ],
      },
    });

    renderWithRouter(<ChatWindow bookId={mockBookId} bookName={mockBookName} />);

    // Вводим сообщение
    const input = screen.getByPlaceholderText(/написать сообщение/i);
    fireEvent.change(input, { target: { value: 'Привет' } });

    // Отправляем
    const sendButton = screen.getByRole('button', { name: /отправить/i });
    fireEvent.click(sendButton);

    // Ждём появления кнопки очистки
    await waitFor(() => {
      expect(screen.getByText(/очистить/i)).toBeInTheDocument();
    });
  });

  it('должен блокировать отправку пустого сообщения', () => {
    renderWithRouter(<ChatWindow bookId={mockBookId} bookName={mockBookName} />);
    const sendButton = screen.getByRole('button', { name: /отправить/i });
    expect(sendButton).toBeDisabled();
  });

  it('должен показывать индикатор загрузки во время ожидания ответа', async () => {
    const { sendMessage } = await import('../../api/search');
    sendMessage.mockImplementation(() => new Promise(resolve =>
      setTimeout(() => resolve({
        data: { messages: [{ role: 'assistant', content: 'Ответ' }] }
      }), 100)
    ));

    renderWithRouter(<ChatWindow bookId={mockBookId} bookName={mockBookName} />);

    const input = screen.getByPlaceholderText(/написать сообщение/i);
    fireEvent.change(input, { target: { value: 'Привет' } });

    const sendButton = screen.getByRole('button', { name: /отправить/i });
    fireEvent.click(sendButton);

    // Проверяем что кнопка заблокирована во время загрузки
    await waitFor(() => {
      expect(sendButton).toBeDisabled();
    });
  });
});