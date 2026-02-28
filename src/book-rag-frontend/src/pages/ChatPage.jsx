import React, { useState, useEffect } from 'react';
import { Spin, Alert, Typography } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import ChatWindow from '../components/ChatWindow';
import { getBookById } from '../api/search';
import { message } from 'antd';

const { Title } = Typography;

const ChatPage = () => {
  const { bookId } = useParams();
  const navigate = useNavigate();
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBook = async () => {
      setLoading(true);
      try {
        const response = await getBookById(bookId);
        setBook(response.data);
      } catch (err) {
        console.error('Error fetching book:', err);
        setError(err.response?.data?.userMessage || 'Не удалось загрузить информацию о книге');
        message.error('Ошибка загрузки книги');
      } finally {
        setLoading(false);
      }
    };

    fetchBook();
  }, [bookId]);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: 'calc(100vh - 140px)' 
      }}>
        <Spin size="large" tip="Загрузка книги..." />
      </div>
    );
  }

  if (error || !book) {
    return (
      <div style={{ padding: 40 }}>
        <Alert
          message="Ошибка"
          description={error || 'Книга не найдена'}
          type="error"
          showIcon
          action={
            <button 
              onClick={() => navigate('/')}
              style={{ 
                background: 'none', 
                border: 'none', 
                color: '#1890ff', 
                cursor: 'pointer' 
              }}
            >
              Вернуться к списку книг
            </button>
          }
        />
      </div>
    );
  }

  return (
    <div style={{ width: '100%', maxWidth: '1200px', margin: '0 auto' }}>
      <ChatWindow bookId={bookId} bookName={book.name} />
    </div>
  );
};

export default ChatPage;