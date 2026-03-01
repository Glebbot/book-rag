import React, { useState, useEffect } from 'react';
import { Spin, Alert, Typography, Button } from 'antd';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import ChatWindow from '../components/ChatWindow';

const { Title } = Typography;

const ChatPage = () => {
  const { bookId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  // Получаем bookName из state навигации (передаётся при переходе из списка книг)
  const bookName = location.state?.bookName;

  const [loading, setLoading] = useState(!bookName);
  const [error, setError] = useState(null);

  // Опционально: если bookName не передан, можно показать ошибку или сделать фоллбэк
  useEffect(() => {
    if (!bookName) {
      // Если имя книги не передано — показываем ошибку
      // (можно раскомментировать fetch, если нужен фоллбэк на API)
      setError('Информация о книге не передана. Вернитесь к списку книг и попробуйте снова.');
      setLoading(false);

      // /* Фоллбэк-запрос, если очень нужен (раскомментируйте при необходимости):
      // const fetchBook = async () => {
      //   try {
      //     const response = await getBookById(bookId);
      //     setBookName(response.data.name);
      //   } catch (err) {
      //     setError('Не удалось загрузить информацию о книге');
      //     message.error('Ошибка загрузки книги');
      //   } finally {
      //     setLoading(false);
      //   }
      // };
      // fetchBook();
      // */
    } else {
      setLoading(false);
    }
  }, [bookName, bookId]);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: 'calc(100vh - 140px)'
      }}>
        <Spin size="large" tip="Загрузка..." />
      </div>
    );
  }

  if (error || !bookName) {
    return (
      <div style={{ padding: 40 }}>
        <Alert
          message="Ошибка"
          description={error || 'Книга не найдена'}
          type="error"
          showIcon
          action={
            <Button
              type="link"
              onClick={() => navigate('/')}
            >
              Вернуться к списку книг
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div style={{ width: '100%', maxWidth: '1200px', margin: '0 auto' }}>
      <ChatWindow bookId={bookId} bookName={bookName} />
    </div>
  );
};

export default ChatPage;