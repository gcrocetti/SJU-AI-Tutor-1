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
      
      // MOCK API CALL - In production, this would be a real fetch request
      console.log(`[MOCK API] GET request to ${url.toString()}`);
      
      /**
       * In the real implementation, this would be:
       * 
       * const response = await fetch(url.toString(), {
       *   method: 'GET',
       *   headers: {
       *     'Accept': 'application/json',
       *     'Authorization': `Bearer ${this.getAuthToken()}`
       *   }
       * });
       * 
       * const data = await response.json();
       * 
       * if (!response.ok) {
       *   return {
       *     success: false,
       *     error: {
       *       code: response.status.toString(),
       *       message: data.message || 'Unknown error occurred'
       *     }
       *   };
       * }
       * 
       * return {
       *   success: true,
       *   data: data as T
       * };
       */
      
      // Mock success response - this would be replaced with actual API logic
      return {
        success: true,
        data: {} as T
      };
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
      
      // MOCK API CALL - In production, this would be a real fetch request
      console.log(`[MOCK API] POST request to ${url}`, data);
      
      /**
       * In the real implementation, this would be:
       * 
       * const response = await fetch(url, {
       *   method: 'POST',
       *   headers: {
       *     'Content-Type': 'application/json',
       *     'Accept': 'application/json',
       *     'Authorization': `Bearer ${this.getAuthToken()}`
       *   },
       *   body: JSON.stringify(data)
       * });
       * 
       * const responseData = await response.json();
       * 
       * if (!response.ok) {
       *   return {
       *     success: false,
       *     error: {
       *       code: response.status.toString(),
       *       message: responseData.message || 'Unknown error occurred'
       *     }
       *   };
       * }
       * 
       * return {
       *   success: true,
       *   data: responseData as T
       * };
       */
      
      // Mock success response - this would be replaced with actual API logic
      return {
        success: true,
        data: {} as T
      };
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