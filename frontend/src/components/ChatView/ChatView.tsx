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
   * Formats source links in text
   * 
   * @param text - The text containing source links to format
   * @returns Formatted source links
   */
  const formatSourceLinks = (text: string): ReactNode[] => {
    // Regular expression to find source links
    // Matches [Source: https://...] or similar patterns
    const sourcePattern = /\[(Source|Source \d+):\s*(https?:\/\/[^\s\]]+)\]/g;
    
    if (!sourcePattern.test(text)) {
      return [text];
    }
    
    const parts = [];
    let lastIndex = 0;
    let match;
    const regex = new RegExp(sourcePattern);
    
    // Reset regex
    regex.lastIndex = 0;
    
    // Find all matches
    while ((match = regex.exec(text)) !== null) {
      // Add text before the match
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }
      
      const sourceLabel = match[1];
      const sourceUrl = match[2];
      
      // Extract domain for displaying a cleaner link text
      let displayUrl = sourceUrl;
      try {
        const url = new URL(sourceUrl);
        displayUrl = url.hostname.replace('www.', '');
      } catch (e) {
        // Use the full URL if parsing fails
      }
      
      // Add the formatted link
      parts.push(
        <a 
          key={`source-${match.index}`}
          href={sourceUrl}
          className="source-link"
          target="_blank"
          rel="noopener noreferrer"
        >
          {`[${sourceLabel}: ${displayUrl}]`}
        </a>
      );
      
      lastIndex = regex.lastIndex;
    }
    
    // Add any remaining text
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }
    
    return parts;
  };
  
  /**
   * Format message text with paragraphs, lists, and links
   * 
   * @param text - The message text to format
   * @returns Formatted message content
   */
  const formatMessageContent = (text: string): ReactNode => {
    if (!text) return null;
    
    // Split the text into paragraphs
    const paragraphs = text.split('\n\n');
    
    return (
      <>
        {paragraphs.map((paragraph, index) => {
          // Check if paragraph is a numbered list item
          const isNumberedListItem = /^\d+\.\s/.test(paragraph);
          
          // Check if paragraph is a bulleted list item
          const isBulletedListItem = /^[-*•]\s/.test(paragraph);
          
          if (paragraph.trim() === '') {
            return <br key={`br-${index}`} />;
          } else if (isNumberedListItem) {
            // For a cleaner display, we'll create proper lists later
            // For now, just display as paragraph
            return (
              <p key={`p-${index}`}>
                {formatSourceLinks(paragraph)}
              </p>
            );
          } else if (isBulletedListItem) {
            // For a cleaner display, we'll create proper lists later
            // For now, just display as paragraph
            return (
              <p key={`p-${index}`}>
                {formatSourceLinks(paragraph)}
              </p>
            );
          } else {
            return (
              <p key={`p-${index}`}>
                {formatSourceLinks(paragraph)}
              </p>
            );
          }
        })}
      </>
    );
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
            {formatMessageContent(message.text)}
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