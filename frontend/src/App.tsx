import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import ChatViewPage from './components/ChatViewPage/ChatViewPage';
import DiagnosticViewPage from './components/DiagnosticViewPage/DiagnosticViewPage';
import AuthPage from './components/AuthPage';
import authService from './services/authService';
import './App.css';

/**
 * App Component
 * 
 * The root component for the Ciro AI Tutor application. This component sets up
 * the routing system using React Router and provides the main application
 * structure, including the header and content area.
 * 
 * The application has two main views:
 * 1. Chat View ('/') - The primary interface for conversing with the AI tutor
 * 2. Diagnostics View ('/diagnostics') - A dashboard showing student progress and resources
 * 
 * Future enhancements may include:
 * - Authentication persistence across refreshes
 * - Settings pages
 * - Admin interfaces
 * - Error boundaries
 * 
 * @component
 * @example
 * return (
 *   <App />
 * )
 */
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // Check authentication status on app load
  useEffect(() => {
    const checkAuth = () => {
      const isLoggedIn = authService.isAuthenticated();
      setIsAuthenticated(isLoggedIn);
    };
    
    checkAuth();
    
    // Set up event listener for auth changes (like storage events)
    window.addEventListener('storage', checkAuth);
    
    return () => {
      window.removeEventListener('storage', checkAuth);
    };
  }, []);
  
  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
  };
  
  const handleLogout = () => {
    authService.signout();
    setIsAuthenticated(false);
  };

  return (
    <BrowserRouter>
      <div className="app-container">
        {/* Global header - present on all pages when authenticated */}
        {isAuthenticated && (
          <header className="header">
            <div className="header-left"></div>
            <div className="header-center">Ciro AI Tutor</div>
            <div className="header-right">
              <button className="logout-button" onClick={handleLogout}>
                Log Out
              </button>
            </div>
          </header>
        )}
        
        {/* Main content area - houses all routes */}
        <div className={`content-container ${!isAuthenticated ? 'full-height' : ''}`}>
          <Routes>
            {/* Auth routes - accessible when not authenticated */}
            <Route
              path="/login"
              element={isAuthenticated ? <Navigate to="/" /> : <AuthPage onAuthSuccess={handleAuthSuccess} />}
            />
            
            {/* Protected routes - redirect to login if not authenticated */}
            <Route
              path="/"
              element={isAuthenticated ? <ChatViewPage /> : <Navigate to="/login" />}
            />
            
            <Route
              path="/diagnostics"
              element={isAuthenticated ? <DiagnosticViewPage /> : <Navigate to="/login" />}
            />
            
            {/* Default redirect */}
            <Route path="*" element={<Navigate to={isAuthenticated ? "/" : "/login"} />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;