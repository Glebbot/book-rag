import React, { useState } from 'react';
import { Table, Button, Space, Input, Select, Tag, Modal, Form, message, Popconfirm } from 'antd';
import { EditOutlined, DeleteOutlined, CommentOutlined, PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getBooks, updateBook, deleteBook, uploadBook } from '../../api/books';

const { Search } = Input;
const { Option } = Select;

// Доступные жанры для фильтра
const AVAILABLE_GENRES = ['Роман', 'Исторический', 'Психологический', 'Фантастика', 'Драма', 'Новый'];

const BookTable = () => {
  const navigate = useNavigate();
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingBook, setEditingBook] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    year: null,
    genres: [],
    author: '',
  });
  const [form] = Form.useForm();

  // Загрузка списка книг
  const fetchBooks = async () => {
    setLoading(true);
    try {
      const response = await getBooks();
      setBooks(response.data);
    } catch (error) {
      message.error('Ошибка загрузки книг: ' + (error.response?.data?.userMessage || error.message));
    } finally {
      setLoading(false);
    }
  };

  // Первоначальная загрузка
  React.useEffect(() => {
    fetchBooks();
  }, []);

  // Обработка загрузки файла
  const handleUpload = async (file) => {
    if (!file.name.endsWith('.pdf')) {
      message.error('Пожалуйста, загрузите файл в формате PDF');
      return false;
    }

    setUploading(true);
    try {
      await uploadBook(file);
      message.success('Книга успешно загружена');
      await fetchBooks();
      setIsModalVisible(false);
    } catch (error) {
      message.error('Ошибка загрузки: ' + (error.response?.data?.userMessage || error.message));
    } finally {
      setUploading(false);
    }
    return false; // Предотвращаем стандартную загрузку
  };

  // Обработка редактирования
  const handleEdit = (record) => {
    setEditingBook(record);
    form.setFieldsValue(record);
    setIsModalVisible(true);
  };

  // Сохранение изменений
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      // Проверяем, что есть изменения
      const changes = {};
      if (values.name !== editingBook.name) changes.name = values.name;
      if (values.year !== editingBook.year) changes.year = values.year;
      if (values.author !== editingBook.author) changes.author = values.author;
      if (JSON.stringify(values.genres) !== JSON.stringify(editingBook.genres)) {
        changes.genres = values.genres;
      }

      if (Object.keys(changes).length === 0) {
        message.info('Нет изменений для сохранения');
        setIsModalVisible(false);
        return;
      }

      await updateBook(editingBook.id, changes);
      message.success('Книга обновлена');
      await fetchBooks();
      setIsModalVisible(false);
      setEditingBook(null);
    } catch (error) {
      if (error.response?.status === 304) {
        message.info('Нет изменений для сохранения');
      } else {
        message.error('Ошибка обновления: ' + (error.response?.data?.userMessage || error.message));
      }
    }
  };

  // Обработка удаления
  const handleDelete = async (bookId) => {
    try {
      await deleteBook(bookId);
      message.success('Книга удалена');
      await fetchBooks();
    } catch (error) {
      message.error('Ошибка удаления: ' + (error.response?.data?.userMessage || error.message));
    }
  };

  // Переход к чату
  const handleChat = (bookId) => {
    navigate(`/chat/${bookId}`);
  };

  // Фильтрация данных
  const filteredBooks = books.filter((book) => {
    const matchSearch = !filters.search || 
      book.name.toLowerCase().includes(filters.search.toLowerCase()) ||
      book.author?.toLowerCase().includes(filters.search.toLowerCase());
    const matchYear = !filters.year || book.year === filters.year;
    const matchGenres = !filters.genres.length || 
      filters.genres.some((g) => book.genres?.includes(g));
    const matchAuthor = !filters.author || 
      book.author?.toLowerCase().includes(filters.author.toLowerCase());
    
    return matchSearch && matchYear && matchGenres && matchAuthor;
  });

  // Уникальные авторы для фильтра
  const uniqueAuthors = [...new Set(books.map((b) => b.author).filter(Boolean))];

  // Уникальные годы для фильтра
  const uniqueYears = [...new Set(books.map((b) => b.year).filter(Boolean))].sort((a, b) => b - a);

  // Колонки таблицы
  const columns = [
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: 'Автор',
      dataIndex: 'author',
      key: 'author',
      filters: uniqueAuthors.map((a) => ({ text: a, value: a })),
      onFilter: (value, record) => record.author === value,
    },
    {
      title: 'Год',
      dataIndex: 'year',
      key: 'year',
      sorter: (a, b) => a.year - b.year,
      filters: uniqueYears.map((y) => ({ text: String(y), value: y })),
      onFilter: (value, record) => record.year === value,
    },
    {
      title: 'Жанры',
      dataIndex: 'genres',
      key: 'genres',
      render: (genres) => (
        <Space wrap>
          {genres?.map((genre) => (
            <Tag key={genre} color="blue">{genre}</Tag>
          ))}
        </Space>
      ),
      filters: AVAILABLE_GENRES.map((g) => ({ text: g, value: g })),
      onFilter: (value, record) => record.genres?.includes(value),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            icon={<CommentOutlined />}
            onClick={() => handleChat(record.id)}
          >
            Чат
          </Button>
          <Button
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Редактировать
          </Button>
          <Popconfirm
            title="Вы уверены, что хотите удалить эту книгу?"
            onConfirm={() => handleDelete(record.id)}
            okText="Да"
            cancelText="Нет"
          >
            <Button danger icon={<DeleteOutlined />}>
              Удалить
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      {/* Верхняя панель с фильтрами и кнопкой добавления */}
      <div style={{ marginBottom: 16, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <Search
          placeholder="Поиск по названию или автору"
          allowClear
          style={{ width: 300 }}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />
        <Select
          placeholder="Фильтр по жанру"
          mode="multiple"
          style={{ width: 200 }}
          onChange={(value) => setFilters({ ...filters, genres: value })}
          allowClear
        >
          {AVAILABLE_GENRES.map((genre) => (
            <Option key={genre} value={genre}>{genre}</Option>
          ))}
        </Select>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setEditingBook(null);
            form.resetFields();
            setIsModalVisible(true);
          }}
        >
          Добавить книгу
        </Button>
      </div>

      {/* Таблица книг */}
      <Table
        columns={columns}
        dataSource={filteredBooks}
        rowKey="id"
        loading={loading || uploading}
        pagination={{ pageSize: 10 }}
      />

      {/* Модальное окно для добавления/редактирования */}
      <Modal
        title={editingBook ? 'Редактировать книгу' : 'Добавить книгу'}
        open={isModalVisible}
        onOk={editingBook ? handleSave : undefined}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingBook(null);
          form.resetFields();
        }}
        confirmLoading={uploading}
        footer={
          editingBook
            ? undefined
            : [
                <Button key="cancel" onClick={() => setIsModalVisible(false)}>
                  Отмена
                </Button>,
                <label key="upload" htmlFor="file-upload">
                  <Button type="primary" loading={uploading} as="span">
                    Загрузить PDF
                  </Button>
                </label>,
                <input
                  id="file-upload"
                  type="file"
                  accept=".pdf"
                  style={{ display: 'none' }}
                  onChange={(e) => e.target.files[0] && handleUpload(e.target.files[0])}
                />,
              ]
        }
      >
        {editingBook ? (
          <Form form={form} layout="vertical">
            <Form.Item
              name="name"
              label="Название"
              rules={[{ required: true, message: 'Введите название' }]}
            >
              <Input maxLength={100} />
            </Form.Item>
            <Form.Item
              name="author"
              label="Автор"
              rules={[{ required: true, message: 'Введите автора' }]}
            >
              <Input maxLength={100} />
            </Form.Item>
            <Form.Item
              name="year"
              label="Год"
              rules={[
                { required: true, message: 'Введите год' },
                { type: 'number', min: 0, max: new Date().getFullYear(), message: 'Год должен быть от 0 до текущего' },
              ]}
            >
              <Input type="number" />
            </Form.Item>
            <Form.Item
              name="genres"
              label="Жанры"
              rules={[{ required: true, message: 'Выберите жанры' }]}
            >
              <Select mode="multiple" allowClear>
                {AVAILABLE_GENRES.map((genre) => (
                  <Option key={genre} value={genre}>{genre}</Option>
                ))}
              </Select>
            </Form.Item>
          </Form>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <p>Выберите PDF файл для загрузки</p>
            <p style={{ color: '#999', fontSize: '12px' }}>
              Файл будет обработан и добавлен в картотеку
            </p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BookTable;