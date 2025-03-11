import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChatViewPage from './components/ChatViewPage/ChatViewPage';
import DiagnosticViewPage from './components/DiagnosticViewPage/DiagnosticViewPage';
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
 * - Authentication routes
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
  return (
    <BrowserRouter>
      <div className="app-container">
        {/* Global header - present on all pages */}
        <header className="header">Ciro AI Tutor</header>
        
        {/* Main content area - houses all routes */}
        <div className="content-container">
          <Routes>
            {/* Homepage/Chat route */}
            <Route path="/" element={<ChatViewPage />} />
            
            {/* Diagnostics dashboard route */}
            <Route path="/diagnostics" element={<DiagnosticViewPage />} />
            
            {/* 
              TODO: Add additional routes:
              - Authentication routes (login, signup, forgot password)
              - User profile/settings
              - Error pages (404, 500, etc.)
              - Help/documentation pages
            */}
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;