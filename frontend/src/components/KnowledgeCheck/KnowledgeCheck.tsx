import React, { useState, useEffect } from 'react';
import { Chapter, QuizQuestion, QuizResult, FrontendQuizQuestion } from '../../types';
import diagnosticService from '../../services/diagnosticService';
import './KnowledgeCheck-v2.css';

// Component version: v1.0.2 - Updated with new CSS file

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
  
  // Quiz questions (without correct answers initially)
  const [questions, setQuestions] = useState<FrontendQuizQuestion[]>([]);
  
  // Quiz questions with correct answers (only available after submission)
  const [completeQuestions, setCompleteQuestions] = useState<QuizQuestion[]>([]);
  
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

  // Check the selected answer and provide immediate feedback
  const handleCheckAnswer = async () => {
    try {
      // Get user ID from auth service (mock for now)
      const userId = '123';
      
      // Force-decode and display the correct answers from session storage
      const storedQuestionsData = sessionStorage.getItem(`quiz_${selectedChapter?.id}`);
      if (storedQuestionsData) {
        // Decode the base64 encoded questions
        let fullQuestions: QuizQuestion[] = [];
        try {
          fullQuestions = JSON.parse(atob(storedQuestionsData));
          console.log("Retrieved questions:", fullQuestions);
        } catch (e) {
          console.error("Failed to decode questions:", e);
          fullQuestions = [];
        }
        
        if (fullQuestions.length > 0) {
          // Calculate current correct/incorrect
          let correctCount = 0;
          const currentCorrectIndex = fullQuestions[currentQuestionIndex]?.correctIndex;
          
          // Check if the answer is correct
          const isCorrect = selectedAnswers[currentQuestionIndex] === currentCorrectIndex;
          console.log(`Answer checked: ${isCorrect ? 'Correct!' : 'Incorrect'}`);
          console.log(`Selected: ${selectedAnswers[currentQuestionIndex]}, Correct: ${currentCorrectIndex}`);
          
          if (isCorrect) {
            correctCount++;
          }
          
          // Set quiz results (partial) to enable highlighting
          setQuizResults({
            userId,
            chapterId: selectedChapter?.id || '',
            correct: correctCount,
            total: fullQuestions.length,
            percentage: (correctCount / fullQuestions.length) * 100,
            userAnswers: selectedAnswers,
            questions: fullQuestions // Include full questions with correct answers
          });
          
          // Show the explanation
          console.log("Setting explanation:", fullQuestions[currentQuestionIndex]?.explanation);
        }
      } else {
        console.error("No stored questions found for chapter:", selectedChapter?.id);
      }
      
      // Mark this question as answered
      setQuestionAnswered(true);
      
      // If this is the last question, submit the quiz after a delay
      if (isLastQuestion) {
        setTimeout(async () => {
          await handleSubmitQuiz();
        }, 1500);
      }
    } catch (error) {
      console.error('Error checking answer:', error);
      setQuestionAnswered(true);
    }
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
      
      // Now that the quiz is scored, we can safely store the complete questions with answers
      if (results.questions) {
        setCompleteQuestions(results.questions);
      }
      
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
              {currentQuestion.options.map((option, index) => {
                // Determine if this option is correct or incorrect
                let optionClass = "";
                
                if (selectedAnswers[currentQuestionIndex] === index) {
                  optionClass = "selected";
                  
                  if (questionAnswered && quizResults && quizResults.questions) {
                    const correctIndex = quizResults.questions[currentQuestionIndex]?.correctIndex;
                    if (correctIndex !== undefined) {
                      optionClass += index === correctIndex ? " correct" : " incorrect";
                    }
                  }
                } else if (questionAnswered && quizResults && quizResults.questions) {
                  const correctIndex = quizResults.questions[currentQuestionIndex]?.correctIndex;
                  if (correctIndex !== undefined && index === correctIndex) {
                    optionClass += " correct-answer";
                  }
                }
                
                return (
                  <div 
                    key={index}
                    className={`quiz-option ${optionClass}`}
                    onClick={() => handleSelectAnswer(index)}
                  >
                    <div className="option-letter">{LETTERS[index]}</div>
                    <div className="option-text">{option}</div>
                  </div>
                );
              })}
            </div>
            
            {questionAnswered && quizResults && quizResults.questions && quizResults.questions[currentQuestionIndex]?.explanation && (
              <div className="explanation">
                <strong>Explanation:</strong>
                <div>{quizResults.questions[currentQuestionIndex].explanation}</div>
              </div>
            )}
          </div>
          
          <div className="quiz-navigation">
            {!questionAnswered && !quizResults ? (
              <button 
                className="quiz-button next"
                disabled={selectedAnswers[currentQuestionIndex] === -1}
                onClick={handleCheckAnswer}
              >
                {isLastQuestion ? 'Submit Quiz' : 'Check Answer'} 
              </button>
            ) : !isLastQuestion ? (
              <button 
                className="quiz-button next"
                onClick={handleNextQuestion}
              >
                Next Question
              </button>
            ) : null}
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