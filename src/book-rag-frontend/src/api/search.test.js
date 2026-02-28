import { describe, it, expect, beforeEach, vi } from 'vitest';
import { sendMessage, getBookById } from './search';

describe('Search API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('sendMessage', () => {
    const mockBookId = '550e8400-e29b-41d4-a716-446655440001';
    const mockMessages = [
      { role: 'user', content: 'Привет' },
    ];

    it('должен отправлять сообщение и получать ответ (MOCK)', async () => {
      const response = await sendMessage(mockBookId, mockMessages);
      expect(response.data).toBeDefined();
      expect(response.data.messages).toBeDefined();
      expect(response.data.messages.length).toBeGreaterThan(mockMessages.length);
    });

    it('должен возвращать сообщение с ролью assistant', async () => {
      const response = await sendMessage(mockBookId, mockMessages);
      const lastMessage = response.data.messages[response.data.messages.length - 1];
      expect(lastMessage.role).toBe('assistant');
      expect(lastMessage.content).toBeDefined();
    });

    it('должен выбрасывать ошибку при превышении контекста', async () => {
      const largeMessages = Array(1000).fill({ role: 'user', content: 'A'.repeat(300) });
      await expect(sendMessage(mockBookId, largeMessages)).rejects.toThrow();
    });
  });

  describe('getBookById', () => {
    const mockBookId = '550e8400-e29b-41d4-a716-446655440001';

    it('должен возвращать книгу по ID (MOCK)', async () => {
      const response = await getBookById(mockBookId);
      expect(response.data).toBeDefined();
      expect(response.data.id).toBe(mockBookId);
    });

    it('должен возвращать ошибку при несуществующем ID', async () => {
      await expect(getBookById('invalid-id')).rejects.toThrow();
    });
  });
});