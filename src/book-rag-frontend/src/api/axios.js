import axios from 'axios';
import { config } from '../config';

const api = axios.create({
  baseURL: config.API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Логируем ошибки для отладки
    if (error.response?.data?.userMessage) {
      console.error('API Error:', error.response.data.userMessage);
    }
    return Promise.reject(error);
  }
);

export default api;