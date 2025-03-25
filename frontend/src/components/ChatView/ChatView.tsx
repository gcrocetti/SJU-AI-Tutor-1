import { useState, useRef, useEffect, ReactNode } from 'react';
import { v4 as uuidv4 } from 'uuid';
import './ChatView.css';
import chatService from '../../services/chatService';

/**
 * ChatView Component
 * 
 * A React component that provides a chat interface for students to interact with the Ciro AI tutor.
 * Connects to a Flask API that processes messages through the agent system.
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
      text: "Hey there! I'm CIRO, your AI Tutor. I'm here to provide you with academic and personal support. How may I help you today?",
      sender: "bot"
    }
  ]);
  
  // State for controlling the input field
  const [inputValue, setInputValue] = useState<string>('');
  
  // State to control the display of the typing indicator
  const [isTyping, setIsTyping] = useState<boolean>(false);
  
  // State to store the current session ID
  const [sessionId, setSessionId] = useState<string>('');
  
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
   * Formats a message text to properly display hyperlinks to sources
   * 
   * Converts patterns like [Source: https://example.com] to hyperlinks
   * 
   * @param text - The message text to format
   * @returns - Formatted message with hyperlinked sources
   */
  const formatMessageWithLinks = (text: string): ReactNode[] => {
    if (!text) return [];
    
    // Regular expression to find source links
    // Matches [Source: https://...] or similar patterns
    const sourcePattern = /\[(Source|Source \d+):\s*(https?:\/\/[^\s\]]+)\]/g;
    
    // Split the text by source links
    const parts = text.split(sourcePattern);
    
    // If no source links found, return the original text
    if (parts.length === 1) return [text];
    
    // Initialize result array
    const result: ReactNode[] = [];
    let key = 0;
    
    // Process each part
    for (let i = 0; i < parts.length; i++) {
      // Add regular text part
      if (parts[i] && !parts[i].startsWith('http')) {
        result.push(<span key={key++}>{parts[i]}</span>);
      }
      
      // If we have a source label and URL, create a link
      if (i + 1 < parts.length && parts[i + 1]?.startsWith('http')) {
        const sourceLabel = parts[i] || 'Source';
        const sourceUrl = parts[i + 1];
        
        // Extract domain for displaying a cleaner link text
        let displayUrl = sourceUrl;
        try {
          const url = new URL(sourceUrl);
          displayUrl = url.hostname.replace('www.', '');
        } catch (e) {
          // Use the full URL if parsing fails
        }
        
        result.push(
          <a 
            key={key++}
            href={sourceUrl}
            className="source-link"
            target="_blank"
            rel="noopener noreferrer"
          >
            {`[${sourceLabel}: ${displayUrl}]`}
          </a>
        );
        
        // Skip the URL part as we've already used it
        i++;
      }
    }
    
    return result;
  };
  
  /**
   * Handles message submission when the user sends a message
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
    
    // Show typing indicator
    setIsTyping(true);
    
    try {
      // Send message to the backend and await response
      const botResponse = await chatService.sendMessage(inputValue, sessionId);
      
      // If this is the first message, store the session ID
      if (!sessionId && botResponse.metadata?.sessionId) {
        setSessionId(botResponse.metadata.sessionId);
      }
      
      // Add the response to the chat
      setMessages(prev => [...prev, {
        id: botResponse.id,
        text: botResponse.text,
        sender: 'bot'
      }]);
    } catch (error) {
      console.error('Failed to get response:', error);
      
      // Show error message
      setMessages(prev => [...prev, {
        id: uuidv4(),
        text: "Sorry, I encountered an error. Please try again.",
        sender: 'bot'
      }]);
    } finally {
      setIsTyping(false);
    }
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
            {formatMessageWithLinks(message.text)}
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
          disabled={isTyping}
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={!inputValue.trim() || isTyping}
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