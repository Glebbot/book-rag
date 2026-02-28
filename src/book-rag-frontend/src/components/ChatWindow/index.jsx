import React, { useState, useRef, useEffect } from 'react';
import { 
  Input,
  Button,
  Typography,
  message,
  Alert,
  Space,
  Card,
  Avatar
} from 'antd';
import { SendOutlined, UserOutlined, ArrowLeftOutlined, RobotOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { sendMessage } from '../../api/search';
import { config } from '../../config';

const { Text } = Typography;
const { TextArea } = Input;

// Компонент анимации точек
const LoadingDots = () => {
  const [dots, setDots] = useState('.');

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => {
        if (prev.length >= 10) {
          return '.';
        }
        return prev + '.';
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{
      background: '#f0f2f5',
      borderRadius: '16px',
      padding: '12px 16px',
      boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
      display: 'inline-block',
    }}>
      <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#999' }}>
        {dots}
      </Text>
    </div>
  );
};

const ChatWindow = ({ bookId, bookName }) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Найдите функцию scrollToBottom и обновите:
const scrollToBottom = () => {
  if (messagesEndRef.current) {
    messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
  }
};

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Фокус на поле ввода при загрузке
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Очистка контекста при уходе со страницы
  useEffect(() => {
    return () => {
      console.log('Chat context cleared');
    };
  }, []);

  // Отправка сообщения
  const handleSend = async () => {
    if (!inputValue.trim()) {
      message.warning('Введите сообщение');
      return;
    }

    if (inputValue.length > config.MAX_MESSAGE_LENGTH) {
      message.error(`Сообщение слишком длинное (макс. ${config.MAX_MESSAGE_LENGTH} символов)`);
      return;
    }

    const userMessage = {
      role: 'user',
      content: inputValue.trim(),
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputValue('');
    setLoading(true);
    setError(null);

    try {
      const response = await sendMessage(bookId, newMessages);
      setMessages(response.data.messages);
    } catch (err) {
      console.error('Chat error:', err);

      if (err.response?.status === 413) {
        setError({
          type: 'context',
          message: err.response.data?.userMessage || 'Превышен максимальный размер контекста',
        });
        message.error('Превышен лимит контекста. Начните новый диалог.');
      } else if (err.response?.status === 404) {
        setError({
          type: 'notfound',
          message: err.response.data?.userMessage || 'Книга не найдена',
        });
        message.error('Книга не найдена');
      } else if (err.response?.status === 400) {
        setError({
          type: 'badrequest',
          message: err.response.data?.userMessage || 'Некорректный запрос',
        });
        message.error('Некорректный формат сообщения');
      } else {
        setError({
          type: 'unknown',
          message: err.response.data?.userMessage || 'Произошла ошибка при отправке сообщения',
        });
        message.error('Ошибка соединения');
      }

      setMessages(messages);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  // Обработка нажатия Enter
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Очистка истории чата
  const handleClearChat = () => {
    setMessages([]);
    setError(null);
    message.success('История чата очищена');
  };

  // Форматирование времени
  const formatTime = () => {
    return new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  };

  // Рендер сообщения
  const renderMessage = (msg, index) => {
    const isUser = msg.role === 'user';

    return (
      <div
        key={index}
        style={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          marginBottom: 12,
          padding: '0 16px',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center', // Центрирование по вертикали
            gap: 8,
            maxWidth: '70%',
            flexDirection: isUser ? 'row-reverse' : 'row',
          }}
        >
          {/* Аватар */}
          <Avatar
            size={36}
            style={{
              backgroundColor: isUser ? '#3390ec' : '#52c41a',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
            icon={isUser ? <UserOutlined /> : <RobotOutlined />}
          />

          {/* Сообщение */}
          <div
            style={{
              background: isUser ? '#3390ec' : '#f0f2f5',
              borderRadius: '16px',
              padding: '10px 14px',
              boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
              color: isUser ? '#ffffff' : '#000000',
              position: 'relative',
            }}
          >
            <Text style={{ fontSize: 15, lineHeight: 1.4, color: isUser ? '#ffffff' : '#000000' }}>
              {msg.content}
            </Text>
            <div
              style={{
                marginTop: 4,
                fontSize: 11,
                color: isUser ? 'rgba(255,255,255,0.7)' : '#999',
                textAlign: 'right',
              }}
            >
              {formatTime()}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Card
      style={{
        height: 'calc(100vh - 140px)',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 0,
        border: 'none',
        boxShadow: 'none',
        padding: 0,
        background: '#ffffff'
      }}
      title={
        <Space style={{ cursor: 'pointer' }} onClick={() => navigate('/')}>
          <Button
            type="text"
            icon={<ArrowLeftOutlined />}
            style={{ border: 'none', boxShadow: 'none' }}
          />
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: 16, fontWeight: 600 }}>{bookName}</span>
            <span style={{ fontSize: 13, color: '#999' }}>бот</span>
          </div>
        </Space>
      }
      extra={
        messages.length > 0 && (
          <Button
            size="small"
            onClick={handleClearChat}
            color="danger"
            variant="filled"
          >
            Очистить
          </Button>
        )
      }
      headStyle={{
        background: '#ffffff',
        borderBottom: '1px solid #e0e0e0',
        padding: '12px 16px',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}
      bodyStyle={{
        flex: 1,
        overflow: 'auto',
        padding: 0,
        display: 'flex',
        flexDirection: 'column',
        background: '#ffffff',
      }}
    >
      {/* Область сообщений */}
      <div style={{ flex: 1, overflow: 'auto', padding: '16px 0' }}>
        {messages.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            color: '#999',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 16,
          }}>
            <div
              style={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 36,
                color: 'white',
                boxShadow: '0 4px 12px rgba(82, 196, 26, 0.3)',
              }}
            >
              <RobotOutlined />
            </div>
            <div>
              <p style={{ fontSize: 18, fontWeight: 600, margin: 0, color: '#333' }}>{bookName}</p>
              <p style={{ fontSize: 14, margin: '8px 0 0 0', color: '#999' }}>
                Задайте вопрос по книге
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => renderMessage(msg, index))
        )}

        {/* Индикатор загрузки с точками */}
        {loading && (
          <div style={{
            textAlign: 'left',
            padding: '8px 16px',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}>
              <Avatar
                size={36}
                style={{ backgroundColor: '#52c41a' }}
                icon={<RobotOutlined />}
              />
              <LoadingDots />
            </div>
          </div>
        )}

        {/* Ошибка контекста */}
        {error?.type === 'context' && (
          <div style={{ padding: '0 16px', marginTop: 16 }}>
            <Alert
              message="Лимит контекста превышен"
              description={error.message}
              type="warning"
              showIcon
              action={
                <Button size="small" onClick={handleClearChat}>
                  Новый диалог
                </Button>
              }
            />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Область ввода - как в Telegram */}
      <div style={{
        background: '#ffffff',
        padding: '12px 16px',
        borderTop: '1px solid #e0e0e0',
        display: 'flex',
        alignItems: 'flex-end',
        gap: 12,
      }}>
        <TextArea
          ref={inputRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Написать сообщение..."
          rows={1}
          maxLength={config.MAX_MESSAGE_LENGTH}
          disabled={loading || error?.type === 'context'}
          style={{
            resize: 'none',
            border: 'none',
            boxShadow: 'none',
            background: '#f0f2f5',
            borderRadius: '20px',
            padding: '12px 16px',
            fontSize: 15,
            maxHeight: 120,
          }}
          autoSize={{ minRows: 1, maxRows: 4 }}
        />
        <Button
          type="primary"
          shape="circle"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={loading}
          disabled={!inputValue.trim() || loading || error?.type === 'context'}
          aria-label="Отправить"
          style={{
            width: 48,
            height: 48,
            background: '#3390ec',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        />
      </div>
    </Card>
  );
};

export default ChatWindow;