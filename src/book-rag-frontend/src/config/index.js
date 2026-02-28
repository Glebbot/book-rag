// Единое место для всех настроек приложения
export const config = {
    // Флаг использования мока вместо реального бекенда
    USE_MOCK: true,
    
    // URL API бекенда
    API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    
    // Максимальная длина сообщения (для валидации на клиенте)
    MAX_MESSAGE_LENGTH: 2000,
    
    // Таймаут для имитации запросов (мс)
    MOCK_DELAY: 100,
    
    // Максимальное количество сообщений в истории (для UI)
    MAX_CHAT_HISTORY: 5,

    // Максимальнная суммарная длина сообщений в чате
    MAX_CHAT_LENGTH: 10000,
  };
  
  export default config;