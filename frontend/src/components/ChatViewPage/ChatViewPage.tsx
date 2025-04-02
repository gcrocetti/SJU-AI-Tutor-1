import { useNavigate } from 'react-router-dom';
import ChatView from '../ChatView/ChatView';
import useDocumentTitle from '../../hooks/useDocumentTitle';
import './ChatViewPage.css';

const ChatViewPage: React.FC = () => {
  const navigate = useNavigate();
  
  // Set the document title for the chat page
  useDocumentTitle('CIRO');
  
  return (
    <div className="chat-page">
      <ChatView />
      <button 
        className="navigation-button right"
        onClick={() => navigate('/diagnostics')}
        aria-label="View Diagnostics"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
          <path fillRule="evenodd" d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"/>
        </svg>
      </button>
    </div>
  );
};

export default ChatViewPage;