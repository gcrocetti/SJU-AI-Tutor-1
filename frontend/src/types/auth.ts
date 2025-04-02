/**
 * Auth-related Types
 * 
 * This file contains types related to authentication, including
 * user profiles, login, and signup data structures.
 */

/**
 * User signup form data
 */
export interface SignupFormData {
  /** Unique identifier for the user */
  sub: string;
  /** User's password */
  password: string;
  /** User's school email address */
  schoolEmail: string;
  /** User's first name */
  firstName: string;
  /** User's last name */
  lastName: string;
}

/**
 * User signin form data
 */
export interface SigninFormData {
  /** Unique identifier for the user */
  sub: string;
  /** User's school email address */
  schoolEmail: string;
  /** User's password */
  password: string;
}

/**
 * User profile information
 */
export interface UserProfile {
  /** Unique identifier for the user */
  sub: string;
  /** User's school email address */
  schoolEmail: string;
  /** User's first name */
  firstName: string;
  /** User's last name */
  lastName: string;
  /** When the user was created */
  createdAt?: string;
  /** When the user was last updated */
  updatedAt?: string;
}

/**
 * Authentication response
 */
export interface AuthResponse {
  /** Whether the authentication was successful */
  success: boolean;
  /** Auth token (if successful) */
  token?: string;
  /** User profile information (if successful) */
  user?: UserProfile;
  /** Error message (if unsuccessful) */
  message?: string;
}