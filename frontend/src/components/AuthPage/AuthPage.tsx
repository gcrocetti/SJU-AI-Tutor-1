import { useState } from 'react';
import LoginForm from '../LoginForm/LoginForm';
import SignupForm from '../SignupForm/SignupForm';
import useDocumentTitle from '../../hooks/useDocumentTitle';
import './AuthPage.css';

interface AuthPageProps {
  onAuthSuccess?: () => void;
}

const AuthPage = ({ onAuthSuccess }: AuthPageProps) => {
  const [isLogin, setIsLogin] = useState(true);
  
  // Set the document title based on whether it's login or signup
  useDocumentTitle(isLogin ? 'CIRO Login' : 'Register');
  
  const handleSwitchMode = () => {
    setIsLogin(!isLogin);
  };
  
  const handleSuccess = () => {
    if (onAuthSuccess) {
      onAuthSuccess();
    }
  };
  
  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-sidebar">
          <div className="auth-logo">
            <img src="/images/SJUCrest.svg" alt="St. John's University" />
          </div>
          <div className="auth-welcome">
            <h1>Welcome to CIRO</h1>
            <p>Your personalized learning assistant for academic success</p>
          </div>
        </div>
        
        <div className="auth-content">
          {isLogin ? (
            <LoginForm 
              onSuccess={handleSuccess} 
              onSignupClick={handleSwitchMode} 
            />
          ) : (
            <SignupForm 
              onSuccess={handleSuccess} 
              onLoginClick={handleSwitchMode} 
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthPage;