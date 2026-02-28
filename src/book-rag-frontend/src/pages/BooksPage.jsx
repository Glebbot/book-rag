import React from 'react';
import { Typography } from 'antd';
import BookTable from '../components/BookTable';

const { Title } = Typography;

const BooksPage = () => {
  return (
    <div style={{ width: '100%', maxWidth: '1400px', margin: '0 auto' }}>
      <Title level={2} style={{ marginBottom: 24 }}>Картотека книг</Title>
      <BookTable />
    </div>
  );
};

export default BooksPage;