/**
 * Chat-related Types
 * 
 * This file contains types related to chat functionality, including
 * messages, conversations, and related UI state.
 */

import { AgentAction } from './api';

/**
 * Message sender type
 * 
 * Defines who sent a message - either the user or the AI tutor (bot).
 */
export type MessageSender = 'user' | 'bot';

/**
 * Message Type
 * 
 * Represents a single message in the chat conversation.
 * Used in chat history, user inputs, and bot responses.
 */
export interface Message {
  /** Unique identifier for the message */
  id: string;
  /** Text content of the message */
  text: string;
  /** Who sent the message - either the user or the AI tutor */
  sender: MessageSender;
  /** When the message was sent */
  timestamp: Date;
  /** Optional metadata for enhanced message functionality */
  metadata?: {
    /** Flag to show thinking/reasoning process */
    thinking?: boolean;
    /** Agent actions taken to process the message */
    actions?: AgentAction[];
    /** Citations and references for message content */
    citations?: Citation[];
    /** Confidence score of the response (0-100) */
    confidence?: number;
  };
}

/**
 * Citation Type
 * 
 * Represents a source or reference cited in a bot response.
 * Used to provide attribution and verification.
 */
export interface Citation {
  /** Unique identifier for the citation */
  id: string;
  /** Title of the cited source */
  title: string;
  /** Relevant excerpt from the source */
  text: string;
  /** Source identifier (URL, document name, etc.) */
  source: string;
  /** Score indicating relevance (0-100) */
  relevanceScore: number;
}

/**
 * Conversation Type
 * 
 * Represents a complete chat conversation with multiple messages.
 * Used for persistence and history tracking.
 */
export interface Conversation {
  /** Unique identifier for the conversation */
  id: string;
  /** Optional title/summary of the conversation */
  title?: string;
  /** All messages in the conversation */
  messages: Message[];
  /** When the conversation started */
  createdAt: Date;
  /** When the conversation was last updated */
  updatedAt: Date;
  /** Optional metadata for categorization and filtering */
  metadata?: {
    /** Main topic of conversation */
    topic?: string;
    /** Brief summary of the conversation */
    summary?: string;
    /** Tags for categorization */
    tags?: string[];
  };
}

/**
 * Chat State
 * 
 * Represents the current state of the chat interface.
 * Used for managing UI state in components.
 */
export interface ChatState {
  /** All available conversations */
  conversations: Conversation[];
  /** ID of the currently active conversation */
  activeConversationId: string | null;
  /** Whether a network request is in progress */
  isLoading: boolean;
  /** Error message, if any */
  error: string | null;
}

/**
 * Send Message Request
 * 
 * Represents a request to send a message to the AI tutor.
 * Used for API communication.
 */
export interface SendMessageRequest {
  /** ID of the conversation */
  conversationId: string;
  /** Message text */
  text: string;
  /** ID of the user sending the message */
  userId: string;
}

/**
 * Send Message Response
 * 
 * Represents a response from the AI tutor API.
 * Used for processing and displaying bot responses.
 */
export interface SendMessageResponse {
  /** The bot's response message */
  message: Message;
  /** Optional thinking process details */
  thinking?: {
    /** Steps taken by the agent to generate the response */
    steps: AgentAction[];
  };
  /** Optional citations for sources used in the response */
  citations?: Citation[];
}