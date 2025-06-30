import { v4 as uuidv4 } from 'uuid';
import { 
  Conversation, 
  Message
} from '../types';

/**
 * ChatService
 * 
 * Service class for handling all chat-related operations.
 * Connects to the Flask backend API that interfaces with:
 * - OpenAI's ChatGPT APIs for the LLM
 * - Pinecone for vector storage and retrieval
 * - LangChain/LangGraph for orchestration
 */
export class ChatService {
  /**
   * Send a message to the AI tutor and get a response
   * 
   * This method handles:
   * 1. Formatting the user's message
   * 2. Sending it to the backend
   * 3. Receiving and processing the AI response
   * 
   * @param text - The user's message text
   * @param sessionId - Optional ID of an existing conversation
   * @returns Promise resolving to the AI's response message
   */
  async sendMessage(text: string, sessionId?: string): Promise<Message> {
    // Create the request object
    const request = {
      message: text,
      session_id: sessionId
    };
    
    try {
      // Make the API call to the Flask backend
      const response = await fetch('http://localhost:5001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(request)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get response from server');
      }
      
      // Parse the response
      const result = await response.json();
      
      // Store session ID from response
      const returnedSessionId = result.session_id || sessionId;
      
      // Create a formatted bot message from the response
      const botMessage: Message = {
        id: uuidv4(),
        text: result.response,
        sender: 'bot',
        timestamp: new Date(),
        metadata: {
          // Include which agents were used and the session ID
          thinking: true,
          sessionId: returnedSessionId,
          actions: result.used_agents?.map((agent: string) => ({
            type: 'agent',
            input: { name: agent },
            output: { used: true },
            timestamp: new Date().toISOString()
          })) || []
        }
      };
      
      return botMessage;
    } catch (error) {
      // Log and rethrow errors
      console.error('Failed to send message', error);
      throw error;
    }
  }
  
  /**
   * Get a list of the user's conversations
   * 
   * @returns Promise resolving to an array of conversations
   */
  async getConversations(): Promise<Conversation[]> {
    try {
      // Make API call to the sessions endpoint
      const response = await fetch('http://localhost:5001/api/sessions');
      
      if (!response.ok) {
        throw new Error('Failed to fetch conversations');
      }
      
      const result = await response.json();
      
      // Format the sessions into conversations
      const conversations: Conversation[] = result.sessions.map((sessionId: string) => ({
        id: sessionId,
        title: `Conversation ${sessionId.substring(0, 8)}`,
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date()
      }));
      
      return conversations;
    } catch (error) {
      console.error('Failed to fetch conversations', error);
      return [];
    }
  }
  
  /**
   * Get a specific conversation by ID, including its messages
   * 
   * @param id - The ID of the conversation to retrieve
   * @returns Promise resolving to the conversation or null if not found
   */
  async getConversation(id: string): Promise<Conversation | null> {
    try {
      // Make API call to get the specific session
      const response = await fetch(`http://localhost:5001/api/sessions/${id}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch conversation ${id}`);
      }
      
      const result = await response.json();
      
      // Format the session into a conversation
      const conversation: Conversation = {
        id: result.session_id,
        title: `Conversation ${result.session_id.substring(0, 8)}`,
        messages: result.messages.map((msg: any) => ({
          id: uuidv4(),
          text: msg.content,
          sender: msg.role === 'user' ? 'user' : 'bot',
          timestamp: new Date()
        })),
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      return conversation;
    } catch (error) {
      console.error(`Failed to fetch conversation ${id}`, error);
      return null;
    }
  }
  
  /**
   * Create a new conversation
   * 
   * @param title - Optional title for the conversation
   * @returns Promise resolving to the new conversation
   */
  async createConversation(title?: string): Promise<Conversation> {
    const id = uuidv4();
    const now = new Date();
    
    // Create a new conversation locally
    // In a full implementation, this could call the API to initialize a new session
    const newConversation: Conversation = {
      id,
      title: title || 'New Conversation',
      messages: [],
      createdAt: now,
      updatedAt: now
    };
    
    return newConversation;
  }
}

// Create a singleton instance for use throughout the application
export const chatService = new ChatService();
export default chatService;