import api from './axios';
import { config } from '../config';

// === МОК ДАННЫЕ ДЛЯ ЧАТА ===
const MOCK_CHAT_RESPONSES = [
  "Это интересный вопрос! Согласно тексту книги, данное событие описывается в третьей главе.",
  "Автор подробно раскрывает эту тему в контексте исторических событий того времени.",
  "В книге говорится, что главный герой столкнулся с подобной дилеммой во второй части произведения.",
  "Этот момент является ключевым для понимания основной идеи произведения.",
  "Согласно анализу текста, можно сделать вывод, что автор хотел подчеркнуть важность этого вопроса.",
];

// POST /search/book/<bookId>
export const sendMessage = async (bookId, messages) => {
  if (config.USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, config.MOCK_DELAY + Math.random() * 1000));
    
    // Имитация ошибки при слишком длинном контексте
    const totalLength = messages.reduce((sum, m) => sum + m.content.length, 0);
    if (totalLength > config.MAX_CHAT_LENGTH) {
      const error = new Error('Out of context');
      error.response = { 
        status: 413, 
        data: { 
          errorCode: 'OutOfContext', 
          userMessage: 'Превышен максимальный размер контекста (max 200000 tokens)' 
        } 
      };
      throw error;
    }
    
    // Имитация ответа ассистента
    const lastUserMessage = messages.filter(m => m.role === 'user').pop();
    const mockResponse = {
      role: 'assistant',
      content: MOCK_CHAT_RESPONSES[Math.floor(Math.random() * MOCK_CHAT_RESPONSES.length)] + 
               ` (ответ на: "${lastUserMessage?.content?.substring(0, 50)}...")`
    };
    
    return { 
      data: { 
        messages: [...messages, mockResponse] 
      }, 
      status: 200 
    };
  }
  
  return api.post(`/search/book/${bookId}`, { messages });
};

// GET /books/<bookId> - для получения информации о книге в чате
export const getBookById = async (bookId) => {
  if (config.USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, config.MOCK_DELAY));
    // Импортируем MOCK_BOOKS из books.js (в реальном проекте лучше вынести в отдельный файл)
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
    const book = MOCK_BOOKS.find(b => b.id === bookId);
    if (!book) {
      const error = new Error('Book not found');
      error.response = { status: 404, data: { errorCode: 'NotFound', userMessage: 'Книга не найдена' } };
      throw error;
    }
    return { data: book };
  }
  return api.get(`/books/${bookId}`);
};