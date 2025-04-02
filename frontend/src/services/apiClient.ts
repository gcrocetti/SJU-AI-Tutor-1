import { ApiResponse } from '../types/api';

/**
 * ApiClient
 * 
 * A base service for making HTTP requests to the backend API.
 * This class provides methods for GET and POST requests with proper
 * error handling and type safety. It's designed to be easily extensible
 * for future HTTP methods (PUT, DELETE, etc.) as needed.
 * 
 * Currently configured to use mock responses, but structured to facilitate
 * an easy transition to real API calls when the backend is implemented.
 * 
 * Usage example:
 * ```typescript
 * const response = await apiClient.get<UserProfile>('/api/user/profile');
 * if (response.success) {
 *   // Use response.data
 * } else {
 *   // Handle error: response.error.message
 * }
 * ```
 */

export class ApiClient {
  /** Base URL for all API requests */
  private baseUrl: string;
  
  /**
   * Creates a new ApiClient instance
   * 
   * @param baseUrl - Optional base URL override (default: from environment variables)
   */
  constructor(baseUrl: string = '') {
    // Use provided URL, or environment variable, or empty string (relative URLs)
    this.baseUrl = baseUrl || import.meta.env.VITE_API_BASE_URL || '';
  }

  /**
   * Make a GET request to the API
   * 
   * @param endpoint - API endpoint path (e.g., '/api/user/profile')
   * @param params - Optional query parameters
   * @returns Promise resolving to a typed ApiResponse
   * 
   * TODO: Implement actual API integration with:
   * - Authentication tokens
   * - Request/response interceptors
   * - Error handling with retry logic
   * - Request cancellation
   */
  async get<T>(endpoint: string, params?: Record<string, string>): Promise<ApiResponse<T>> {
    try {
      // Construct the full URL with query parameters
      const url = new URL(this.baseUrl + endpoint);
      
      if (params) {
        Object.keys(params).forEach(key => {
          url.searchParams.append(key, params[key]);
        });
      }
      
      console.log(`Making GET request to ${url.toString()}`);
      
      // Get auth token from localStorage
      const authToken = localStorage.getItem('authToken');
      
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          ...(authToken && { 'Authorization': `Bearer ${authToken}` })
        }
      });
      
      if (!response.ok) {
        // Handle unauthorized errors (expired token)
        if (response.status === 401) {
          // Clear the token if it's expired
          localStorage.removeItem('authToken');
        }
        
        let errorMsg = 'Unknown error occurred';
        try {
          const errorData = await response.json();
          errorMsg = errorData.message || errorMsg;
        } catch (e) {
          // If error response is not JSON, just use status text
          errorMsg = response.statusText;
        }
        
        return {
          success: false,
          error: {
            code: response.status.toString(),
            message: errorMsg
          }
        };
      }
      
      try {
        const data = await response.json();
        return {
          success: true,
          data: data as T
        };
      } catch (e) {
        return {
          success: false,
          error: {
            code: 'PARSE_ERROR',
            message: 'Failed to parse response'
          }
        };
      }
    } catch (error) {
      // Log the error for debugging
      console.error('API request failed', error);
      
      // Return a standardized error response
      return {
        success: false,
        error: {
          code: 'REQUEST_FAILED',
          message: error instanceof Error ? error.message : 'Unknown error occurred'
        }
      };
    }
  }

  /**
   * Make a POST request to the API
   * 
   * @param endpoint - API endpoint path (e.g., '/api/chat/messages')
   * @param data - Request payload (will be serialized as JSON)
   * @returns Promise resolving to a typed ApiResponse
   * 
   * TODO: Implement actual API integration with:
   * - Authentication tokens
   * - Content-Type handling
   * - File uploads
   * - Progress tracking for large payloads
   */
  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    try {
      // Construct the full URL
      const url = this.baseUrl + endpoint;
      
      console.log(`Making POST request to ${url}`, data);
      
      // Get auth token from localStorage
      const authToken = localStorage.getItem('authToken');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...(authToken && { 'Authorization': `Bearer ${authToken}` })
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        // Handle unauthorized errors (expired token)
        if (response.status === 401) {
          // Clear the token if it's expired
          localStorage.removeItem('authToken');
        }
        
        let errorMsg = 'Unknown error occurred';
        try {
          const errorData = await response.json();
          errorMsg = errorData.message || errorMsg;
        } catch (e) {
          // If error response is not JSON, just use status text
          errorMsg = response.statusText;
        }
        
        return {
          success: false,
          error: {
            code: response.status.toString(),
            message: errorMsg
          }
        };
      }
      
      try {
        const responseData = await response.json();
        return {
          success: true,
          data: responseData as T
        };
      } catch (e) {
        return {
          success: false,
          error: {
            code: 'PARSE_ERROR',
            message: 'Failed to parse response'
          }
        };
      }
    } catch (error) {
      // Log the error for debugging
      console.error('API request failed', error);
      
      // Return a standardized error response
      return {
        success: false,
        error: {
          code: 'REQUEST_FAILED',
          message: error instanceof Error ? error.message : 'Unknown error occurred'
        }
      };
    }
  }
}
export const apiClient = new ApiClient();
export default apiClient;