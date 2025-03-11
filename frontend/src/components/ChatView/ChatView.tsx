import { useState, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import './ChatView.css';

/* Imports for backend implementation */
//import chatService from '../../services/chatService'; // Handles API communication with backend, needed to replace placeholder logic we're using now
//import { Message } from '../../types'; // Handles proper typing for messages 
//import { ChatViewProps } from './types'; // Handles props for this component, needed when passing initial messages, session IDs, callback functions, etc

/**
 * ChatView Component
 * 
 * A React component that provides a chat interface for students to interact with the Ciro AI tutor.
 * Currently implements a simple placeholder response system, but designed to be connected to a
 * backend service that will process messages through an LLM (likely OpenAI) and retrieve context
 * from a vector database (Pinecone).
 * 
 * @component
 * @example
 * return (
 *   <ChatView />
 * )
 */
const ChatView: React.FC = () => {
  // State to store all messages in the conversation
  const [messages, setMessages] = useState<Array<{ id: string; text: string; sender: 'user' | 'bot' }>>([
    {
      id: '1',
      text: "Hello! I'm Ciro, your AI tutor for LST1000. How can I help you today?",
      sender: "bot"
    }
  ]);
  
  // State for controlling the input field
  const [inputValue, setInputValue] = useState<string>('');
  
  // State to control the display of the typing indicator
  const [isTyping, setIsTyping] = useState<boolean>(false);
  
  // Reference to the bottom of the message list for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  /**
   * Auto-scrolls to the bottom of the message list whenever
   * new messages are added or the typing indicator appears
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);
  
  /**
   * Updates the input field state as the user types
   * 
   * @param e - The input change event
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };
  
  /**
   * Handles message submission when the user sends a message
   * 
   * Currently implements a placeholder response system.
   * TODO: Replace with actual backend service integration
   * - Will need to call chatService.sendMessage()
   * - Will need to track session ID
   * - Will need to handle API errors
   * - Will need to process bot responses, potentially including citations and "thinking" steps
   * 
   * @param e - The form submission event
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    
    // Add user message to the chat
    const userMessage = {
      id: uuidv4(),
      text: inputValue,
      sender: 'user' as const
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    
    // Show typing indicator to simulate the bot thinking
    setIsTyping(true);
    
    // PLACEHOLDER: Replace with actual API call
    // TODO: Implement API integration with backend
    setTimeout(() => {
      const botResponse = {
        id: uuidv4(),
        text: "Hmmm, let me think about that...",
        sender: 'bot' as const
      };
      
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 2000); // Simulated 2-second delay
    
    /**
     * FUTURE IMPLEMENTATION:
     * 
     * try {
     *   // Send to backend and await response
     *   const sessionId = "current-session-id"; // Will need state for this
     *   const response = await chatService.sendMessage(inputValue, sessionId);
     *   
     *   // Process and add the bot's response
     *   setMessages(prev => [...prev, response]);
     * } catch (error) {
     *   // Handle errors and show appropriate message to user
     *   console.error('Failed to get response:', error);
     *   setMessages(prev => [...prev, {
     *     id: uuidv4(),
     *     text: "Sorry, I encountered an error. Please try again.",
     *     sender: 'bot'
     *   }]);
     * } finally {
     *   setIsTyping(false);
     * }
     */
  };

  return (
    <div className="chat-main">
      <div className="chat-window">
        {/* Render each message */}
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`message ${message.sender === 'bot' ? 'bot-message' : 'user-message'}`}
          >
            {message.text}
          </div>
        ))}
        
        {/* Typing indicator - shown when isTyping is true */}
        {isTyping && (
          <div className="message bot-message typing-indicator">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
        )}
        
        {/* Reference for auto-scrolling */}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Message input form */}
      <form onSubmit={handleSubmit} className="input-container">
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          placeholder="Ask Ciro anything about LST1000..."
          className="input-field"
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={!inputValue.trim()}
          aria-label="Send message"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path
              d="M12 2L12 22M12 2L6 8M12 2L18 8"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
              fill="none"
            />
          </svg>
        </button>
      </form>
    </div>
  );
};

export default ChatView;