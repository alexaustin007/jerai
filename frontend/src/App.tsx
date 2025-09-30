/**
 * Main App Component with Routing
 * Routes between Issue Tracker (Dashboard) and Shop
 */

import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Shop from './pages/Shop';

export default function App() {
  return (
    <Router>
      {/* Navigation Header */}
      <header style={{
        backgroundColor: '#1e293b',
        color: 'white',
        padding: '15px 30px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>
          🤖 Jerai - AI Bug Fixer
        </h1>
        <nav style={{ display: 'flex', gap: '20px' }}>
          <Link
            to="/"
            style={{
              color: 'white',
              textDecoration: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              backgroundColor: 'rgba(255,255,255,0.1)',
              transition: 'background-color 0.2s'
            }}
          >
            📋 Issue Tracker
          </Link>
          <Link
            to="/shop"
            style={{
              color: 'white',
              textDecoration: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              backgroundColor: 'rgba(255,255,255,0.1)',
              transition: 'background-color 0.2s'
            }}
          >
            🛒 Demo Shop
          </Link>
        </nav>
      </header>

      {/* Routes */}
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/shop" element={<Shop />} />
      </Routes>
    </Router>
  );
}