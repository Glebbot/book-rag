import { Routes, Route } from 'react-router-dom';
import BooksPage from './pages/BooksPage';
import ChatPage from './pages/ChatPage';
import Layout from './components/Layout';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<BooksPage />} />
        <Route path="chat/:bookId" element={<ChatPage />} />
      </Route>
    </Routes>
  );
}

export default App;