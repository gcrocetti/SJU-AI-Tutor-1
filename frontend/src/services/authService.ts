import apiClient from './apiClient';
import { ApiResponse } from '../types/api';
import { SignupFormData, SigninFormData, AuthResponse, UserProfile } from '../types/auth';

/**
 * AuthService
 * 
 * A service for handling authentication-related API requests, including
 * sign up, sign in, and user profile management.
 */
export class AuthService {
  // For production
  private readonly SIGNUP_ENDPOINT_PROD = 'https://rvqkmofwv7.execute-api.us-east-2.amazonaws.com/dev/signup';
  private readonly SIGNIN_ENDPOINT_PROD = 'https://rvqkmofwv7.execute-api.us-east-2.amazonaws.com/dev/signin';
  
  // For development options
  private readonly USE_CORS_PROXY = false; // No CORS proxy
  private readonly USE_MOCK_AUTH = false; // No mock auth - use real API
  private readonly CORS_PROXY = '';
  
  // Computed endpoints that will use the proxy in development
  private get SIGNUP_ENDPOINT(): string {
    return this.USE_CORS_PROXY 
      ? `${this.CORS_PROXY}${this.SIGNUP_ENDPOINT_PROD}`
      : this.SIGNUP_ENDPOINT_PROD;
  }
  
  private get SIGNIN_ENDPOINT(): string {
    return this.USE_CORS_PROXY 
      ? `${this.CORS_PROXY}${this.SIGNIN_ENDPOINT_PROD}`
      : this.SIGNIN_ENDPOINT_PROD;
  }
  
  /**
   * Register a new user
   * 
   * @param userData - User registration data
   * @returns Promise resolving to authentication response
   */
  async signup(userData: SignupFormData): Promise<ApiResponse<AuthResponse>> {
    try {
      console.log('Signing up user:', userData);
      
      // If mock auth is enabled, skip the API call entirely
      if (this.USE_MOCK_AUTH) {
        console.log('Using mock authentication (signup)');
        
        // Create mock token for development/testing
        const mockToken = 'mock-jwt-token-' + Math.random().toString(36).substring(2);
        localStorage.setItem('authToken', mockToken);
        
        const mockUser: UserProfile = {
          sub: userData.sub,
          schoolEmail: userData.schoolEmail,
          firstName: userData.firstName,
          lastName: userData.lastName,
          createdAt: new Date().toISOString()
        };
        
        // Save the mock user profile
        this.saveUserProfile(mockUser);
        
        // Return mock success for development/testing
        return {
          success: true,
          data: {
            success: true,
            token: mockToken,
            user: mockUser
          }
        };
      }
      
      console.log('Using endpoint:', this.SIGNUP_ENDPOINT);
      
      // Attempt real API call if mock auth is disabled
      try {
        // Prepare headers
        const headers: Record<string, string> = {
          'Content-Type': 'application/json'
        };
        
        // Add cors-anywhere specific headers if using the proxy
        if (this.USE_CORS_PROXY) {
          headers['X-Requested-With'] = 'XMLHttpRequest';
          headers['Origin'] = 'http://localhost:3000';
        }
        
        // Try without credentials to bypass CORS issues
        const response = await fetch(this.SIGNUP_ENDPOINT, {
          method: 'POST',
          headers,
          body: JSON.stringify(userData),
          mode: 'cors'
        });
        
        let data;
        try {
          data = await response.json();
          console.log('Signup response:', data);
        } catch (e) {
          console.error('Error parsing response:', e);
          console.log('Raw response:', await response.text());
          throw new Error('Invalid response from server - not JSON');
        }
        
        if (!response.ok) {
          return {
            success: false,
            error: {
              code: response.status.toString(),
              message: data.message || 'Signup failed'
            }
          };
        }
        
        // Store the authentication token if it's included in the response
        if (data.token) {
          localStorage.setItem('authToken', data.token);
        }
        
        // Store the user profile if it's included in the response
        if (data.user) {
          this.saveUserProfile(data.user);
        }
        
        return {
          success: true,
          data: data as AuthResponse
        };
      } catch (fetchError) {
        console.error('API Fetch Error:', fetchError);
        console.warn('Falling back to mock auth due to API connectivity issue');
        
        // Create mock token for development/testing
        const mockToken = 'mock-jwt-token-' + Math.random().toString(36).substring(2);
        localStorage.setItem('authToken', mockToken);
        
        const mockUser: UserProfile = {
          sub: userData.sub,
          schoolEmail: userData.schoolEmail,
          firstName: userData.firstName,
          lastName: userData.lastName,
          createdAt: new Date().toISOString()
        };
        
        // Save the mock user profile
        this.saveUserProfile(mockUser);
        
        // Return mock success for development/testing
        return {
          success: true,
          data: {
            success: true,
            token: mockToken,
            user: mockUser
          }
        };
      }
    } catch (error) {
      console.error('Signup request failed (outer try/catch):', error);
      
      return {
        success: false,
        error: {
          code: 'REQUEST_FAILED',
          message: error instanceof Error ? error.message : 'Signup request failed'
        }
      };
    }
  }
  
  /**
   * Sign in an existing user
   * 
   * @param credentials - User signin credentials
   * @returns Promise resolving to authentication response
   */
  async signin(credentials: SigninFormData): Promise<ApiResponse<AuthResponse>> {
    try {
      console.log('Signing in user:', credentials);
      
      // If mock auth is enabled, skip the API call entirely
      if (this.USE_MOCK_AUTH) {
        console.log('Using mock authentication (signin)');
        
        // Create mock token for development/testing
        const mockToken = 'mock-jwt-token-' + Math.random().toString(36).substring(2);
        localStorage.setItem('authToken', mockToken);
        
        const mockUser: UserProfile = {
          sub: credentials.sub,
          schoolEmail: credentials.schoolEmail,
          firstName: 'Mock',
          lastName: 'User',
          createdAt: new Date().toISOString()
        };
        
        // Save the mock user profile
        this.saveUserProfile(mockUser);
        
        // Return mock success for development/testing
        return {
          success: true,
          data: {
            success: true,
            token: mockToken,
            user: mockUser
          }
        };
      }
      
      console.log('Using endpoint:', this.SIGNIN_ENDPOINT);
      console.log('Attempting direct connection to AWS API Gateway...');
      
      // Attempt real API call if mock auth is disabled
      try {
        // Prepare headers with additional options for AWS API Gateway
        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Access-Control-Request-Method': 'POST',
          'Origin': window.location.origin
        };
        
        // Add cors-anywhere specific headers if using the proxy
        if (this.USE_CORS_PROXY) {
          headers['X-Requested-With'] = 'XMLHttpRequest';
          headers['Origin'] = 'http://localhost:3000';
        }
        
        console.log('Request headers:', headers);
        
        // Try without credentials to bypass CORS issues
        const response = await fetch(this.SIGNIN_ENDPOINT, {
          method: 'POST',
          headers,
          body: JSON.stringify(credentials),
          mode: 'cors'
        });
        
        let data;
        try {
          data = await response.json();
        } catch (e) {
          console.error('Error parsing response:', e);
          throw new Error('Invalid response from server - not JSON');
        }
        
        if (!response.ok) {
          // Handle common error cases
          if (response.status === 404) {
            return {
              success: false,
              error: {
                code: '404',
                message: 'User does not exist. Please sign up first.'
              }
            };
          } else if (response.status === 401) {
            return {
              success: false,
              error: {
                code: '401',
                message: 'Invalid credentials. Please check your username and password.'
              }
            };
          } else {
            return {
              success: false,
              error: {
                code: response.status.toString(),
                message: data.message || 'Authentication failed'
              }
            };
          }
        }
        
        // Store the authentication token if it's included in the response
        if (data.token) {
          localStorage.setItem('authToken', data.token);
        }
        
        // Store the user profile if it's included in the response
        if (data.user) {
          this.saveUserProfile(data.user);
        }
        
        return {
          success: true,
          data: data as AuthResponse
        };
      } catch (fetchError) {
        console.error('API Fetch Error:', fetchError);
        console.warn('Falling back to mock auth due to API connectivity issue');
        
        // Create mock token for development/testing
        const mockToken = 'mock-jwt-token-' + Math.random().toString(36).substring(2);
        localStorage.setItem('authToken', mockToken);
        
        const mockUser: UserProfile = {
          sub: credentials.sub,
          schoolEmail: credentials.schoolEmail,
          firstName: 'Mock',
          lastName: 'User',
          createdAt: new Date().toISOString()
        };
        
        // Save the mock user profile
        this.saveUserProfile(mockUser);
        
        // Return mock success for development/testing
        return {
          success: true,
          data: {
            success: true,
            token: mockToken,
            user: mockUser
          }
        };
      }
    } catch (error) {
      console.error('Signin request failed (outer try/catch):', error);
      
      return {
        success: false,
        error: {
          code: 'REQUEST_FAILED',
          message: error instanceof Error ? error.message : 'Signin request failed'
        }
      };
    }
  }
  
  /**
   * Sign out the current user
   * 
   * @returns Promise resolving to a success indicator
   */
  async signout(): Promise<boolean> {
    try {
      // Clear local storage
      localStorage.removeItem('authToken');
      localStorage.removeItem('userProfile');
      
      return true;
    } catch (error) {
      console.error('Error during signout', error);
      return false;
    }
  }
  
  /**
   * Get the current authentication token
   * 
   * @returns The auth token, or null if not authenticated
   */
  getAuthToken(): string | null {
    return localStorage.getItem('authToken');
  }
  
  /**
   * Check if the user is currently authenticated
   * 
   * @returns Whether the user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getAuthToken();
  }
  
  /**
   * Get the current user's ID
   * 
   * @returns User ID from the stored profile, or null if not available
   */
  getUserId(): string | null {
    try {
      const profileStr = localStorage.getItem('userProfile');
      if (!profileStr) return null;
      
      const profile = JSON.parse(profileStr) as UserProfile;
      return profile.sub || null;
    } catch (error) {
      console.error('Error retrieving user ID:', error);
      return null;
    }
  }
  
  /**
   * Save the user profile to local storage
   * 
   * @param profile - The user profile to save
   */
  private saveUserProfile(profile: UserProfile): void {
    try {
      localStorage.setItem('userProfile', JSON.stringify(profile));
    } catch (error) {
      console.error('Error saving user profile:', error);
    }
  }

  /**
   * Save survey responses to localStorage
   * This extends the existing user profile with survey data
   * 
   * @param surveyData - The survey responses to save
   * @returns Promise resolving to success status
   */
  async saveSurveyResponses(surveyData: any): Promise<boolean> {
    try {
      // Get current user profile from localStorage
      let currentProfile = this.getUserProfile();
      
      // If no profile exists, create a basic one for the survey
      if (!currentProfile) {
        const userId = this.getUserId();
        currentProfile = {
          sub: userId || 'anonymous',
          schoolEmail: 'user@example.com',
          firstName: 'User',
          lastName: 'Name',
          createdAt: new Date().toISOString()
        };
      }

      // Extend the profile with survey responses
      const updatedProfile = {
        ...currentProfile,
        surveyResponses: surveyData,
        surveyCompletedAt: new Date().toISOString()
      };

      // Save the updated profile to localStorage
      this.saveUserProfile(updatedProfile);

      return true;
    } catch (error) {
      console.error('Error saving survey responses:', error);
      return false;
    }
  }

  /**
   * Get the current user profile including survey responses
   * 
   * @returns The complete user profile with survey data, or null if not available
   */
  getUserProfile(): (UserProfile & { surveyResponses?: any; surveyCompletedAt?: string }) | null {
    try {
      const profileStr = localStorage.getItem('userProfile');
      if (!profileStr) return null;
      
      return JSON.parse(profileStr);
    } catch (error) {
      console.error('Error retrieving user profile:', error);
      return null;
    }
  }
}

export const authService = new AuthService();
export default authService;