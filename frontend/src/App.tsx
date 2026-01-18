/**
 * Main App component with routing
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ArticleListPage } from './pages/ArticleListPage';
import { ArticleDetailPage } from './pages/ArticleDetailPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ArticleListPage />} />
        <Route path="/articles/:id" element={<ArticleDetailPage />} />
      </Routes>
    </Router>
  );
}

export default App;
