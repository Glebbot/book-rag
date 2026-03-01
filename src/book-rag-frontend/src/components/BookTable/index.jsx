import React, { useState, useRef } from 'react';
import { Table, Button, Space, Input, InputNumber, Select, Tag, Modal, Form, message, Popconfirm, Empty } from 'antd';
import { EditOutlined, DeleteOutlined, CommentOutlined, PlusOutlined, BookOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getBooks, updateBook, deleteBook, uploadBook } from '../../api/books';

const { Search } = Input;
const { Option } = Select;

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
  const fileInputRef = useRef(null);

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const response = await getBooks();
      let booksData;
      if (response?.data?.books && Array.isArray(response.data.books)) {
        booksData = response.data.books;
      } else if (Array.isArray(response?.data)) {
        booksData = response.data;
      } else {
        booksData = [];
      }
      setBooks(booksData);
    } catch (error) {
      message.error('Ошибка загрузки книг: ' + (error.response?.data?.userMessage || error.message));
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchBooks();
  }, []);

  const handleUpload = async (file) => {
    if (!file?.name?.endsWith('.pdf')) {
      message.error('Пожалуйста, загрузите файл в формате PDF');
      return false;
    }

    setUploading(true);
    try {
      await uploadBook(file);
      message.success('Книга успешно загружена');
      await fetchBooks();
      setIsModalVisible(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      message.error('Ошибка загрузки: ' + (error.response?.data?.userMessage || error.message));
    } finally {
      setUploading(false);
    }
    return false;
  };

  const handleEdit = (record) => {
    setEditingBook(record);
    form.setFieldsValue(record);
    setIsModalVisible(true);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();

      const changes = {};
      if (values.name !== editingBook?.name) changes.name = values.name;
      if (values.year !== editingBook?.year) changes.year = values.year;
      if (values.author !== editingBook?.author) changes.author = values.author;
      if (JSON.stringify(values.genres) !== JSON.stringify(editingBook?.genres)) {
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

  const handleDelete = async (bookId) => {
    try {
      await deleteBook(bookId);
      message.success('Книга удалена');
      await fetchBooks();
    } catch (error) {
      message.error('Ошибка удаления: ' + (error.response?.data?.userMessage || error.message));
    }
  };

  const handleChat = (bookId, bookName) => {
    navigate(`/chat/${bookId}`, { state: { bookName } });
};

  const safeBooks = Array.isArray(books) ? books : [];

  const filteredBooks = safeBooks.filter((book) => {
    const matchSearch = !filters.search ||
      (book?.name && book.name.toLowerCase().includes(filters.search.toLowerCase())) ||
      (book?.author && book.author.toLowerCase().includes(filters.search.toLowerCase()));
    const matchYear = !filters.year || book?.year === filters.year;
    const matchGenres = !filters.genres?.length ||
      (book?.genres && filters.genres.some((g) => book.genres.includes(g)));
    const matchAuthor = !filters.author ||
      (book?.author && book.author.toLowerCase().includes(filters.author.toLowerCase()));

    return matchSearch && matchYear && matchGenres && matchAuthor;
  });

  const uniqueAuthors = [...new Set(safeBooks.map((b) => b?.author).filter(Boolean))];
  const uniqueYears = [...new Set(safeBooks.map((b) => b?.year).filter(Boolean))].sort((a, b) => b - a);

  const emptyTableText = () => {
    if (loading) return null;

    const hasActiveFilters = filters.search || filters.year || filters.genres?.length || filters.author;

    if (hasActiveFilters && filteredBooks.length === 0) {
      return (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="Ничего не найдено по заданным фильтрам"
        >
          <Button type="primary" onClick={() => setFilters({ search: '', year: null, genres: [], author: '' })}>
            Сбросить фильтры
          </Button>
        </Empty>
      );
    }

    if (safeBooks.length === 0) {
      return (
        <Empty
          image={<BookOutlined style={{ fontSize: 48, color: '#ccc' }} />}
          description={
            <div>
              <p style={{ margin: 0, color: '#666' }}>В картотеке пока нет книг</p>
              <p style={{ margin: '8px 0 0 0', fontSize: 12, color: '#999' }}>
                Нажмите «Добавить книгу», чтобы загрузить первую
              </p>
            </div>
          }
        >
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
        </Empty>
      );
    }

    return null;
  };

  const columns = [
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => (a?.name || '').localeCompare(b?.name || ''),
      render: (text) => text || '—',
    },
    {
      title: 'Автор',
      dataIndex: 'author',
      key: 'author',
      filters: uniqueAuthors.map((a) => ({ text: a, value: a })),
      onFilter: (value, record) => record?.author === value,
      render: (text) => text || '—',
    },
    {
      title: 'Год',
      dataIndex: 'year',
      key: 'year',
      sorter: (a, b) => (a?.year || 0) - (b?.year || 0),
      filters: uniqueYears.map((y) => ({ text: String(y), value: y })),
      onFilter: (value, record) => record?.year === value,
      render: (text) => text || '—',
    },
    {
      title: 'Жанры',
      dataIndex: 'genres',
      key: 'genres',
      render: (genres) => {
        if (!genres || genres.length === 0) return '—';
        return (
          <Space wrap>
            {genres.map((genre) => (
              <Tag key={genre} color="blue">{genre}</Tag>
            ))}
          </Space>
        );
      },
      filters: AVAILABLE_GENRES.map((g) => ({ text: g, value: g })),
      onFilter: (value, record) => record?.genres?.includes(value),
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 280,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            icon={<CommentOutlined />}
            onClick={() => handleChat(record?.id, record?.name)}
            size="small"
          >
            Чат
          </Button>
          <Button
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            Редактировать
          </Button>
          <Popconfirm
            title="Вы уверены, что хотите удалить эту книгу?"
            onConfirm={() => handleDelete(record?.id)}
            okText="Да"
            cancelText="Нет"
          >
            <Button danger icon={<DeleteOutlined />} size="small">
              Удалить
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <Search
          placeholder="Поиск по названию или автору"
          allowClear
          style={{ width: 300 }}
          onChange={(e) => setFilters({ ...filters, search: e.target.value || '' })}
        />
        <Select
          placeholder="Фильтр по жанру"
          mode="multiple"
          style={{ width: 200 }}
          onChange={(value) => setFilters({ ...filters, genres: value || [] })}
          allowClear
          value={filters.genres}
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

      <Table
        columns={columns}
        dataSource={filteredBooks}
        rowKey="id"
        loading={loading || uploading}
        pagination={{ pageSize: 10 }}
        locale={{
          emptyText: emptyTableText(),
        }}
      />

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
                <Button
                  key="upload"
                  type="primary"
                  loading={uploading}
                  onClick={() => fileInputRef.current?.click()}
                >
                  Загрузить PDF
                </Button>,
                <input
                  ref={fileInputRef}
                  id="file-upload"
                  type="file"
                  accept=".pdf"
                  style={{ display: 'none' }}
                  onChange={(e) => {
                    if (e.target.files?.[0]) {
                      handleUpload(e.target.files[0]);
                    }
                  }}
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
                { type: 'integer', min: 0, max: new Date().getFullYear(), message: 'Год должен быть от 0 до текущего' },
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                max={new Date().getFullYear()}
                placeholder="Введите год"
              />
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