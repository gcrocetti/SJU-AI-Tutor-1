import { 
    UserProfile, 
    ProgressMetrics, 
    TaskItem,
    KnowledgeCheckQuestion,
    Achievement,
    ImportantDate,
    Announcement,
    Resource
  } from '../../types';
  
  export interface DiagnosticsViewProps {
    initialData?: {
      userProfile?: UserProfile;
      progressMetrics?: ProgressMetrics;
      tasks?: TaskItem[];
      knowledgeCheck?: KnowledgeCheckQuestion;
      achievements?: Achievement[];
      importantDates?: ImportantDate[];
      announcements?: Announcement[];
      resources?: Resource[];
    };
  }
  
  export interface UserProfileCardProps {
    userProfile: UserProfile;
  }
  
  export interface ProgressCardProps {
    progressMetrics: ProgressMetrics;
  }
  
  export interface TaskListCardProps {
    tasks: TaskItem[];
    onToggleTask?: (id: string, completed: boolean) => void;
  }
  
  export interface KnowledgeCheckCardProps {
    question: KnowledgeCheckQuestion;
    onSubmitAnswer: (questionId: string, answerIndex: number) => void;
  }
  
  export interface AchievementsCardProps {
    achievements: Achievement[];
  }
  
  export interface ImportantDatesCardProps {
    importantDates: ImportantDate[];
  }
  
  export interface AnnouncementsCardProps {
    announcements: Announcement[];
  }
  
  export interface ResourcesCardProps {
    resources: Resource[];
  }