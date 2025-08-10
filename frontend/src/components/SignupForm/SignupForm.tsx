import { useState } from 'react';
import { SignupFormData } from '../../types/auth';
import authService from '../../services/authService';
import './SignupForm.css';

interface SignupFormProps {
  onSuccess?: () => void;
  onLoginClick?: () => void;
}

const SignupForm = ({ onSuccess, onLoginClick }: SignupFormProps) => {
  const [formData, setFormData] = useState<SignupFormData>({
    sub: '',
    password: '',
    schoolEmail: '',
    firstName: '',
    lastName: ''
  });
  
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (name === 'confirmPassword') {
      setConfirmPassword(value);
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };
  
  const validateForm = (): boolean => {
    // Password confirmation check
    if (formData.password !== confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    
    // Email domain validation (optional)
    if (!formData.schoolEmail.endsWith('.edu')) {
      setError('Please use a valid school email address (.edu)');
      return false;
    }
    
    // Password strength validation (optional)
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    
    return true;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await authService.signup(formData);
      
      if (response.success && response.data) {
        console.log('Signup successful:', response.data);
        if (onSuccess) onSuccess();
      } else {
        setError(response.error?.message || 'Signup failed');
      }
    } catch (err) {
      setError('An unexpected error occurred');
      console.error('Signup error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="signup-form-container">
      <h2>Create Account</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="firstName">First Name</label>
            <input
              type="text"
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="lastName">Last Name</label>
            <input
              type="text"
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              required
            />
          </div>
        </div>
        
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
            placeholder="your.email@school.edu"
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
            minLength={8}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={confirmPassword}
            onChange={handleChange}
            required
          />
        </div>
        
        <button type="submit" className="signup-button" disabled={loading}>
          {loading ? 'Creating Account...' : 'Sign Up'}
        </button>
      </form>
      
      <div className="signup-footer">
        <p>Already have an account? <button className="text-button" onClick={onLoginClick}>Log In</button></p>
      </div>
    </div>
  );
};

export default SignupForm;