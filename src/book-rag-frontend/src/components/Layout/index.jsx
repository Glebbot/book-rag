import React from 'react';
import { Layout as AntLayout, Menu, Typography } from 'antd';
import { BookOutlined } from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';

const { Header, Content } = AntLayout;

const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <BookOutlined />,
      label: 'Книги',
    },
  ];

  return (
    <AntLayout style={{ minHeight: '100vh', width: '100%' }}>
      <Header style={{
        display: 'flex',
        alignItems: 'center',
        gap: 20,
        padding: '0 24px',
        width: '100%',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
        borderBottom: 'none',
      }}>
        <div style={{ color: 'white', fontSize: 20, fontWeight: 'bold' }}>
          📚 RAG Книги
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname.startsWith('/chat') ? '/' : location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{
            flex: 1,
            minWidth: 0,
            background: 'transparent',
            borderBottom: 'none',
          }}
        />
      </Header>
      <Content style={{
        padding: '0',
        background: '#fff',
        margin: 0,
        minHeight: 'calc(100vh - 64px)',
        width: '100%',
        overflow: 'auto',
      }}>
        <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
          <Outlet />
        </div>
      </Content>
    </AntLayout>
  );
};

export default Layout;