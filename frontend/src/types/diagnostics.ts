/**
 * Diagnostics-related Types
 * 
 * This file contains types related to student diagnostics, progress tracking,
 * and learning resources. These types support the diagnostics dashboard and
 * related features.
 */

/**
 * User Profile Type
 * 
 * Represents information about the student using the system.
 * Used for personalization and tracking.
 */
export interface UserProfile {
  /** Unique identifier for the user */
  id: string;
  /** User's full name */
  name: string;
  /** User's email address */
  email: string;
  /** School or department */
  school: string;
  /** Number of credit hours */
  creditHours: number;
  /** University ID number */
  xNumber: string;
  /** User role in the system */
  role: 'student' | 'faculty' | 'admin';
  /** Optional user preferences */
  preferences?: Record<string, any>;
}

/**
 * Progress Data Point Type
 * 
 * Represents a single data point in a progress timeline.
 * Used for charting and visualizations.
 */
export interface ProgressData {
  /** Time period (typically a month) */
  date: string;
  /** First metric series (e.g., attendance) */
  series1: number;
  /** Second metric series (e.g., participation) */
  series2: number;
  /** Third metric series (e.g., performance) */
  series3: number;
  /** Optional total number of users for comparison */
  totalUsers?: number;
}

/**
 * Progress Metrics Type
 * 
 * Represents overall academic progress across different metrics.
 * Used for dashboards and progress tracking.
 */
export interface ProgressMetrics {
  /** Overall progress score (0-100) */
  overall: number;
  /** Progress scores by category */
  byCategory: Record<string, number>;
  /** Historical trend data for charting */
  trend: ProgressData[];
}

/**
 * Task Item Type
 * 
 * Represents a task, assignment, or to-do item.
 * Used for task lists and planning.
 */
export interface TaskItem {
  /** Unique identifier for the task */
  id: string;
  /** Task title/description */
  title: string;
  /** Optional due date */
  dueDate?: Date;
  /** Whether the task has been completed */
  completed: boolean;
  /** Task priority level */
  priority: 'low' | 'medium' | 'high';
  /** Task category for grouping */
  category: string;
}

/**
 * Knowledge Check Question Type
 * 
 * Represents a quiz question for knowledge assessment.
 * Used for interactive learning and progress tracking.
 */
export interface KnowledgeCheckQuestion {
  /** Unique identifier for the question */
  id: string;
  /** The question text */
  question: string;
  /** Array of possible answers */
  options: string[];
  /** Index of the correct answer in the options array */
  correctAnswer: number;
  /** Difficulty level */
  difficulty: 'easy' | 'medium' | 'hard';
  /** Subject category */
  category: string;
  /** Optional explanation for the answer */
  explanation?: string;
}

/**
 * Quiz Question Type
 * 
 * Enhanced question type for the multi-question knowledge check quizzes.
 */
export interface QuizQuestion {
  /** The question text */
  question: string;
  /** Array of possible answers */
  options: string[];
  /** Index of the correct answer in the options array (0-based) 
   * This will only be available on the server side or after submission
   */
  correctIndex?: number;
  /** Explanation of why the answer is correct */
  explanation?: string;
}

/**
 * Frontend Quiz Question Type
 * 
 * Version of question without correct answers for initial display
 */
export interface FrontendQuizQuestion {
  /** Unique ID for the question */
  id: string;
  /** The question text */
  question: string;
  /** Array of possible answers */
  options: string[];
}

/**
 * Quiz Result Type
 * 
 * Represents the results of a completed quiz.
 */
export interface QuizResult {
  /** User ID who took the quiz */
  userId: string;
  /** Chapter ID for the quiz */
  chapterId: string;
  /** Number of correct answers */
  correct: number;
  /** Total number of questions */
  total: number;
  /** Percentage score (0-100) */
  percentage: number;
  /** Array of the user's answer indices */
  userAnswers: number[];
  /** User's best scores by chapter */
  bestScores?: Record<string, number>;
  /** Number of attempts by chapter */
  attemptCounts?: Record<string, number>;
  /** Full quiz questions with correct answers (only available after submission) */
  questions?: QuizQuestion[];
}

/**
 * Chapter Type
 * 
 * Represents a course chapter for knowledge checks.
 */
export interface Chapter {
  /** Unique identifier for the chapter */
  id: string;
  /** Chapter title */
  title: string;
  /** Brief description of chapter contents */
  description: string;
  /** Best score achieved (0-100) */
  bestScore?: number;
  /** Number of attempts made */
  attempts?: number;
}

/**
 * Text Evaluation Type
 * 
 * Represents the evaluation of a free-form text response.
 */
export interface TextEvaluation {
  /** Individual scores by category */
  scores: {
    /** Accuracy of information (0-3) */
    accuracy: number;
    /** Depth of understanding (0-3) */
    depth: number;
    /** Clarity of expression (0-2) */
    clarity: number;
    /** Application of concepts (0-2) */
    application: number;
  };
  /** Total score (0-10) */
  totalScore: number;
  /** Feedback text */
  feedback: string;
}

/**
 * Achievement Type
 * 
 * Represents a student achievement or badge.
 * Used for gamification and progress recognition.
 */
export interface Achievement {
  /** Unique identifier for the achievement */
  id: string;
  /** Achievement name */
  title: string;
  /** Detailed description of how to earn it */
  description: string;
  /** Icon name (Bootstrap Icons identifier) */
  icon: string;
  /** When the achievement was earned (undefined if not yet earned) */
  dateEarned?: Date;
  /** Whether the achievement is active/earned */
  isActive: boolean;
}

/**
 * Important Date Type
 * 
 * Represents an important academic date or deadline.
 * Used for calendars and planning.
 */
export interface ImportantDate {
  /** Unique identifier for the date */
  id: string;
  /** When the event occurs */
  date: Date;
  /** Brief title of the event */
  title: string;
  /** Detailed description */
  description: string;
}

/**
 * Announcement Type
 * 
 * Represents a course or system announcement.
 * Used for notifications and updates.
 */
export interface Announcement {
  /** Unique identifier for the announcement */
  id: string;
  /** Announcement title */
  title: string;
  /** Full announcement content */
  body: string;
  /** When the announcement was posted */
  date: Date;
  /** Importance level */
  priority: 'low' | 'medium' | 'high';
}

/**
 * Resource Type
 * 
 * Represents an educational resource or link.
 * Used for providing study materials and references.
 */
export interface Resource {
  /** Unique identifier for the resource */
  id: string;
  /** Resource title */
  title: string;
  /** Resource URL or location */
  url: string;
  /** Resource category for grouping */
  category: string;
  /** Optional detailed description */
  description?: string;
}

/**
 * Diagnostics State
 * 
 * Represents the complete state of the diagnostics view.
 * Used for managing UI state in components.
 */
export interface DiagnosticsState {
  /** User profile data */
  userProfile: UserProfile | null;
  /** Academic progress metrics */
  progress: ProgressMetrics | null;
  /** Task and assignment list */
  tasks: TaskItem[];
  /** Current knowledge check question */
  knowledgeCheck: KnowledgeCheckQuestion | null;
  /** User achievements */
  achievements: Achievement[];
  /** Important academic dates */
  importantDates: ImportantDate[];
  /** Course announcements */
  announcements: Announcement[];
  /** Educational resources */
  resources: Resource[];
  /** Whether data is being loaded */
  isLoading: boolean;
  /** Error message, if any */
  error: string | null;
}