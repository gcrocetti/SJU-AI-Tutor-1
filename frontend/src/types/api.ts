/**
 * API-related Types
 * 
 * This file contains types related to API communication, including
 * response structures, endpoints, and service-specific types for
 * OpenAI, Pinecone, and other external services.
 */

/**
 * Common API response structure
 * 
 * Generic wrapper for all API responses to ensure consistent
 * handling of success/error states.
 */
export interface ApiResponse<T> {
  /** Whether the request was successful */
  success: boolean;
  /** Response data (only present if success is true) */
  data?: T;
  /** Error information (only present if success is false) */
  error?: {
    /** Error code (e.g., "NOT_FOUND", "UNAUTHORIZED") */
    code: string;
    /** Human-readable error message */
    message: string;
  };
}

/**
 * API endpoints
 * 
 * Enum of all available API endpoints for the application.
 * Using an enum ensures consistency and prevents typos.
 */
export enum ApiEndpoint {
  /** Chat API endpoint for message exchange */
  CHAT = '/api/chat',
  /** User profile endpoint */
  USER_PROFILE = '/api/user',
  /** Diagnostics data endpoint */
  DIAGNOSTICS = '/api/diagnostics',
  /** Educational resources endpoint */
  RESOURCES = '/api/resources',
  /** Progress tracking endpoint */
  PROGRESS = '/api/progress',
}

/**
 * OpenAI API message format
 * 
 * Represents a single message in the OpenAI chat completion format.
 */
export interface OpenAIMessage {
  /** Message role (system, user, or assistant) */
  role: 'system' | 'user' | 'assistant';
  /** Message content */
  content: string;
}

/**
 * OpenAI API completion request
 * 
 * Parameters for requesting a completion from OpenAI's API.
 */
export interface OpenAICompletionRequest {
  /** Array of messages in the conversation */
  messages: OpenAIMessage[];
  /** Maximum tokens to generate (optional) */
  max_tokens?: number;
  /** Sampling temperature (0-2, higher = more random) */
  temperature?: number;
}

/**
 * OpenAI API completion response
 * 
 * Response from OpenAI's chat completion API.
 */
export interface OpenAICompletionResponse {
  /** Response ID */
  id: string;
  /** Model used for generation */
  model: string;
  /** Generated completions */
  choices: {
    /** Index of the choice */
    index: number;
    /** Generated message */
    message: OpenAIMessage;
    /** Reason generation stopped */
    finish_reason: 'stop' | 'length' | 'content_filter';
  }[];
}

/**
 * Pinecone vector search request
 * 
 * Parameters for searching vectors in Pinecone.
 */
export interface VectorSearchRequest {
  /** Query text or vector */
  query: string;
  /** Number of results to return */
  topK?: number;
  /** Optional metadata filters */
  filters?: Record<string, any>;
}

/**
 * Pinecone search result item
 * 
 * A single result from a vector search.
 */
export interface VectorSearchResult {
  /** Vector ID */
  id: string;
  /** Similarity score (higher = more similar) */
  score: number;
  /** Associated metadata */
  metadata: Record<string, any>;
}

/**
 * Pinecone search response
 * 
 * Complete response from a Pinecone vector search.
 */
export interface VectorSearchResponse {
  /** Array of search results */
  results: VectorSearchResult[];
}

/**
 * LangChain/LangGraph agent action
 * 
 * Represents a single action taken by the agent during processing.
 */
export interface AgentAction {
  /** Type of action */
  type: 'search' | 'retrieve' | 'generate' | 'analyze';
  /** Input parameters */
  input: Record<string, any>;
  /** Output results (optional) */
  output?: Record<string, any>;
  /** When the action occurred */
  timestamp: string;
}

/**
 * LangChain/LangGraph agent state
 * 
 * Represents the current state of an agent-based conversation.
 */
export interface AgentState {
  /** ID of the conversation */
  conversationId: string;
  /** History of actions taken */
  actions: AgentAction[];
  /** Current step in the processing chain */
  currentStep?: string;
}