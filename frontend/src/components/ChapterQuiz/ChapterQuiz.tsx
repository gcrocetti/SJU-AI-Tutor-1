import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { QuizQuestion, QuizResult, Chapter } from '../../types';
import diagnosticService from '../../services/diagnosticService';
import authService from '../../services/authService';
import './ChapterQuiz.css';

const LETTERS = ['A', 'B', 'C', 'D'];

const ChapterQuiz: React.FC = () => {
  const { chapterId } = useParams<{ chapterId: string }>();
  const navigate = useNavigate();
  
  // Quiz state
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<number[]>([]);
  const [questionAnswered, setQuestionAnswered] = useState(false);
  const [quizResults, setQuizResults] = useState<QuizResult | null>(null);
  
  // Loading and error states
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Get chapter and generate quiz questions on component mount
  useEffect(() => {
    const init = async () => {
      if (!chapterId) {
        navigate('/diagnostics/chapters');
        return;
      }
      
      setIsLoading(true);
      try {
        // Fetch chapter info
        const chaptersData = await diagnosticService.getChapters();
        const currentChapter = chaptersData.find(c => c.id === chapterId) || null;
        
        if (!currentChapter) {
          setError(`Chapter with ID ${chapterId} not found.`);
          return;
        }
        
        setChapter(currentChapter);
        
        // Generate quiz questions
        const questionsData = await diagnosticService.generateQuizQuestions(chapterId);
        setQuestions(questionsData);
        setSelectedAnswers(new Array(questionsData.length).fill(-1));
      } catch (error) {
        console.error('Failed to initialize quiz:', error);
        setError('Failed to load quiz. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    
    init();
  }, [chapterId, navigate]);

  // Handle selecting an answer
  const handleSelectAnswer = (answerIndex: number) => {
    if (questionAnswered) return;
    
    const newAnswers = [...selectedAnswers];
    newAnswers[currentQuestionIndex] = answerIndex;
    setSelectedAnswers(newAnswers);
  };

  // Check if the selected answer is correct
  const handleCheckAnswer = () => {
    setQuestionAnswered(true);
  };

  // Move to the next question
  const handleNextQuestion = () => {
    setCurrentQuestionIndex(currentQuestionIndex + 1);
    setQuestionAnswered(false);
  };

  // Submit the quiz for scoring
  const handleSubmitQuiz = async () => {
    if (!chapterId) return;
    
    setIsLoading(true);
    try {
      // Get user ID from auth service
      const userId = authService.getUserId() || '123'; // Fallback ID if not authenticated
      
      const results = await diagnosticService.scoreQuiz(
        userId,
        chapterId,
        selectedAnswers,
        questions
      );
      
      setQuizResults(results);
    } catch (error) {
      console.error('Failed to score quiz:', error);
      setError('Failed to score quiz. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  // Retry the quiz
  const handleRetryQuiz = () => {
    setCurrentQuestionIndex(0);
    setSelectedAnswers(new Array(questions.length).fill(-1));
    setQuestionAnswered(false);
    setQuizResults(null);
  };

  if (isLoading) {
    return <div className="quiz-container">Loading quiz...</div>;
  }

  if (error) {
    return (
      <div className="quiz-container">
        <div className="error-message">{error}</div>
        <button 
          className="navigation-button left"
          onClick={() => navigate('/diagnostics/chapters')}
          aria-label="Back to Chapters"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm3.5 7.5a.5.5 0 0 1 0 1H5.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L5.707 7.5H11.5z"/>
          </svg>
        </button>
      </div>
    );
  }

  // Current question
  const currentQuestion = questions[currentQuestionIndex];
  
  // Whether it's the last question
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  
  // Progress percentage
  const progressPercentage = questions.length > 0 
    ? ((currentQuestionIndex) / questions.length) * 100 
    : 0;

  // Show results if quiz is completed
  if (quizResults) {
    return (
      <div className="quiz-container">
        <button 
          className="navigation-button left"
          onClick={() => navigate('/diagnostics/chapters')}
          aria-label="Back to Chapters"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm3.5 7.5a.5.5 0 0 1 0 1H5.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L5.707 7.5H11.5z"/>
          </svg>
        </button>
        
        <div className="results-container">
          <div className="results-header">
            <h1>Quiz Results</h1>
            <h2>{chapter?.title}</h2>
          </div>
          
          <div className="results-score">
            {quizResults.percentage.toFixed(0)}%
          </div>
          
          <div className="results-message">
            {quizResults.percentage >= 80 
              ? 'Excellent! You have a strong understanding of this topic.' 
              : quizResults.percentage >= 60 
                ? 'Good work! You understand the basics but should review some concepts.' 
                : 'You should review this chapter material more thoroughly.'}
          </div>
          
          <div className="results-stats">
            <div className="results-stat">
              <div className="stat-value">{quizResults.correct}</div>
              <div className="stat-label">Correct</div>
            </div>
            <div className="results-stat">
              <div className="stat-value">{quizResults.total - quizResults.correct}</div>
              <div className="stat-label">Incorrect</div>
            </div>
            <div className="results-stat">
              <div className="stat-value">{quizResults.total}</div>
              <div className="stat-label">Total Questions</div>
            </div>
          </div>
          
          {quizResults.bestScores && (
            <div>
              <p>
                Your best score for this chapter: {quizResults.bestScores[chapterId]?.toFixed(0) || 'N/A'}%
              </p>
              <p>
                Total attempts: {quizResults.attemptCounts?.[chapterId] || 0}
              </p>
            </div>
          )}
          
          <div className="results-actions">
            <button 
              className="results-button retry"
              onClick={handleRetryQuiz}
            >
              Retry Quiz
            </button>
            <button 
              className="results-button back"
              onClick={() => navigate('/diagnostics/chapters')}
            >
              Back to Chapters
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="quiz-container">
      <button 
        className="navigation-button left"
        onClick={() => navigate('/diagnostics/chapters')}
        aria-label="Back to Chapters"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
          <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm3.5 7.5a.5.5 0 0 1 0 1H5.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L5.707 7.5H11.5z"/>
        </svg>
      </button>
      
      <div className="quiz-header">
        <h1 className="quiz-title">{chapter?.title}</h1>
        <p className="quiz-subtitle">Quiz your knowledge on this topic</p>
        
        <div className="quiz-progress">
          <div className="progress-text">Question {currentQuestionIndex + 1} of {questions.length}</div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>
      </div>
      
      {currentQuestion && (
        <div className="quiz-question">
          <div className="question-text">{currentQuestion.question}</div>
          
          <div className="quiz-options">
            {currentQuestion.options.map((option, index) => (
              <div 
                key={index}
                className={`quiz-option ${selectedAnswers[currentQuestionIndex] === index ? 'selected' : ''} ${
                  questionAnswered 
                    ? index === currentQuestion.correctIndex 
                      ? 'correct' 
                      : selectedAnswers[currentQuestionIndex] === index 
                        ? 'incorrect' 
                        : '' 
                    : ''
                }`}
                onClick={() => handleSelectAnswer(index)}
              >
                <div className="option-letter">{LETTERS[index]}</div>
                <div>{option}</div>
              </div>
            ))}
          </div>
          
          {questionAnswered && (
            <div className="explanation">
              <strong>Explanation: </strong>
              {currentQuestion.explanation}
            </div>
          )}
          
          <div className="quiz-buttons">
            {!questionAnswered ? (
              <button 
                className="quiz-button check"
                disabled={selectedAnswers[currentQuestionIndex] === -1}
                onClick={handleCheckAnswer}
              >
                Check Answer
              </button>
            ) : (
              <button 
                className={`quiz-button ${isLastQuestion ? 'next' : 'next'}`}
                onClick={isLastQuestion ? handleSubmitQuiz : handleNextQuestion}
              >
                {isLastQuestion ? 'Submit Quiz' : 'Next Question'}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChapterQuiz;