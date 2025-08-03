import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import ChatViewPage from './components/ChatViewPage/ChatViewPage';
import DiagnosticViewPage from './components/DiagnosticViewPage/DiagnosticViewPage';
import ChapterList from './components/ChapterList';
import ChapterQuiz from './components/ChapterQuiz';
import AuthPage from './components/AuthPage';
import SurveyPage from './components/SurveyPage';
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
  const [needsSurvey, setNeedsSurvey] = useState<boolean>(false);

  // Check authentication status and survey completion on app load
  useEffect(() => {
    const checkAuth = () => {
      const isLoggedIn = authService.isAuthenticated();
      setIsAuthenticated(isLoggedIn);
      
      // Check if user needs to complete the survey
      if (isLoggedIn) {
        const userProfile = authService.getUserProfile();
        const hasSurveyData = userProfile?.surveyResponses;
        setNeedsSurvey(!hasSurveyData);
      } else {
        setNeedsSurvey(false);
      }
    };
    
    checkAuth();
    
    // Set up event listener for auth changes (like storage events)
    window.addEventListener('storage', checkAuth);
    
    return () => {
      window.removeEventListener('storage', checkAuth);
    };
  }, []);
  
  const handleAuthSuccess = (isSignup: boolean = false) => {
    setIsAuthenticated(true);
    
    if (isSignup) {
      // Always show survey for new signups
      setNeedsSurvey(true);
    } else {
      // For login, only show survey if they haven't completed it
      const userProfile = authService.getUserProfile();
      const hasSurveyData = userProfile?.surveyResponses;
      setNeedsSurvey(!hasSurveyData);
    }
  };
  
  const handleSurveyComplete = () => {
    setNeedsSurvey(false);
  };
  
  const handleLogout = () => {
    authService.signout();
    setIsAuthenticated(false);
    setNeedsSurvey(false);
  };

  return (
    <BrowserRouter>
      <div className="app-container">
        {/* Global header - present on all pages when authenticated */}
        {isAuthenticated && (
          <header className="header">
            <div className="header-left"></div>
            <div className="header-center">CIRO AI Tutor</div>
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
              element={isAuthenticated ? (needsSurvey ? <Navigate to="/survey" /> : <Navigate to="/" />) : <AuthPage onAuthSuccess={handleAuthSuccess} />}
            />
            
            {/* Survey route - only accessible to authenticated users who haven't completed the survey */}
            <Route
              path="/survey"
              element={isAuthenticated ? (needsSurvey ? <SurveyPage onComplete={handleSurveyComplete} /> : <Navigate to="/" />) : <Navigate to="/login" />}
            />
            
            {/* Protected routes - redirect to survey if needed, otherwise to login if not authenticated */}
            <Route
              path="/"
              element={
                isAuthenticated 
                  ? (needsSurvey ? <Navigate to="/survey" /> : <ChatViewPage />) 
                  : <Navigate to="/login" />
              }
            />
            
            <Route
              path="/diagnostics"
              element={
                isAuthenticated 
                  ? (needsSurvey ? <Navigate to="/survey" /> : <DiagnosticViewPage />) 
                  : <Navigate to="/login" />
              }
            />
            
            <Route
              path="/diagnostics/chapters"
              element={
                isAuthenticated 
                  ? (needsSurvey ? <Navigate to="/survey" /> : <ChapterList />) 
                  : <Navigate to="/login" />
              }
            />
            
            <Route
              path="/diagnostics/quiz/:chapterId"
              element={
                isAuthenticated 
                  ? (needsSurvey ? <Navigate to="/survey" /> : <ChapterQuiz />) 
                  : <Navigate to="/login" />
              }
            />
            
            {/* Default redirect */}
            <Route path="*" element={<Navigate to={isAuthenticated ? (needsSurvey ? "/survey" : "/") : "/login"} />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;