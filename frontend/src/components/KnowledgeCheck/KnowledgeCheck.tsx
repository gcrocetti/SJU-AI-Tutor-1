import React, { useState, useEffect } from 'react';
import { Chapter, QuizQuestion, QuizResult } from '../../types';
import diagnosticService from '../../services/diagnosticService';
import './KnowledgeCheck.css';

const LETTERS = ['A', 'B', 'C', 'D'];

interface KnowledgeCheckProps {
  onClose?: () => void;
}

const KnowledgeCheck: React.FC<KnowledgeCheckProps> = ({ onClose }) => {
  // Active view (chapter selection, quiz, or results)
  const [view, setView] = useState<'chapters' | 'quiz' | 'results'>('chapters');
  
  // Available chapters
  const [chapters, setChapters] = useState<Chapter[]>([]);
  
  // Selected chapter
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null);
  
  // Quiz questions
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  
  // Current question index
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  
  // Selected answers
  const [selectedAnswers, setSelectedAnswers] = useState<number[]>([]);
  
  // Whether the current question has been answered
  const [questionAnswered, setQuestionAnswered] = useState(false);
  
  // Quiz results
  const [quizResults, setQuizResults] = useState<QuizResult | null>(null);
  
  // Loading state
  const [isLoading, setIsLoading] = useState(false);
  
  // Error state
  const [error, setError] = useState<string | null>(null);

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

  // Select a chapter
  const handleChapterSelect = (chapter: Chapter) => {
    setSelectedChapter(chapter);
  };

  // Start the quiz for the selected chapter
  const handleStartQuiz = async () => {
    if (!selectedChapter) return;
    
    setIsLoading(true);
    try {
      const questionsData = await diagnosticService.generateQuizQuestions(selectedChapter.id);
      setQuestions(questionsData);
      setSelectedAnswers(new Array(questionsData.length).fill(-1));
      setCurrentQuestionIndex(0);
      setQuestionAnswered(false);
      setView('quiz');
    } catch (error) {
      console.error('Failed to generate quiz questions:', error);
      setError('Failed to load quiz questions. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  // Select an answer for the current question
  const handleSelectAnswer = (answerIndex: number) => {
    if (questionAnswered) return;
    
    const newAnswers = [...selectedAnswers];
    newAnswers[currentQuestionIndex] = answerIndex;
    setSelectedAnswers(newAnswers);
  };

  // Check the selected answer
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
    if (!selectedChapter) return;
    
    setIsLoading(true);
    try {
      // Get user ID from auth service (mock for now)
      const userId = '123';
      
      const results = await diagnosticService.scoreQuiz(
        userId,
        selectedChapter.id,
        selectedAnswers,
        questions
      );
      
      setQuizResults(results);
      setView('results');
    } catch (error) {
      console.error('Failed to score quiz:', error);
      setError('Failed to score quiz. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  // Retry the quiz
  const handleRetryQuiz = () => {
    setView('quiz');
    setCurrentQuestionIndex(0);
    setSelectedAnswers(new Array(questions.length).fill(-1));
    setQuestionAnswered(false);
    setQuizResults(null);
  };

  // Return to chapter selection
  const handleBackToChapters = () => {
    setView('chapters');
    setSelectedChapter(null);
    setQuestions([]);
    setSelectedAnswers([]);
    setCurrentQuestionIndex(0);
    setQuestionAnswered(false);
    setQuizResults(null);
  };

  // Current question
  const currentQuestion = questions[currentQuestionIndex];
  
  // Whether it's the last question
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  
  // Progress percentage
  const progressPercentage = questions.length > 0 
    ? ((currentQuestionIndex) / questions.length) * 100 
    : 0;

  if (isLoading) {
    return (
      <div className="knowledge-check-container">
        <div className="loading-message">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="knowledge-check-container">
        <div className="error-message">{error}</div>
        <button onClick={handleBackToChapters}>Try Again</button>
      </div>
    );
  }

  return (
    <div className="knowledge-check-container">
      {view === 'chapters' && (
        <>
          <h2>Knowledge Check</h2>
          <p>Select a chapter to test your knowledge:</p>
          
          <div className="chapter-selection">
            {chapters.map((chapter) => (
              <div 
                key={chapter.id}
                className={`chapter-card ${selectedChapter?.id === chapter.id ? 'selected' : ''}`}
                onClick={() => handleChapterSelect(chapter)}
              >
                <h3>{chapter.title}</h3>
                <p>{chapter.description}</p>
                <div className="chapter-stats">
                  <span>Best Score: {chapter.bestScore?.toFixed(0) || 'N/A'}%</span>
                  <span>Attempts: {chapter.attempts || 0}</span>
                </div>
              </div>
            ))}
          </div>
          
          <div className="chapter-action">
            <button 
              className="start-quiz-button"
              disabled={!selectedChapter}
              onClick={handleStartQuiz}
            >
              Start Quiz
            </button>
          </div>
        </>
      )}

      {view === 'quiz' && currentQuestion && (
        <div className="quiz-container">
          <div className="quiz-header">
            <h3>{selectedChapter?.title}</h3>
            <div className="quiz-progress">
              <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
            </div>
          </div>
          
          <div className="quiz-question">
            <h3>{currentQuestion.question}</h3>
            
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
                  {option}
                </div>
              ))}
            </div>
            
            {questionAnswered && (
              <div className="explanation">
                <strong>Explanation: </strong>
                {currentQuestion.explanation}
              </div>
            )}
          </div>
          
          <div className="quiz-navigation">
            <div>
              {/* Placeholder for back button if needed */}
            </div>
            
            {!questionAnswered ? (
              <button 
                className="quiz-button next"
                disabled={selectedAnswers[currentQuestionIndex] === -1}
                onClick={handleCheckAnswer}
              >
                Check Answer
              </button>
            ) : (
              <button 
                className={`quiz-button ${isLastQuestion ? 'submit' : 'next'}`}
                onClick={isLastQuestion ? handleSubmitQuiz : handleNextQuestion}
              >
                {isLastQuestion ? 'Submit Quiz' : 'Next Question'}
              </button>
            )}
          </div>
        </div>
      )}

      {view === 'results' && quizResults && (
        <div className="results-container">
          <h2>Quiz Results</h2>
          
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
            <div className="stat-item">
              <div className="stat-value">{quizResults.correct}</div>
              <div className="stat-label">Correct</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{quizResults.total - quizResults.correct}</div>
              <div className="stat-label">Incorrect</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{quizResults.total}</div>
              <div className="stat-label">Total Questions</div>
            </div>
          </div>
          
          {quizResults.bestScores && selectedChapter && (
            <div>
              <p>
                Your best score for this chapter: {quizResults.bestScores[selectedChapter.id]?.toFixed(0) || 'N/A'}%
              </p>
              <p>
                Total attempts: {quizResults.attemptCounts?.[selectedChapter.id] || 0}
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
              onClick={handleBackToChapters}
            >
              Back to Chapters
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeCheck;