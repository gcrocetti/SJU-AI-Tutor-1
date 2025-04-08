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
  TextEvaluation
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
  private getDefaultChapters(userId: string): Chapter[] {
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
   * @returns Promise resolving to array of QuizQuestions
   */
  async generateQuizQuestions(chapterId: string, numQuestions: number = 10): Promise<QuizQuestion[]> {
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
          return result.data.questions;
        } else {
          // Fallback to mock data in case of issues
          console.warn('No questions data in response, using mock data');
          return this.getMockQuestions(chapterId);
        }
      } catch (apiError) {
        console.error('API error:', apiError);
        console.warn('Using mock data due to API error');
        return this.getMockQuestions(chapterId);
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
   * @param questions - Array of quiz questions with correct answers
   * @returns Promise resolving to QuizResult
   */
  async scoreQuiz(
    userId: string,
    chapterId: string,
    answers: number[],
    questions: QuizQuestion[]
  ): Promise<QuizResult> {
    try {
      console.log(`Scoring quiz for user ${userId}, chapter ${chapterId}`);
      
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
          return {
            userId,
            chapterId,
            correct: result.data.quiz_result.correct,
            total: result.data.quiz_result.total,
            percentage: result.data.quiz_result.percentage,
            userAnswers: answers,
            bestScores: result.data.quiz_result.best_scores || {},
            attemptCounts: result.data.quiz_result.attempt_counts || {}
          };
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
    
    return {
      userId,
      chapterId,
      correct,
      total,
      percentage,
      userAnswers: answers,
      bestScores: {
        'chapter-1': 90,
        'chapter-2': 75,
        'chapter-3': 80,
        [chapterId]: Math.max(percentage, this.getMockBestScore(chapterId))
      },
      attemptCounts: {
        'chapter-1': 2,
        'chapter-2': 1,
        'chapter-3': 1,
        [chapterId]: this.getMockAttemptCount(chapterId) + 1
      }
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
    prompt: string,
    response: string
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
    const scores: Record<string, number> = {
      'chapter-1': 90,
      'chapter-2': 75,
      'chapter-3': 80,
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
    const counts: Record<string, number> = {
      'chapter-1': 2,
      'chapter-2': 1,
      'chapter-3': 1,
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
    let topic = '';
    
    switch (chapterId) {
      case 'chapter-1':
        topic = 'Introduction to Computer Science';
        break;
      case 'chapter-2':
        topic = 'Data Structures';
        break;
      case 'chapter-3':
        topic = 'Object-Oriented Programming';
        break;
      case 'chapter-4':
        topic = 'Web Development';
        break;
      case 'chapter-5':
        topic = 'Databases';
        break;
      case 'chapter-6':
        topic = 'Computer Networks';
        break;
      case 'chapter-7':
        topic = 'Software Engineering';
        break;
      case 'chapter-8':
        topic = 'AI and Machine Learning';
        break;
      case 'chapter-9':
        topic = 'Operating Systems';
        break;
      case 'chapter-10':
        topic = 'Modern Development Tools';
        break;
      default:
        topic = 'Computer Science';
    }
    
    return [
      {
        question: `What is the primary purpose of ${topic}?`,
        options: [
          `To organize and process data efficiently`,
          `To create user interfaces`,
          `To design hardware components`,
          `To write documentation`
        ],
        correctIndex: 0,
        explanation: `${topic} primarily focuses on organizing and processing data efficiently to solve complex problems.`
      },
      {
        question: `Which of the following is NOT typically associated with ${topic}?`,
        options: [
          `Algorithms`,
          `Data structures`,
          `Hardware design`,
          `Problem solving`
        ],
        correctIndex: 2,
        explanation: `Hardware design is typically part of computer engineering, not ${topic}.`
      },
      {
        question: `What is a key benefit of understanding ${topic}?`,
        options: [
          `Increased ability to debug complex systems`,
          `Higher salary potential`,
          `Reduced need for team collaboration`,
          `Lower hardware costs`
        ],
        correctIndex: 0,
        explanation: `Understanding ${topic} greatly enhances your ability to debug and troubleshoot complex systems.`
      },
      {
        question: `Which field is most closely related to ${topic}?`,
        options: [
          `Mathematics`,
          `Biology`,
          `Marketing`,
          `Literature`
        ],
        correctIndex: 0,
        explanation: `${topic} is most closely related to mathematics, as both involve logical thinking and abstract problem-solving.`
      },
      {
        question: `What is a common challenge when working with ${topic}?`,
        options: [
          `Scalability issues`,
          `Limited application domains`,
          `Excessive simplicity`,
          `Too much standardization`
        ],
        correctIndex: 0,
        explanation: `Scalability is often a significant challenge in ${topic} as systems grow in complexity and size.`
      },
      {
        question: `In ${topic}, what does the term "abstraction" most closely refer to?`,
        options: [
          `Hiding implementation details`,
          `Creating virtual reality`,
          `Working remotely`,
          `Abstract art`
        ],
        correctIndex: 0,
        explanation: `In ${topic}, abstraction refers to hiding implementation details to manage complexity and focus on relevant aspects.`
      },
      {
        question: `Which programming paradigm is most associated with ${topic}?`,
        options: [
          `Object-oriented programming`,
          `Financial modeling`,
          `Literary analysis`,
          `Mechanical engineering`
        ],
        correctIndex: 0,
        explanation: `Object-oriented programming is commonly associated with ${topic} as it provides structured approaches to software development.`
      },
      {
        question: `What is NOT a common career path for someone studying ${topic}?`,
        options: [
          `Software developer`,
          `Systems analyst`,
          `Mechanical engineer`,
          `Data scientist`
        ],
        correctIndex: 2,
        explanation: `Mechanical engineering is not typically a direct career path from studying ${topic} as it involves different fundamental principles and training.`
      },
      {
        question: `Which tool is most commonly used in ${topic}?`,
        options: [
          `Integrated Development Environments (IDEs)`,
          `Hammers and screwdrivers`,
          `Microscopes`,
          `Paint brushes`
        ],
        correctIndex: 0,
        explanation: `IDEs are essential tools in ${topic} for writing, testing, and debugging code efficiently.`
      },
      {
        question: `What is a fundamental concept in ${topic}?`,
        options: [
          `Algorithms`,
          `Poetry`,
          `Cooking techniques`,
          `Fashion design`
        ],
        correctIndex: 0,
        explanation: `Algorithms are fundamental to ${topic}, providing step-by-step procedures for solving problems efficiently.`
      }
    ];
  }
}

// Create a singleton instance
export const diagnosticsService = new DiagnosticsService();
export default diagnosticsService;