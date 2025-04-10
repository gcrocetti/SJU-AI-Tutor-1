import { useState, useRef, useEffect, ReactNode } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ChatView.css';
import chatService from '../../services/chatService';
import diagnosticService from '../../services/diagnosticService';
import { Message, TextEvaluation } from '../../types';

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
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hey there! I'm CIRO, your AI Tutor. I'm here to provide you with academic and personal support. How may I help you today?",
      sender: "bot",
      timestamp: new Date()
    }
  ]);
  
  // State for controlling the input field
  const [inputValue, setInputValue] = useState<string>('');
  
  // State to control the display of the typing indicator
  const [isTyping, setIsTyping] = useState<boolean>(false);
  
  // State to store the current session ID
  const [sessionId, setSessionId] = useState<string>('');
  
  // State to track if we are currently working on a knowledge check
  const [activeKnowledgeCheck, setActiveKnowledgeCheck] = useState<{
    messageId: string;
    topic: string;
    prompt: string;
    response: string;
  } | null>(null);
  
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
   * Auto-adjusts the textarea height based on content
   */
  const adjustTextareaHeight = () => {
    const textarea = document.querySelector('.input-field') as HTMLTextAreaElement;
    if (textarea) {
      // Reset height to auto to calculate the new height correctly
      textarea.style.height = 'auto';
      
      // Set new height (with a max of 150px, about 5-6 lines)
      const newHeight = Math.min(textarea.scrollHeight, 150);
      textarea.style.height = `${newHeight}px`;
    }
  };
  
  /**
   * Adjust textarea height whenever input value changes
   */
  useEffect(() => {
    adjustTextareaHeight();
  }, [inputValue]);
  
  // No replacement
  
  /**
   * Updates the input field state as the user types
   * 
   * @param e - The textarea change event
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
  };
  
  /**
   * Handles key press events in the input field
   * Allows Shift+Enter for new lines, Enter alone to submit
   * 
   * @param e - The keyboard event
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // If Enter is pressed without Shift, submit the form
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent default behavior (new line)
      handleSubmit(e as unknown as React.FormEvent);
    }
    // Shift+Enter will create a new line (default behavior)
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
   * Handles submission of a free-response knowledge check answer
   */
  const handleKnowledgeCheckSubmit = async () => {
    if (!activeKnowledgeCheck || !activeKnowledgeCheck.response.trim()) return;
    
    const { messageId, topic, prompt, response } = activeKnowledgeCheck;
    
    // First update the message to show it's being evaluated
    setMessages(prev => prev.map(message => {
      if (message.id === messageId) {
        return {
          ...message,
          metadata: {
            ...message.metadata,
            knowledgeCheck: {
              ...message.metadata?.knowledgeCheck!,
              awaitingResponse: false,
              response: response
            }
          }
        };
      }
      return message;
    }));
    
    // Show typing indicator
    setIsTyping(true);
    
    try {
      // Get a mock user ID for now
      const userId = '123';
      
      // Call the evaluate text response API
      const evaluation = await diagnosticService.evaluateTextResponse(
        userId,
        topic,
        prompt,
        response
      );
      
      // Update the message with the evaluation
      setMessages(prev => prev.map(message => {
        if (message.id === messageId) {
          return {
            ...message,
            metadata: {
              ...message.metadata,
              knowledgeCheck: {
                ...message.metadata?.knowledgeCheck!,
                evaluation
              }
            }
          };
        }
        return message;
      }));
      
      // Add a follow-up message with the evaluation results
      const feedbackMessage: Message = {
        id: uuidv4(),
        text: `I've evaluated your response:
          
**Score: ${evaluation.totalScore}/10**

${evaluation.feedback}

**Breakdown:**
- Accuracy: ${evaluation.scores.accuracy}/3
- Depth: ${evaluation.scores.depth}/3
- Clarity: ${evaluation.scores.clarity}/2
- Application: ${evaluation.scores.application}/2`,
        sender: 'bot',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, feedbackMessage]);
      
      // Clear the active knowledge check
      setActiveKnowledgeCheck(null);
    } catch (error) {
      console.error('Failed to evaluate response:', error);
      
      // Show error message
      setMessages(prev => [...prev, {
        id: uuidv4(),
        text: "Sorry, I encountered an error evaluating your response. Please try again.",
        sender: 'bot',
        timestamp: new Date()
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  /**
   * Format message with paragraphs, lists, links, and knowledge checks
   * 
   * @param message - The message to format
   * @returns Formatted message content
   */
  const formatMessageContent = (message: Message): ReactNode => {
    if (!message.text && !message.metadata?.knowledgeCheck) return null;
    
    // Fallback function for plain text rendering in case of markdown errors
    const renderPlainText = (text: string) => {
      return (
        <>
          {text.split('\n').map((line, i) => (
            <React.Fragment key={i}>
              {line}
              <br />
            </React.Fragment>
          ))}
        </>
      );
    };
    
    // Handle knowledge check messages
    if (message.metadata?.knowledgeCheck && message.metadata.knowledgeCheck.type === 'free-response') {
      const knowledgeCheck = message.metadata.knowledgeCheck;
      
      return (
        <div className="knowledge-check-container">
          <div className="knowledge-check-prompt">
            <h3>Knowledge Check: {knowledgeCheck.topic}</h3>
            <div className="markdown-content">
              {(() => {
                try {
                  return (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        code: ({ inline, ...props }) => (
                          inline ? <code className="inline-code" {...props} /> : <code className="code-block" {...props} />
                        ),
                      }}
                    >
                      {knowledgeCheck.prompt}
                    </ReactMarkdown>
                  );
                } catch (error) {
                  console.error("Error rendering markdown in knowledge check prompt:", error);
                  return renderPlainText(knowledgeCheck.prompt);
                }
              })()}
            </div>
          </div>
          
          {knowledgeCheck.awaitingResponse ? (
            <div className="knowledge-check-response-form">
              <textarea
                value={activeKnowledgeCheck?.response || ''}
                onChange={(e) => setActiveKnowledgeCheck(prev => 
                  prev && prev.messageId === message.id 
                    ? { ...prev, response: e.target.value } 
                    : { messageId: message.id, topic: knowledgeCheck.topic, prompt: knowledgeCheck.prompt, response: e.target.value }
                )}
                placeholder="Enter your response here..."
                rows={5}
                className="knowledge-check-textarea"
              />
              <button 
                onClick={handleKnowledgeCheckSubmit}
                disabled={!activeKnowledgeCheck?.response?.trim()}
                className="knowledge-check-submit"
              >
                Submit Answer
              </button>
            </div>
          ) : (
            <div className="knowledge-check-submitted">
              <div className="knowledge-check-response">
                <h4>Your Response:</h4>
                <div className="user-markdown-response">
                  {(() => {
                    try {
                      return (
                        <ReactMarkdown 
                          remarkPlugins={[remarkGfm]}
                          components={{
                            code: ({ inline, ...props }) => (
                              inline ? <code className="inline-code" {...props} /> : <code className="code-block" {...props} />
                            ),
                          }}
                        >
                          {knowledgeCheck.response || ''}
                        </ReactMarkdown>
                      );
                    } catch (error) {
                      console.error("Error rendering markdown in user response:", error);
                      return renderPlainText(knowledgeCheck.response || '');
                    }
                  })()}
                </div>
              </div>
              
              {knowledgeCheck.evaluation && (
                <div className="knowledge-check-evaluation">
                  <h4>Evaluation:</h4>
                  <div className="evaluation-score">
                    Score: {knowledgeCheck.evaluation.totalScore}/10
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      );
    }
    
    // For regular messages, use ReactMarkdown for rendering
    try {
      return (
        <div className="markdown-content">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              // Custom link renderer to add target="_blank" for external links
              a: (props) => (
                <a 
                  {...props} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="markdown-link"
                />
              ),
              // Customize code blocks with syntax highlighting class
              code: ({ inline, ...props }) => (
                inline 
                  ? <code className="inline-code" {...props} /> 
                  : <code className="code-block" {...props} />
              ),
              // Add custom classes to other elements as needed
              h1: (props) => <h1 className="markdown-h1" {...props} />,
              h2: (props) => <h2 className="markdown-h2" {...props} />,
              h3: (props) => <h3 className="markdown-h3" {...props} />,
              blockquote: (props) => <blockquote className="markdown-blockquote" {...props} />,
              table: (props) => <table className="markdown-table" {...props} />,
            }}
          >
            {message.text}
          </ReactMarkdown>
        </div>
      );
    } catch (error) {
      console.error("Error rendering markdown, falling back to plain text:", error);
      // If markdown rendering fails, fall back to plain text
      return (
        <div className="fallback-text">
          {renderPlainText(message.text)}
        </div>
      );
    }
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
    const userMessage: Message = {
      id: uuidv4(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    
    // Show typing indicator
    setIsTyping(true);
    
    // Check if the message is requesting a knowledge check
    const isKnowledgeCheckRequest = inputValue.toLowerCase().includes('check my knowledge') || 
                                   inputValue.toLowerCase().includes('test my understanding') || 
                                   inputValue.toLowerCase().includes('evaluate my knowledge');
    
    try {
      // Send message to the backend and await response
      const botResponse = await chatService.sendMessage(inputValue, sessionId);
      
      // If this is the first message, store the session ID
      if (!sessionId && botResponse.metadata?.sessionId) {
        setSessionId(botResponse.metadata.sessionId);
      }
      
      // Add the response to the chat
      const botMessageBase: Message = {
        id: botResponse.id || uuidv4(),
        text: botResponse.text,
        sender: 'bot',
        timestamp: new Date(),
        metadata: botResponse.metadata
      };
      
      // If this was a knowledge check request, we can simulate a free-response question
      if (isKnowledgeCheckRequest) {
        // For demo purposes, we'll hardcode a topic and prompt
        const topic = 'Data Structures';
        const prompt = 'Please explain how a hash table works and its applications in computer science.';
        
        // First send a regular response
        setMessages(prev => [...prev, botMessageBase]);
        
        // Then after a short delay, send a knowledge check question
        setTimeout(() => {
          const knowledgeCheckMessage: Message = {
            id: uuidv4(),
            text: '',
            sender: 'bot',
            timestamp: new Date(),
            metadata: {
              knowledgeCheck: {
                type: 'free-response',
                topic,
                prompt,
                awaitingResponse: true
              }
            }
          };
          
          setMessages(prev => [...prev, knowledgeCheckMessage]);
        }, 1000);
      } else {
        // Normal message flow
        setMessages(prev => [...prev, botMessageBase]);
      }
    } catch (error) {
      console.error('Failed to get response:', error);
      
      // Show error message
      setMessages(prev => [...prev, {
        id: uuidv4(),
        text: "Sorry, I encountered an error. Please try again.",
        sender: 'bot',
        timestamp: new Date()
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
            {formatMessageContent(message)}
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
        <textarea
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask Ciro anything about LST1000... (Shift+Enter for new line)"
          className="input-field"
          disabled={isTyping}
          rows={1}
          style={{ resize: 'none' }}
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