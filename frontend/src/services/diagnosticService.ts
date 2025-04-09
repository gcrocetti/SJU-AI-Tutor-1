import { 
  UserProfile,
  ProgressMetrics,
  TaskItem,
  KnowledgeCheckQuestion,
  Achievement,
  ImportantDate,
  Announcement,
  Resource,
  ProgressData,
  QuizQuestion,
  QuizResult,
  Chapter,
  TextEvaluation,
  FrontendQuizQuestion
} from '../types';
import authService from './authService';

/**
 * DiagnosticsService
 * 
 * Service class for handling all diagnostics-related data operations.
 * Currently provides mock data, but designed to be connected to a
 * backend API in the future.
 * 
 * All methods return promises to simulate asynchronous API calls,
 * which will make the transition to real API calls smoother.
 */
export class DiagnosticsService {
  // API base URL
  private apiBaseUrl = 'http://localhost:5000/api';

  /**
   * Get the authentication headers for API requests
   * 
   * @returns Object with auth headers
   */
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    
    const token = authService.getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  }
  
  /**
   * Get the user profile information
   * 
   * @returns Promise resolving to UserProfile or null
   * 
   * TODO: Implement real API call with authentication
   */
  async getUserProfile(): Promise<UserProfile | null> {
    try {
      // Mock data - replace with actual API call
      return {
        id: '123',
        name: 'Jane Doe',
        email: 'jane.doe25@stjohns.edu',
        school: 'Tobin School of Business',
        creditHours: 10,
        xNumber: 'X######',
        role: 'student'
      };
    } catch (error) {
      console.error('Failed to fetch user profile', error);
      return null;
    }
  }
  
  /**
   * Get progress metrics for the student
   * 
   * @returns Promise resolving to ProgressMetrics or null
   * 
   * TODO: Implement real API call with progress tracking
   * TODO: Add filtering by time period, course, etc.
   */
  async getProgressMetrics(): Promise<ProgressMetrics | null> {
    try {
      // Generate mock progress data
      const trendData: ProgressData[] = [
        { date: "2024-01", series1: 10, series2: 30, series3: 20 },
        { date: "2024-02", series1: 40, series2: 20, series3: 50 },
        { date: "2024-03", series1: 30, series2: 50, series3: 40 },
        { date: "2024-04", series1: 60, series2: 40, series3: 80 },
        { date: "2024-05", series1: 90, series2: 70, series3: 100 }
      ];
      
      // Mock data - replace with actual API call
      return {
        overall: 76,
        byCategory: {
          attendance: 92,
          participation: 68,
          assignments: 85,
          exams: 72
        },
        trend: trendData
      };
    } catch (error) {
      console.error('Failed to fetch progress metrics', error);
      return null;
    }
  }
  
  /**
   * Get upcoming tasks and assignments
   * 
   * @returns Promise resolving to array of TaskItems
   * 
   * TODO: Implement real API call with task tracking
   * TODO: Add sorting, filtering, and pagination
   */
  async getTasks(): Promise<TaskItem[]> {
    try {
      // Mock data - replace with actual API call
      return [
        { id: '1', title: 'Read Chapter 3', dueDate: new Date(Date.now() + 86400000), completed: false, priority: 'high', category: 'reading' },
        { id: '2', title: 'Submit Assignment 2', dueDate: new Date(Date.now() + 2 * 86400000), completed: false, priority: 'high', category: 'assignment' },
        { id: '3', title: 'Group Discussion Post', dueDate: new Date(Date.now() + 3 * 86400000), completed: false, priority: 'medium', category: 'discussion' },
        { id: '4', title: 'Study for Quiz', dueDate: new Date(Date.now() + 5 * 86400000), completed: false, priority: 'medium', category: 'study' },
        { id: '5', title: 'Review Feedback', completed: false, priority: 'low', category: 'review' }
      ];
    } catch (error) {
      console.error('Failed to fetch tasks', error);
      return [];
    }
  }
  
  /**
   * Get knowledge check question
   * 
   * @returns Promise resolving to KnowledgeCheckQuestion or null
   * 
   * TODO: Implement real API call with question bank
   * TODO: Add adaptive difficulty based on student performance
   */
  async getKnowledgeCheck(): Promise<KnowledgeCheckQuestion | null> {
    try {
      // Mock data - replace with actual API call
      return {
        id: '1',
        question: 'Which of the following is an example of an adverb?',
        options: ['Quickly', 'Dog', 'Beautiful', 'Laptop'],
        correctAnswer: 0, // Index of the correct answer (Quickly)
        difficulty: 'easy',
        category: 'grammar'
      };
    } catch (error) {
      console.error('Failed to fetch knowledge check', error);
      return null;
    }
  }
  
  /**
   * Get student achievements
   * 
   * @returns Promise resolving to array of Achievements
   * 
   * TODO: Implement real API call with achievement tracking
   * TODO: Add progress tracking for in-progress achievements
   */
  async getAchievements(): Promise<Achievement[]> {
    try {
      // Mock data - replace with actual API call
      return [
        { id: '1', title: 'First Login', description: 'Logged in for the first time', icon: 'house-door', dateEarned: new Date(Date.now() - 10 * 86400000), isActive: true },
        { id: '2', title: 'First Assignment', description: 'Completed your first assignment', icon: 'gear', dateEarned: new Date(Date.now() - 8 * 86400000), isActive: true },
        { id: '3', title: 'Discussion Master', description: 'Posted in 5 discussions', icon: 'person', dateEarned: new Date(Date.now() - 5 * 86400000), isActive: true },
        { id: '4', title: 'Perfect Quiz', description: 'Got 100% on a quiz', icon: 'envelope', dateEarned: new Date(Date.now() - 3 * 86400000), isActive: true },
        { id: '5', title: 'Consistent Learner', description: 'Logged in for 5 consecutive days', icon: 'bell', dateEarned: new Date(Date.now() - 1 * 86400000), isActive: true },
        { id: '6', title: 'Resource Explorer', description: 'Accessed all available resources', icon: 'bookmark', dateEarned: undefined, isActive: false },
        { id: '7', title: 'Group Leader', description: 'Led a group discussion', icon: 'chat-dots', dateEarned: undefined, isActive: false },
        { id: '8', title: 'Essay Expert', description: 'Got an A on an essay', icon: 'camera', dateEarned: undefined, isActive: false }
      ];
    } catch (error) {
      console.error('Failed to fetch achievements', error);
      return [];
    }
  }
  
  /**
   * Get important academic dates
   * 
   * @returns Promise resolving to array of ImportantDates
   * 
   * TODO: Implement real API call with course calendar integration
   * TODO: Add filtering by course, date range, etc.
   */
  async getImportantDates(): Promise<ImportantDate[]> {
    try {
      // Mock data - replace with actual API call
      return [
        { id: '1', date: new Date('2024-04-15'), title: 'Midterm Exam', description: 'Comprehensive exam covering chapters 1-5' },
        { id: '2', date: new Date('2024-04-18'), title: 'Assignment Due', description: 'Final project proposal submission' },
        { id: '3', date: new Date('2024-04-20'), title: 'Guest Lecture', description: 'Industry expert presentation' },
        { id: '4', date: new Date('2024-04-29'), title: 'Group Presentation', description: 'Team presentations on assigned topics' },
        { id: '5', date: new Date('2024-05-02'), title: 'Research Paper Due', description: 'Submit final research paper' },
        { id: '6', date: new Date('2024-05-18'), title: 'Final Exam', description: 'Comprehensive final examination' }
      ];
    } catch (error) {
      console.error('Failed to fetch important dates', error);
      return [];
    }
  }
  
  /**
   * Get course announcements
   * 
   * @returns Promise resolving to array of Announcements
   * 
   * TODO: Implement real API call with LMS integration
   * TODO: Add filtering, pagination, and read status tracking
   */
  async getAnnouncements(): Promise<Announcement[]> {
    try {
      // Mock data - replace with actual API call
      return [
        {
          id: '1',
          title: 'Course Schedule Update',
          body: 'Please note that there has been a change to the course schedule. The guest lecture originally planned for April 10th has been moved to April 20th. Please update your calendars accordingly.',
          date: new Date(Date.now() - 2 * 86400000),
          priority: 'high'
        }
      ];
    } catch (error) {
      console.error('Failed to fetch announcements', error);
      return [];
    }
  }
  
  /**
   * Get educational resources
   * 
   * @returns Promise resolving to array of Resources
   * 
   * TODO: Implement real API call with content management system
   * TODO: Add categorization, search, and personalization
   */
  async getResources(): Promise<Resource[]> {
    try {
      return [
        // University Resources
        { id: '1', title: 'St. John\'s SignOn', url: 'https://signon.stjohns.edu', category: 'university' },
        { id: '2', title: 'Canvas', url: 'https://stjohns.instructure.com/', category: 'university' },
        { id: '3', title: 'Office of the Registrar', url: 'https://www.stjohns.edu/academics/office-registrar', category: 'university' },
        { id: '4', title: 'Campus Map', url: 'https://www.stjohns.edu/sites/default/files/uploads/140425_m1-9098_queens_campus_map.pdf', category: 'university' },
        { id: '5', title: 'Mission and Values', url: 'https://www.stjohns.edu/who-we-are/history-and-facts/our-mission-vision', category: 'university' },
        
        // Academic Resources
        { id: '6', title: 'University Libraries', url: 'https://www.stjohns.edu/libraries', category: 'academic' },
        { id: '7', title: 'Academic Calendar', url: 'https://www.stjohns.edu/academics/office-registrar/academic-calendar', category: 'academic' },
        { id: '8', title: 'Academic Support', url: 'https://www.stjohns.edu/who-we-are/leadership-and-administration/administrative-offices/office-provost/academic-support-services', category: 'academic' }
      ];
    } catch (error) {
      console.error('Failed to fetch resources', error);
      return [];
    }
  }
  
  /**
   * Submit an answer to a knowledge check question
   * 
   * @param questionId - ID of the question being answered
   * @param answerIndex - Index of the selected answer
   * @returns Promise resolving to boolean indicating if answer was correct
   * 
   * TODO: Implement real API call with answer verification
   * TODO: Add analytics tracking of student responses
   */
  async submitKnowledgeCheckAnswer(questionId: string, answerIndex: number): Promise<boolean> {
    try {
      console.log(`[MOCK] Submitting answer ${answerIndex} for question ${questionId}`);
      
      // Mock response - assume correct if it's option 0 (Quickly)
      return answerIndex === 0;
    } catch (error) {
      console.error('Failed to submit knowledge check answer', error);
      return false;
    }
  }

  /**
   * Get available chapters for quizzes
   * 
   * @returns Promise resolving to array of Chapters
   */
  async getChapters(): Promise<Chapter[]> {
    try {
      // Try to get the authenticated user ID
      const userId = authService.getUserId() || '123'; // Fallback ID if not authenticated
      
      const query = JSON.stringify({
        message: JSON.stringify({
          action: 'get_chapters',
          user_id: userId
        })
      });
      
      try {
        // Call the Knowledge Check Agent API to get chapters with user stats
        const response = await fetch(`${this.apiBaseUrl}/agent/knowledge_check`, {
          method: 'POST',
          headers: this.getHeaders(),
          body: query
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Check if we have data in the response
        if (result.data && result.data.chapters) {
          return result.data.chapters;
        } else {
          // Fallback to default chapters
          console.warn('No chapters data in response, using default chapters');
          return this.getDefaultChapters(userId);
        }
      } catch (apiError) {
        console.error('API error:', apiError);
        console.warn('Using default chapters due to API error');
        return this.getDefaultChapters(userId);
      }
    } catch (error) {
      console.error('Failed to fetch chapters', error);
      return [];
    }
  }
  
  /**
   * Get default chapter list with mock user stats
   * 
   * @param userId - The user ID to get chapters for
   * @returns Array of Chapter objects
   */
  private getDefaultChapters(_userId: string): Chapter[] {
    // This would be replaced with real data in a production implementation
    return [
      { id: 'chapter-1', title: 'Introduction to Computer Science and Programming', description: 'Fundamentals of programming, algorithms, and computer systems.', bestScore: 90, attempts: 2 },
      { id: 'chapter-2', title: 'Basic Data Structures and Algorithms', description: 'Arrays, lists, stacks, queues, and basic search/sort algorithms.', bestScore: 75, attempts: 1 },
      { id: 'chapter-3', title: 'Object-Oriented Programming Principles', description: 'Classes, objects, inheritance, polymorphism, and encapsulation.', bestScore: 80, attempts: 1 },
      { id: 'chapter-4', title: 'Web Development Fundamentals', description: 'HTML, CSS, JavaScript, and web application architecture.', bestScore: 0, attempts: 0 },
      { id: 'chapter-5', title: 'Database Design and SQL', description: 'Relational databases, SQL queries, and database normalization.', bestScore: 0, attempts: 0 },
      { id: 'chapter-6', title: 'Computer Networks and Security', description: 'Network protocols, architecture, and security principles.', bestScore: 0, attempts: 0 },
      { id: 'chapter-7', title: 'Software Engineering Practices', description: 'Development methodologies, testing, version control, and deployment.', bestScore: 0, attempts: 0 },
      { id: 'chapter-8', title: 'Artificial Intelligence and Machine Learning Basics', description: 'Fundamental AI concepts and basic ML techniques.', bestScore: 0, attempts: 0 },
      { id: 'chapter-9', title: 'Operating Systems and Computer Architecture', description: 'CPU architecture, memory, processes, and operating system concepts.', bestScore: 0, attempts: 0 },
      { id: 'chapter-10', title: 'Modern Software Development Tools and Practices', description: 'DevOps, containers, cloud services, and modern development workflows.', bestScore: 0, attempts: 0 }
    ];
  }
  
  /**
   * Generate quiz questions for a chapter
   * 
   * @param chapterId - The chapter ID to generate questions for
   * @param numQuestions - Number of questions to generate (default: 10)
   * @returns Promise resolving to array of FrontendQuizQuestion (without correct answers)
   */
  async generateQuizQuestions(chapterId: string, numQuestions: number = 10): Promise<{ id: string; question: string; options: string[] }[]> {
    try {
      console.log(`Generating ${numQuestions} questions for chapter ${chapterId}`);
      
      const query = JSON.stringify({
        message: JSON.stringify({
          action: 'generate_questions',
          chapter_id: chapterId,
          num_questions: numQuestions
        })
      });
      
      try {
        // Call the Knowledge Check Agent API
        const response = await fetch(`${this.apiBaseUrl}/agent/knowledge_check`, {
          method: 'POST',
          headers: this.getHeaders(),
          body: query
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Check if we have data in the response
        if (result.data && result.data.questions) {
          // Store the full questions with answers in session storage
          // Log the questions for debugging
          console.log("Storing quiz questions:", result.data.questions);
          
          // Randomize option positions before storing
          const randomizedQuestions = this.randomizeOptionPositions(result.data.questions);
          console.log("Questions after randomization:", randomizedQuestions);
          
          // Store in session storage (base64 encoded for minimal obfuscation)
          const encodedData = btoa(JSON.stringify(randomizedQuestions));
          sessionStorage.setItem(`quiz_${chapterId}`, encodedData);
          
          // Verify storage worked by reading it back (debug only)
          try {
            const storedData = sessionStorage.getItem(`quiz_${chapterId}`);
            if (storedData) {
              const decodedData = JSON.parse(atob(storedData));
              console.log("Retrieved stored questions successfully:", decodedData);
            }
          } catch (e) {
            console.error("Failed to verify stored questions:", e);
          }
          
          // Return only the question text and options to the frontend (no correct answers)
          return randomizedQuestions.map((q: QuizQuestion, index: number): FrontendQuizQuestion => ({
            id: `${chapterId}_q${index}`,
            question: q.question,
            options: q.options
          }));
        } else {
          // Fallback to mock data in case of issues
          console.warn('No questions data in response, using mock data');
          const mockQuestions = this.getMockQuestions(chapterId);
          
          // Randomize option positions for mock questions
          const randomizedMockQuestions = this.randomizeOptionPositions(mockQuestions);
          console.log("Mock questions after randomization:", randomizedMockQuestions);
          
          // Store the randomized mock questions
          const encodedMockData = btoa(JSON.stringify(randomizedMockQuestions));
          sessionStorage.setItem(`quiz_${chapterId}`, encodedMockData);
          
          // Return frontend-safe version of randomized mock questions
          return randomizedMockQuestions.map((q, index): FrontendQuizQuestion => ({
            id: `${chapterId}_q${index}`,
            question: q.question,
            options: q.options
          }));
        }
      } catch (apiError) {
        console.error('API error:', apiError);
        console.warn('Using mock data due to API error');
        const mockQuestions = this.getMockQuestions(chapterId);
        
        // Randomize option positions for mock questions
        const randomizedMockQuestions = this.randomizeOptionPositions(mockQuestions);
        console.log("Mock questions after randomization (error case):", randomizedMockQuestions);
        
        // Store the randomized mock questions
        sessionStorage.setItem(
          `quiz_${chapterId}`, 
          btoa(JSON.stringify(randomizedMockQuestions))
        );
        
        // Return frontend-safe version of randomized questions
        return randomizedMockQuestions.map((q, index): FrontendQuizQuestion => ({
          id: `${chapterId}_q${index}`,
          question: q.question,
          options: q.options
        }));
      }
    } catch (error) {
      console.error('Failed to generate quiz questions', error);
      return [];
    }
  }
  
  /**
   * Score a completed quiz
   * 
   * @param userId - User ID
   * @param chapterId - Chapter ID
   * @param answers - Array of answer indices selected by the user
   * @param frontendQuestions - Array of frontend quiz questions (without correct answers)
   * @returns Promise resolving to QuizResult
   */
  async scoreQuiz(
    userId: string,
    chapterId: string,
    answers: number[],
    _frontendQuestions: { id: string; question: string; options: string[] }[]
  ): Promise<QuizResult> {
    try {
      console.log(`Scoring quiz for user ${userId}, chapter ${chapterId}`);
      
      // Retrieve the original questions with correct answers from session storage
      const storedQuestionsData = sessionStorage.getItem(`quiz_${chapterId}`);
      
      if (!storedQuestionsData) {
        throw new Error("Cannot find original quiz data. Please restart the quiz.");
      }
      
      // Decode and parse the stored questions
      const questions: QuizQuestion[] = JSON.parse(atob(storedQuestionsData));
      
      // Create the query for the API with the FULL questions (including correct answers)
      const query = JSON.stringify({
        message: JSON.stringify({
          action: 'score_quiz',
          user_id: userId,
          chapter_id: chapterId,
          answers: answers,
          questions: questions
        })
      });
      
      try {
        // Call the Knowledge Check Agent API
        const response = await fetch(`${this.apiBaseUrl}/agent/knowledge_check`, {
          method: 'POST',
          headers: this.getHeaders(),
          body: query
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Check if we have data in the response
        if (result.data && result.data.quiz_result) {
          // Also save the questions with correct answers for review
          const quizResults = {
            userId,
            chapterId,
            correct: result.data.quiz_result.correct,
            total: result.data.quiz_result.total,
            percentage: result.data.quiz_result.percentage,
            userAnswers: answers,
            bestScores: result.data.quiz_result.best_scores || {},
            attemptCounts: result.data.quiz_result.attempt_counts || {},
            questions: questions // Now we can include the full questions with correct answers
          };
          
          // The quiz is complete, so it's now safe to share the correct answers
          return quizResults;
        } else {
          // Fallback to local scoring if API doesn't return proper data
          console.warn('No quiz result data in response, scoring locally');
          return this.scoreQuizLocally(userId, chapterId, answers, questions);
        }
      } catch (apiError) {
        console.error('API error:', apiError);
        console.warn('Using local scoring due to API error');
        return this.scoreQuizLocally(userId, chapterId, answers, questions);
      }
    } catch (error) {
      console.error('Failed to score quiz', error);
      throw error;
    }
  }
  
  /**
   * Score a quiz locally (fallback method)
   * 
   * @param userId - User ID
   * @param chapterId - Chapter ID
   * @param answers - Array of answer indices selected by the user
   * @param questions - Array of quiz questions with correct answers
   * @returns QuizResult
   */
  private scoreQuizLocally(
    userId: string,
    chapterId: string,
    answers: number[],
    questions: QuizQuestion[]
  ): QuizResult {
    let correct = 0;
    const total = questions.length;
    
    for (let i = 0; i < answers.length; i++) {
      if (i < questions.length && answers[i] === questions[i].correctIndex) {
        correct++;
      }
    }
    
    const percentage = (correct / total) * 100;
    
    // Get current best score for this chapter
    const currentBestScore = this.getMockBestScore(chapterId);
    
    // Calculate new best score (if this attempt is better)
    const newBestScore = Math.max(percentage, currentBestScore);
    
    // Get current attempt count and increment by 1 for this attempt
    const currentAttemptCount = this.getMockAttemptCount(chapterId);
    const newAttemptCount = currentAttemptCount + 1;
    
    return {
      userId,
      chapterId,
      correct,
      total,
      percentage,
      userAnswers: answers,
      bestScores: {
        'chapter-1': 0,
        'chapter-2': 0,
        'chapter-3': 0,
        'chapter-4': 0,
        'chapter-5': 0,
        'chapter-6': 0,
        'chapter-7': 0,
        'chapter-8': 0,
        'chapter-9': 0,
        'chapter-10': 0,
        [chapterId]: newBestScore // The new best score for this chapter
      },
      attemptCounts: {
        'chapter-1': 0,
        'chapter-2': 0,
        'chapter-3': 0,
        'chapter-4': 0,
        'chapter-5': 0,
        'chapter-6': 0,
        'chapter-7': 0,
        'chapter-8': 0,
        'chapter-9': 0,
        'chapter-10': 0,
        [chapterId]: newAttemptCount // Incremented attempt count
      },
      questions: questions // Include the full questions with correct answers for review
    };
  }
  
  /**
   * Evaluate a text response to a knowledge check prompt
   * 
   * @param userId - User ID
   * @param topic - The topic being evaluated
   * @param prompt - The knowledge check prompt
   * @param response - The user's written response
   * @returns Promise resolving to TextEvaluation
   */
  async evaluateTextResponse(
    userId: string,
    topic: string,
    _prompt: string,
    _response: string
  ): Promise<TextEvaluation> {
    try {
      console.log(`Evaluating text response for user ${userId}, topic ${topic}`);
      
      // In a real implementation, this would call the Knowledge Check Agent
      // return this.callKnowledgeCheckAgent('evaluate_text', {
      //   user_id: userId,
      //   topic: topic,
      //   prompt: prompt,
      //   response: response
      // });
      
      // For now, return a mock evaluation
      return {
        scores: {
          accuracy: Math.floor(Math.random() * 4),
          depth: Math.floor(Math.random() * 4),
          clarity: Math.floor(Math.random() * 3),
          application: Math.floor(Math.random() * 3)
        },
        totalScore: 7,
        feedback: "Your response demonstrates good understanding of the core concepts. Consider providing more specific examples and explaining how the concepts apply to real-world situations."
      };
    } catch (error) {
      console.error('Failed to evaluate text response', error);
      throw error;
    }
  }
  
  // Helper methods for mock data
  
  private getMockBestScore(chapterId: string): number {
    // Set all initial best scores to 0 for all chapters
    const scores: Record<string, number> = {
      'chapter-1': 0,
      'chapter-2': 0,
      'chapter-3': 0,
      'chapter-4': 0,
      'chapter-5': 0,
      'chapter-6': 0,
      'chapter-7': 0,
      'chapter-8': 0,
      'chapter-9': 0,
      'chapter-10': 0
    };
    
    return scores[chapterId] || 0;
  }
  
  private getMockAttemptCount(chapterId: string): number {
    // Set all initial attempt counts to 0 for all chapters
    const counts: Record<string, number> = {
      'chapter-1': 0,
      'chapter-2': 0,
      'chapter-3': 0,
      'chapter-4': 0,
      'chapter-5': 0,
      'chapter-6': 0,
      'chapter-7': 0,
      'chapter-8': 0,
      'chapter-9': 0,
      'chapter-10': 0
    };
    
    return counts[chapterId] || 0;
  }
  
  private getMockQuestions(chapterId: string): QuizQuestion[] {
    // Generate 10 mock questions based on the chapter
    let questions: QuizQuestion[] = [];
    
    switch (chapterId) {
      case 'chapter-1': // Introduction to Computer Science
        questions = [
          {
            question: "Which of the following best describes an algorithm?",
            options: [
              "A step-by-step procedure for solving a problem",
              "A programming language created by Al Gore",
              "A hardware component that processes computations",
              "A type of mathematical equation"
            ],
            correctIndex: 0,
            explanation: "An algorithm is a well-defined, step-by-step procedure for solving a problem or accomplishing a task. Algorithms are fundamental to computer science as they define the logical sequence of operations needed to process data and produce desired outputs."
          },
          {
            question: "In computational thinking, what is decomposition?",
            options: [
              "Breaking down complex problems into smaller, more manageable parts",
              "The process of a computer shutting down",
              "Converting decimal numbers to binary",
              "Analyzing how quickly a program runs"
            ],
            correctIndex: 0,
            explanation: "Decomposition is the process of breaking down complex problems into smaller, more manageable parts. This is a key computational thinking skill that helps programmers tackle difficult problems by solving smaller sub-problems first."
          },
          {
            question: "What is the primary purpose of pseudocode?",
            options: [
              "To describe algorithms in a language-independent way",
              "To compile and execute programs faster",
              "To encrypt sensitive data in a program",
              "To document bugs in existing code"
            ],
            correctIndex: 0,
            explanation: "Pseudocode is used to describe algorithms in a language-independent way, allowing programmers to plan and communicate their logic without worrying about specific programming language syntax. It serves as a blueprint before actual coding begins."
          },
          {
            question: "Which of these is NOT a basic data type in most programming languages?",
            options: [
              "Database",
              "Integer",
              "Boolean",
              "String"
            ],
            correctIndex: 0,
            explanation: "Database is not a basic data type but rather a structured system for storing, managing, and retrieving data. The other options (Integer, Boolean, and String) are fundamental data types found in most programming languages."
          },
          {
            question: "Which control structure executes a block of code only if a specified condition is true?",
            options: [
              "Conditional statement (if-then-else)",
              "Loop statement (for, while)",
              "Function call",
              "Try-catch block"
            ],
            correctIndex: 0,
            explanation: "Conditional statements like if-then-else execute a block of code only when a specified condition evaluates to true. This allows programs to make decisions based on different conditions and execute different paths accordingly."
          },
          {
            question: "What is the binary representation of the decimal number 10?",
            options: [
              "1010",
              "1100",
              "1110",
              "1001"
            ],
            correctIndex: 0,
            explanation: "The decimal number 10 is represented as 1010 in binary. This conversion works by: 10 = 8 + 2 = 2^3 + 2^1 = 1010 in binary, where each 1 represents a power of 2 (reading right to left: 2^1 and 2^3)."
          },
          {
            question: "What is the main difference between compiled and interpreted programming languages?",
            options: [
              "Compiled languages translate all code to machine code before execution, while interpreted languages translate code line-by-line during execution",
              "Compiled languages are always faster than interpreted languages",
              "Interpreted languages always produce more efficient code",
              "Compiled languages are newer than interpreted languages"
            ],
            correctIndex: 0,
            explanation: "Compiled languages translate the entire source code to machine code before execution, creating an executable file, while interpreted languages translate and execute code line-by-line during runtime. This fundamental difference affects performance, portability, and debugging."
          },
          {
            question: "In programming, what is the purpose of a variable?",
            options: [
              "To store data values that can be used and modified throughout a program",
              "To vary the speed at which the program executes",
              "To create visual elements in a user interface",
              "To establish network connections between computers"
            ],
            correctIndex: 0,
            explanation: "Variables are named storage locations that hold data values which can be used and modified throughout a program. They allow programmers to work with data dynamically, storing and manipulating values during program execution."
          },
          {
            question: "Which of the following is an example of an infinite loop?",
            options: [
              "while (true) { // code block }",
              "for (int i = 0; i < 10; i++) { // code block }",
              "if (x > 5) { // code block }",
              "switch (value) { case 1: // code block }"
            ],
            correctIndex: 0,
            explanation: "The 'while (true)' statement creates an infinite loop because the condition always evaluates to true, causing the code block to execute repeatedly without termination. Infinite loops can cause programs to become unresponsive and typically need to be manually interrupted."
          },
          {
            question: "What does the acronym 'IDE' stand for in programming?",
            options: [
              "Integrated Development Environment",
              "Interactive Design Elements",
              "Internal Development Engine",
              "Indexed Data Exchange"
            ],
            correctIndex: 0,
            explanation: "IDE stands for Integrated Development Environment. IDEs like Visual Studio Code, Eclipse, and IntelliJ provide comprehensive tools for software development including code editors, debuggers, and build automation tools, making the development process more efficient."
          }
        ];
        break;
      case 'chapter-2': // Data Structures
        questions = [
          {
            question: "Which data structure operates on a Last-In-First-Out (LIFO) principle?",
            options: [
              "Stack",
              "Queue",
              "Linked List",
              "Binary Tree"
            ],
            correctIndex: 0,
            explanation: "A stack operates on the Last-In-First-Out (LIFO) principle, meaning the last element added is the first one to be removed. This is analogous to a stack of plates where you add and remove plates from the top. Common operations are push (add to top) and pop (remove from top)."
          },
          {
            question: "What is the time complexity of searching for an element in an unsorted array?",
            options: [
              "O(n)",
              "O(1)",
              "O(log n)",
              "O(n²)"
            ],
            correctIndex: 0,
            explanation: "Searching for an element in an unsorted array has a time complexity of O(n) because in the worst case, you might need to examine every element in the array before finding the target element or determining it doesn't exist."
          },
          {
            question: "Which of the following best describes a linked list?",
            options: [
              "A sequential collection of elements where each element points to the next element",
              "A collection of elements organized in rows and columns",
              "A collection of elements where each element has a unique key",
              "A collection of elements that follows the LIFO principle"
            ],
            correctIndex: 0,
            explanation: "A linked list is a sequential collection of elements called nodes, where each node contains data and a reference (or pointer) to the next node in the sequence. This structure allows for efficient insertion and deletion operations at any position."
          },
          {
            question: "What is the best-case time complexity of quicksort?",
            options: [
              "O(n log n)",
              "O(n)",
              "O(log n)",
              "O(n²)"
            ],
            correctIndex: 0,
            explanation: "The best-case time complexity of quicksort is O(n log n), which occurs when the pivot chosen at each step divides the array into roughly equal halves. This creates a balanced recursion tree with a height of log n, and at each level, we do O(n) work partitioning the array."
          },
          {
            question: "Which data structure would be most efficient for implementing a dictionary where keys are mapped to values?",
            options: [
              "Hash Table",
              "Array",
              "Linked List",
              "Stack"
            ],
            correctIndex: 0,
            explanation: "A Hash Table is most efficient for implementing a dictionary because it provides average-case O(1) time complexity for insertions, deletions, and lookups. Hash tables map keys to values using a hash function that converts keys into array indices."
          },
          {
            question: "What is the primary advantage of using a binary search over a linear search?",
            options: [
              "It has a better time complexity for sorted data",
              "It works on unsorted data",
              "It uses less memory",
              "It is easier to implement"
            ],
            correctIndex: 0,
            explanation: "The primary advantage of binary search is its superior time complexity of O(log n) compared to linear search's O(n). Binary search repeatedly divides the search space in half, making it much more efficient for large datasets, but it requires that the data be sorted first."
          },
          {
            question: "In Big O notation, what does O(1) represent?",
            options: [
              "Constant time complexity",
              "Linear time complexity",
              "Logarithmic time complexity",
              "Quadratic time complexity"
            ],
            correctIndex: 0,
            explanation: "O(1) represents constant time complexity, meaning the operation takes the same amount of time regardless of the input size. Examples include accessing an array element by index or inserting an element at the beginning of a linked list."
          },
          {
            question: "Which of the following data structures is most appropriate for implementing a breadth-first search algorithm?",
            options: [
              "Queue",
              "Stack",
              "Hash Table",
              "Heap"
            ],
            correctIndex: 0,
            explanation: "A Queue is most appropriate for implementing breadth-first search (BFS) because BFS explores all neighbors at the current depth before moving to nodes at the next depth level. The First-In-First-Out (FIFO) nature of queues naturally supports this level-by-level traversal."
          },
          {
            question: "What is a balanced binary search tree?",
            options: [
              "A tree where the height difference between left and right subtrees is minimal",
              "A tree with an equal number of nodes in all subtrees",
              "A tree where all leaf nodes are at the same level",
              "A tree with exactly the same structure on both sides"
            ],
            correctIndex: 0,
            explanation: "A balanced binary search tree is one where the height difference between the left and right subtrees of any node is kept minimal (typically defined by a specific balance factor). This balancing ensures operations like search, insert, and delete maintain logarithmic time complexity."
          },
          {
            question: "Which sorting algorithm has the same time complexity in best, average, and worst cases?",
            options: [
              "Merge Sort",
              "Quick Sort",
              "Bubble Sort",
              "Insertion Sort"
            ],
            correctIndex: 0,
            explanation: "Merge Sort has the same time complexity of O(n log n) in all cases (best, average, and worst). This consistency makes it reliable for sorting large datasets when the distribution of input is unknown, unlike Quick Sort which can degrade to O(n²) in worst cases."
          }
        ];
        break;
      case 'chapter-3': // Object-Oriented Programming
        questions = [
          {
            question: "Which of the following best describes encapsulation in OOP?",
            options: [
              "Bundling data and methods that operate on the data within a single unit",
              "Creating new classes from existing ones",
              "Having multiple implementations of the same method",
              "Hiding all data from outside users"
            ],
            correctIndex: 0,
            explanation: "Encapsulation in object-oriented programming refers to bundling data (attributes) and the methods that operate on that data within a single unit (class). It includes the concept of data hiding, where implementation details are hidden and access is restricted to preserve the integrity of the data."
          },
          {
            question: "What is inheritance in OOP?",
            options: [
              "A mechanism where a new class acquires properties and behaviors of an existing class",
              "The process of hiding implementation details",
              "The ability of an object to take many forms",
              "A technique for storing data in memory"
            ],
            correctIndex: 0,
            explanation: "Inheritance is a mechanism where a new class (subclass/derived class) acquires properties and behaviors of an existing class (superclass/base class). It promotes code reuse, establishes an 'is-a' relationship, and allows for hierarchical classification of objects."
          },
          {
            question: "What is polymorphism in object-oriented programming?",
            options: [
              "The ability of objects to take different forms or exhibit different behaviors based on context",
              "The process of creating multiple instances of the same class",
              "The technique of hiding object data from external access",
              "The practice of defining classes that inherit from multiple parent classes"
            ],
            correctIndex: 0,
            explanation: "Polymorphism is the ability of objects to take different forms or exhibit different behaviors based on context. In practical terms, it allows objects of different classes to be treated as objects of a common superclass, and method calls to be resolved at runtime rather than compile time."
          },
          {
            question: "What is a constructor in OOP?",
            options: [
              "A special method that initializes a newly created object",
              "A method that destroys objects when they are no longer needed",
              "A method that copies one object to another",
              "A special variable that contains object data"
            ],
            correctIndex: 0,
            explanation: "A constructor is a special method that is automatically called when an object is created from a class. Its primary purpose is to initialize the newly created object, setting initial values for attributes and performing any setup operations the object requires."
          },
          {
            question: "Which of the following is NOT one of the four main principles of OOP?",
            options: [
              "Multithreading",
              "Encapsulation",
              "Inheritance",
              "Polymorphism"
            ],
            correctIndex: 0,
            explanation: "Multithreading is not one of the four main principles of OOP. The four core principles are Encapsulation (bundling data and methods), Inheritance (acquiring properties from existing classes), Polymorphism (multiple forms), and Abstraction (simplifying complex reality by modeling classes)."
          },
          {
            question: "What is method overriding in OOP?",
            options: [
              "Providing a new implementation for a method in a subclass that is already defined in the superclass",
              "Defining multiple methods with the same name but different parameters in the same class",
              "Creating private methods that cannot be accessed outside the class",
              "Declaring methods that cannot be changed in subclasses"
            ],
            correctIndex: 0,
            explanation: "Method overriding is providing a new implementation for a method in a subclass that is already defined in the superclass. This allows a subclass to provide a specific implementation for a method that is already defined in its parent class, supporting polymorphism."
          },
          {
            question: "What does the 'this' keyword refer to in most OOP languages?",
            options: [
              "The current instance of the class",
              "The parent class",
              "The next object to be created",
              "The static class variables"
            ],
            correctIndex: 0,
            explanation: "The 'this' keyword refers to the current instance of the class - the object through which a method is being called or an attribute is being accessed. It helps differentiate between instance variables and parameters/local variables with the same name."
          },
          {
            question: "Which design pattern is used when you need to create objects without specifying their concrete classes?",
            options: [
              "Factory Method",
              "Singleton",
              "Observer",
              "Decorator"
            ],
            correctIndex: 0,
            explanation: "The Factory Method pattern is used when you need to create objects without specifying their concrete classes. It defines an interface for creating objects but lets subclasses decide which classes to instantiate, allowing for flexibility in object creation."
          },
          {
            question: "What is the purpose of an abstract class in OOP?",
            options: [
              "To provide a base class that cannot be instantiated but can be inherited from",
              "To create multiple instances of the same type",
              "To hide data from unauthorized access",
              "To ensure all classes have the same methods"
            ],
            correctIndex: 0,
            explanation: "An abstract class serves as a base class that cannot be instantiated directly but can be inherited from. It can contain a mix of concrete and abstract methods (methods without implementation), forcing subclasses to provide implementations for the abstract methods."
          },
          {
            question: "What is the difference between composition and inheritance in OOP?",
            options: [
              "Composition uses 'has-a' relationships while inheritance uses 'is-a' relationships",
              "Composition only works with abstract classes, while inheritance works with any class",
              "Inheritance allows method reuse but composition doesn't",
              "Composition is a Java-specific concept while inheritance is universal"
            ],
            correctIndex: 0,
            explanation: "Composition establishes 'has-a' relationships where an object contains other objects as parts, while inheritance establishes 'is-a' relationships where a subclass is a specialized version of a superclass. Composition is generally more flexible as it enables stronger encapsulation and allows changing behavior at runtime."
          }
        ];
        break;
      // Add other chapters as needed, following the same pattern
      default:
        // For other chapters, generate generic but plausible questions
        questions = [
          {
            question: `What is a key principle of ${chapterId.replace('-', ' ')}?`,
            options: [
              "Abstraction and modeling of real-world concepts",
              "Maximizing hardware usage at all costs",
              "Avoiding documentation and comments",
              "Writing code that only the original author can understand"
            ],
            correctIndex: 0,
            explanation: `Abstraction and modeling of real-world concepts is a fundamental principle in ${chapterId.replace('-', ' ')}. It allows complex systems to be represented in a simplified, manageable way that focuses on the essential features while hiding unnecessary details.`
          },
          {
            question: `Which of the following is considered a best practice in ${chapterId.replace('-', ' ')}?`,
            options: [
              "Writing clean, maintainable code with appropriate comments",
              "Creating as many global variables as possible",
              "Avoiding version control systems",
              "Duplicating code across multiple files"
            ],
            correctIndex: 0,
            explanation: `Writing clean, maintainable code with appropriate comments is a critical best practice in ${chapterId.replace('-', ' ')}. It improves readability, makes debugging easier, enables better collaboration, and reduces technical debt over time.`
          },
          {
            question: `What is a common challenge when implementing ${chapterId.replace('-', ' ')} concepts?`,
            options: [
              "Balancing performance with maintainability",
              "Finding enough monitors to display the code",
              "Convincing managers that code doesn't need testing",
              "Writing code that no one else can understand"
            ],
            correctIndex: 0,
            explanation: `Balancing performance with maintainability is a common challenge in ${chapterId.replace('-', ' ')}. Optimized code can sometimes be more complex and harder to maintain, requiring careful tradeoffs between runtime efficiency and developer productivity.`
          },
          {
            question: `In the context of ${chapterId.replace('-', ' ')}, what does "abstraction" mean?`,
            options: [
              "Simplifying complex systems by modeling classes appropriate to the problem",
              "Making code as abstract and confusing as possible",
              "Removing all comments from code",
              "Using only abstract data types"
            ],
            correctIndex: 0,
            explanation: `In ${chapterId.replace('-', ' ')}, abstraction refers to the process of simplifying complex systems by creating models that represent the essential features while hiding unnecessary implementation details. This makes systems easier to understand and work with at different levels of complexity.`
          },
          {
            question: `Which of these is NOT typically associated with ${chapterId.replace('-', ' ')}?`,
            options: [
              "Avoiding all forms of documentation",
              "Modular design",
              "Testing and validation",
              "Version control"
            ],
            correctIndex: 0,
            explanation: `Avoiding documentation is NOT associated with good ${chapterId.replace('-', ' ')} practices. Proper documentation is essential for maintaining software, onboarding new team members, and ensuring the long-term viability of a project.`
          },
          {
            question: `What is the main benefit of following ${chapterId.replace('-', ' ')} principles?`,
            options: [
              "Creating more maintainable, scalable, and robust software",
              "Impressing colleagues with complex code",
              "Reducing the need for testing",
              "Eliminating the need for documentation"
            ],
            correctIndex: 0,
            explanation: `Following ${chapterId.replace('-', ' ')} principles leads to creating more maintainable, scalable, and robust software. These principles have evolved from decades of industry experience and are designed to address common challenges in software development.`
          },
          {
            question: `What role does testing play in ${chapterId.replace('-', ' ')}?`,
            options: [
              "It verifies that software meets requirements and functions correctly",
              "It's an optional step that can be skipped to save time",
              "It's only necessary for critical systems",
              "It's only useful for inexperienced developers"
            ],
            correctIndex: 0,
            explanation: `Testing plays a crucial role in ${chapterId.replace('-', ' ')} by verifying that software meets its requirements and functions correctly. It helps identify bugs early, ensures quality, provides documentation, and builds confidence in the code's reliability.`
          },
          {
            question: `Which approach is recommended when designing systems in ${chapterId.replace('-', ' ')}?`,
            options: [
              "Start with high-level design before implementation details",
              "Start coding immediately and figure out the design later",
              "Copy existing code without understanding it",
              "Avoid planning to allow for maximum creativity"
            ],
            correctIndex: 0,
            explanation: `Starting with a high-level design before diving into implementation details is a recommended approach in ${chapterId.replace('-', ' ')}. This top-down approach helps ensure that the overall architecture is sound before resources are committed to specific implementations.`
          },
          {
            question: `What is "refactoring" in the context of ${chapterId.replace('-', ' ')}?`,
            options: [
              "Restructuring existing code without changing its external behavior",
              "Completely rewriting an application from scratch",
              "Removing all comments and documentation",
              "Adding unnecessary complexity to impress other developers"
            ],
            correctIndex: 0,
            explanation: `In ${chapterId.replace('-', ' ')}, refactoring is the process of restructuring existing code without changing its external behavior. It's done to improve non-functional attributes like readability, complexity, maintainability, or performance.`
          },
          {
            question: `How does ${chapterId.replace('-', ' ')} relate to problem-solving?`,
            options: [
              "It provides structured approaches to break down and solve complex problems",
              "It's unrelated to problem-solving",
              "It makes problems more complex intentionally",
              "It focuses exclusively on theoretical problems"
            ],
            correctIndex: 0,
            explanation: `${chapterId.replace('-', ' ')} provides structured approaches to break down and solve complex problems. It offers methodologies, patterns, and tools that help developers analyze problems, design solutions, and implement them effectively.`
          }
        ];
    }
    
    return questions;
  }
  
  /**
   * Randomize the positions of options in each question and update the correctIndex accordingly
   * 
   * @param questions - Array of quiz questions to randomize
   * @returns Array of questions with randomized option positions
   */
  private randomizeOptionPositions(questions: QuizQuestion[]): QuizQuestion[] {
    // Create a deep copy of the questions to avoid modifying the original
    const randomizedQuestions = JSON.parse(JSON.stringify(questions)) as QuizQuestion[];
    
    // Randomize each question's options
    randomizedQuestions.forEach(question => {
      if (!question.options || !Array.isArray(question.options) || question.correctIndex === undefined) {
        console.warn("Skipping randomization for invalid question:", question);
        return;
      }
      
      // Save the correct answer text based on the original correctIndex
      const correctAnswer = question.options[question.correctIndex];
      
      // Create an array of indices [0, 1, 2, 3] and shuffle it
      const newOrder = this.shuffleArray([0, 1, 2, 3]);
      
      // Rearrange options according to the new order
      const newOptions = newOrder.map(i => 
        i < question.options.length ? question.options[i] : null
      ).filter(Boolean) as string[];
      
      // Find where the correct answer ended up after shuffling
      const newCorrectIndex = newOptions.indexOf(correctAnswer);
      
      // Update the question with the new order
      question.options = newOptions;
      question.correctIndex = newCorrectIndex;
    });
    
    return randomizedQuestions;
  }
  
  /**
   * Shuffle an array using the Fisher-Yates algorithm
   * 
   * @param array - Array to shuffle
   * @returns Shuffled array
   */
  private shuffleArray<T>(array: T[]): T[] {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }
}

export const diagnosticsService = new DiagnosticsService();
export default diagnosticsService;