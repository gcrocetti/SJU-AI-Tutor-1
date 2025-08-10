import { useState } from 'react';
import { SigninFormData } from '../../types/auth';
import authService from '../../services/authService';
import './LoginForm.css';

interface LoginFormProps {
  onSuccess?: () => void;
  onSignupClick?: () => void;
}

const LoginForm = ({ onSuccess, onSignupClick }: LoginFormProps) => {
  const [formData, setFormData] = useState<SigninFormData>({
    sub: '',
    schoolEmail: '',
    password: ''
  });
  
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      const response = await authService.signin(formData);
      
      if (response.success && response.data) {
        console.log('Login successful:', response.data);

        // Store the user email in the session
        sessionStorage.setItem('userEmail', formData.schoolEmail);

        if (onSuccess) onSuccess();
      } else {
        setError(response.error?.message || 'Login failed');
        
        // If user doesn't exist, suggest signup
        if (response.error?.code === '404') {
          // Highlight the signup button or add additional UI indicator
          const signupButton = document.querySelector('.text-button');
          if (signupButton) {
            signupButton.classList.add('highlight-signup');
          }
        }
      }
    } catch (err) {
      setError('An unexpected error occurred');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="login-form-container">
      <h2>Log In</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="sub">Username</label>
          <input
            type="text"
            id="sub"
            name="sub"
            value={formData.sub}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="schoolEmail">School Email</label>
          <input
            type="email"
            id="schoolEmail"
            name="schoolEmail"
            value={formData.schoolEmail}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        
        <button type="submit" className="login-button" disabled={loading}>
          {loading ? 'Logging in...' : 'Log In'}
        </button>
      </form>
      
      <div className="login-footer">
        <p>Don't have an account? <button className="text-button" onClick={onSignupClick}>Sign Up</button></p>
      </div>
    </div>
  );
};

export default LoginForm;