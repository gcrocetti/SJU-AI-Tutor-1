import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Chapter } from '../../types';
import diagnosticService from '../../services/diagnosticService';
import './ChapterList.css';

const ChapterList: React.FC = () => {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Fetch chapters on component mount
  useEffect(() => {
    const fetchChapters = async () => {
      setIsLoading(true);
      try {
        const chaptersData = await diagnosticService.getChapters();
        setChapters(chaptersData);
      } catch (error) {
        console.error('Failed to fetch chapters:', error);
        setError('Failed to load chapters. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchChapters();
  }, []);

  // Navigate to chapter quiz
  const handleStartQuiz = (chapterId: string) => {
    navigate(`/diagnostics/quiz/${chapterId}`);
  };

  if (isLoading) {
    return <div className="chapter-list-container">Loading chapters...</div>;
  }

  if (error) {
    return (
      <div className="chapter-list-container">
        <div className="error-message">{error}</div>
        <button onClick={() => window.location.reload()}>Try Again</button>
      </div>
    );
  }

  return (
    <div className="chapter-list-container">
      <button 
        className="navigation-button left"
        onClick={() => navigate('/diagnostics')}
        aria-label="Back to Diagnostics"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
          <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm3.5 7.5a.5.5 0 0 1 0 1H5.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L5.707 7.5H11.5z"/>
        </svg>
      </button>
      
      <div className="chapter-list-header">
        <h1>Chapter Knowledge Checks</h1>
        <p>
          Test your understanding of each chapter's content with these 
          interactive quizzes. Each quiz contains 10 multiple-choice 
          questions to help assess your knowledge.
        </p>
      </div>

      <div className="chapter-grid">
        {chapters.map((chapter) => (
          <div key={chapter.id} className="chapter-card">
            <h2>{chapter.title}</h2>
            <p>{chapter.description}</p>
            
            <div className="chapter-progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${chapter.bestScore || 0}%` }}
              ></div>
            </div>
            
            <div className="chapter-stats">
              <div className="chapter-stat">
                <div className="stat-value">{chapter.bestScore?.toFixed(0) || 'N/A'}%</div>
                <div className="stat-label">Best Score</div>
              </div>
              <div className="chapter-stat">
                <div className="stat-value">{chapter.attempts || 0}</div>
                <div className="stat-label">Attempts</div>
              </div>
            </div>
            
            <button 
              className="start-quiz-button"
              onClick={() => handleStartQuiz(chapter.id)}
            >
              Start Quiz
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChapterList;