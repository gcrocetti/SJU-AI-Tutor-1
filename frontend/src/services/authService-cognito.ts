// This file contains the AWS Cognito implementation of the authentication service
// To use it, rename this file to authService.ts after installing aws-amplify
// This implementation maintains the same interface as the original authService

import { Auth } from 'aws-amplify';
import { ApiResponse } from '../types/api';
import { SignupFormData, SigninFormData, AuthResponse, UserProfile } from '../types/auth';

/**
 * AuthService
 * 
 * A service for handling authentication-related API requests, including
 * sign up, sign in, and user profile management.
 * 
 * This version uses AWS Cognito for authentication.
 */
export class AuthService {
  /**
   * Register a new user
   * 
   * @param userData - User registration data
   * @returns Promise resolving to authentication response
   */
  async signup(userData: SignupFormData): Promise<ApiResponse<AuthResponse>> {
    try {
      console.log('Signing up user with Cognito:', userData.schoolEmail);
      
      // Sign up with Cognito
      const result = await Auth.signUp({
        username: userData.schoolEmail,
        password: userData.password,
        attributes: {
          email: userData.schoolEmail,
          given_name: userData.firstName,
          family_name: userData.lastName,
        }
      });
      
      if (result.user) {
        // After signing up, sign in to get the tokens
        const user = await Auth.signIn(userData.schoolEmail, userData.password);
        
        // Get user session and token
        const userSession = await Auth.currentSession();
        const token = userSession.getIdToken().getJwtToken();
        
        // Store token
        localStorage.setItem('authToken', token);
        
        // Create user profile
        const userProfile: UserProfile = {
          sub: result.userSub,
          schoolEmail: userData.schoolEmail,
          firstName: userData.firstName,
          lastName: userData.lastName,
          createdAt: new Date().toISOString()
        };
        
        // Save user profile
        this.saveUserProfile(userProfile);
        
        return {
          success: true,
          data: {
            success: true,
            token: token,
            user: userProfile
          }
        };
      }
      
      return {
        success: false,
        error: {
          code: 'SIGNUP_FAILED',
          message: 'Failed to create user account'
        }
      };
    } catch (error) {
      console.error('Signup error:', error);
      
      // Handle common Cognito errors
      if (error.code === 'UsernameExistsException') {
        return {
          success: false,
          error: {
            code: 'USERNAME_EXISTS',
            message: 'An account with this email already exists. Please sign in instead.'
          }
        };
      }
      
      return {
        success: false,
        error: {
          code: error.code || 'REQUEST_FAILED',
          message: error.message || 'Signup request failed'
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
      console.log('Signing in user with Cognito:', credentials.schoolEmail);
      
      // Sign in with Cognito
      const user = await Auth.signIn(credentials.schoolEmail, credentials.password);
      
      if (user) {
        // Get the user session and token
        const userSession = await Auth.currentSession();
        const token = userSession.getIdToken().getJwtToken();
        
        // Store token in localStorage for persistence
        localStorage.setItem('authToken', token);
        
        // Create user profile from Cognito attributes
        const userProfile: UserProfile = {
          sub: user.attributes.sub,
          schoolEmail: user.attributes.email,
          firstName: user.attributes.given_name,
          lastName: user.attributes.family_name,
          createdAt: user.attributes.created_at || new Date().toISOString()
        };
        
        // Save user profile to localStorage
        this.saveUserProfile(userProfile);
        
        return {
          success: true,
          data: {
            success: true,
            token: token,
            user: userProfile
          }
        };
      }
      
      return {
        success: false,
        error: {
          code: 'SIGNIN_FAILED',
          message: 'Failed to sign in'
        }
      };
    } catch (error) {
      console.error('Signin error:', error);
      
      // Handle specific Cognito errors
      if (error.code === 'UserNotFoundException') {
        return {
          success: false,
          error: {
            code: '404',
            message: 'User does not exist. Please sign up first.'
          }
        };
      } else if (error.code === 'NotAuthorizedException') {
        return {
          success: false,
          error: {
            code: '401',
            message: 'Invalid credentials. Please check your username and password.'
          }
        };
      } else if (error.code === 'UserNotConfirmedException') {
        return {
          success: false,
          error: {
            code: 'NOT_CONFIRMED',
            message: 'Please check your email and confirm your account before signing in.'
          }
        };
      }
      
      return {
        success: false,
        error: {
          code: error.code || 'REQUEST_FAILED',
          message: error.message || 'Signin request failed'
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
      // Sign out from Cognito
      await Auth.signOut();
      
      // Clear local storage items
      localStorage.removeItem('authToken');
      localStorage.removeItem('userProfile');
      localStorage.removeItem('lastPath');
      localStorage.removeItem('chatMessages');
      localStorage.removeItem('chatSessionId');
      
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
   * Save the user profile to localStorage
   * 
   * @param user - User profile to save
   */
  saveUserProfile(user: UserProfile): void {
    localStorage.setItem('userProfile', JSON.stringify(user));
  }
  
  /**
   * Get the current user profile
   * 
   * @returns The user profile, or null if not available
   */
  getUserProfile(): UserProfile | null {
    const profileJson = localStorage.getItem('userProfile');
    if (!profileJson) return null;
    
    try {
      return JSON.parse(profileJson) as UserProfile;
    } catch (error) {
      console.error('Error parsing user profile:', error);
      return null;
    }
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
   * Refresh the authentication token
   * This is automatically handled by Amplify, but exposed here
   * for explicit refreshes if needed
   * 
   * @returns Promise resolving to a success indicator
   */
  async refreshToken(): Promise<boolean> {
    try {
      // Amplify Auth will automatically refresh tokens when needed
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();
      
      // Update token in localStorage
      localStorage.setItem('authToken', token);
      
      return true;
    } catch (error) {
      console.error('Error refreshing token:', error);
      return false;
    }
  }
  
  /**
   * Reset a user's password by sending a reset code
   * 
   * @param email - The user's email address
   * @returns Promise resolving to a success indicator
   */
  async forgotPassword(email: string): Promise<boolean> {
    try {
      await Auth.forgotPassword(email);
      return true;
    } catch (error) {
      console.error('Error initiating password reset:', error);
      return false;
    }
  }
  
  /**
   * Complete the password reset process with a confirmation code
   * 
   * @param email - The user's email address
   * @param code - The confirmation code sent to the user's email
   * @param newPassword - The new password
   * @returns Promise resolving to a success indicator
   */
  async resetPassword(email: string, code: string, newPassword: string): Promise<boolean> {
    try {
      await Auth.forgotPasswordSubmit(email, code, newPassword);
      return true;
    } catch (error) {
      console.error('Error completing password reset:', error);
      return false;
    }
  }
}

export const authService = new AuthService();
export default authService;