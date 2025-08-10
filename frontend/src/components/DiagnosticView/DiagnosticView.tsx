import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LineChart from '../LineChart/LineChart';
import diagnosticService from '../../services/diagnosticService';
import {
  UserProfile,
  ProgressMetrics,
  TaskItem,
  Achievement,
  ImportantDate,
  Announcement,
  Resource
} from '../../types';
import './DiagnosticView.css';

/**
 * DiagnosticView Component
 * 
 * A dashboard-style view that displays various academic metrics, progress data,
 * and resources for the student. It uses mock data currently, but is designed
 * to be connected to a backend that provides real student data.
 * 
 * The component is divided into several card sections, each displaying different
 * types of information:
 * - Student profile
 * - Academic progress visualization
 * - Tasks and assignments
 * - Knowledge checks
 * - Achievements
 * - Important course dates
 * - Announcements
 * - Educational resources
 * 
 * @component
 * @example
 * return (
 *   <DiagnosticView />
 * )
 */
const DiagnosticView: React.FC = () => {
  // User profile data
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  
  // Academic progress metrics for charts
  const [progressMetrics, setProgressMetrics] = useState<ProgressMetrics | null>(null);
  
  // Upcoming and current tasks
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  
  // Student achievements/badges
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  
  // Important academic dates
  const [importantDates, setImportantDates] = useState<ImportantDate[]>([]);
  
  // Course announcements
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  
  // Educational resources and links
  const [resources, setResources] = useState<Resource[]>([]);
  
  // Loading state for API calls
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  // Navigation hook
  const navigate = useNavigate();

  /**
   * Fetches all diagnostic data on component mount
   * 
   * Currently uses mock data from diagnosticService, but designed
   * to be replaced with actual API calls to the backend
   * 
   * TODO: Implement real API integration with proper error handling
   * - Add authentication tokens to requests
   * - Add retry logic for failed requests
   * - Add refresh mechanism for periodic data updates
   */
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Fetch all required data
        // These calls will eventually be to real endpoints
        
        const profile = await diagnosticService.getUserProfile();
        if (profile) setUserProfile(profile);

        const progress = await diagnosticService.getProgressMetrics();
        if (progress) setProgressMetrics(progress);

        const taskList = await diagnosticService.getTasks();
        setTasks(taskList);

        const achievementList = await diagnosticService.getAchievements();
        setAchievements(achievementList);

        const datesList = await diagnosticService.getImportantDates();
        setImportantDates(datesList);

        const announcementsList = await diagnosticService.getAnnouncements();
        setAnnouncements(announcementsList);

        const resourcesList = await diagnosticService.getResources();
        setResources(resourcesList);
      } catch (error) {
        console.error('Error fetching diagnostic data:', error);
        // TODO: Implement proper error handling UI
        // - Show error messages for specific failures
        // - Add retry options
        // - Fall back to cached data if available
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  /**
   * Formats a date object into a human-readable string
   * 
   * @param dateString - The date to format
   * @returns Formatted date string (e.g., "Apr 15")
   */
  const formatDate = (dateString: Date): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // No longer needed since we removed the simple knowledge check

  // Show loading indicator while data is being fetched
  if (isLoading) {
    return <div className="loading-container">Loading diagnostics data...</div>;
  }

  // No longer needed - route-based approach instead

  return (
    <div className="diagnostics-main">
      <div className="diagnostic-body">
        {/* Student Profile Card */}
        <div className="card profile-card">
          <h2>{userProfile?.name || 'Student'}</h2>
          <div>{userProfile?.school || 'School'}</div>
          <div>Credit Hours: {userProfile?.creditHours || 0}</div>
          <div>X Number: {userProfile?.xNumber?.substring(0, 4)}...</div>
          <div>
            <a href={`mailto:${userProfile?.email}`}>{userProfile?.email}</a>
          </div>
        </div>

        {/* Progress Chart Card */}
        <div className="card chart-card">
          <h4>Your Progress</h4>
          {/* 
            LineChart visualizes progress metrics over time
            TODO: Add more interactive chart options and filters
            TODO: Allow toggling between different metrics
          */}
          {progressMetrics?.trend && <LineChart data={progressMetrics.trend} />}
        </div>

        {/* Tasks List Card */}
        <div className="card tasks-card">
          <h4>Next Up:</h4>
          <ul className="list-items">
            {tasks.map((task) => (
              <li key={task.id} className={task.completed ? 'completed' : ''}>
                <div className="task-item">
                  <span className={`priority-dot ${task.priority}`}></span>
                  <span className="task-title">{task.title}</span>
                  {task.dueDate && (
                    <span className="due-date">Due: {formatDate(task.dueDate)}</span>
                  )}
                </div>
              </li>
            ))}
            {tasks.length === 0 && <li>No tasks available</li>}
          </ul>
          {/* 
            TODO: Implement task completion toggling
            TODO: Add task filtering options
            TODO: Add ability to create new tasks
          */}
        </div>

        {/* Knowledge Check Card */}
        <div className="card knowledge-card">
          <h4>Knowledge Check:</h4>
          
          <div style={{ padding: '20px 0', textAlign: 'center' }}>
            <p style={{ marginBottom: '20px' }}>
              Test your understanding with chapter quizzes.
              Each quiz contains 10 multiple choice questions to help you
              gauge your knowledge.
            </p>
            
            <button 
              className="submit-button" 
              style={{ 
                width: '150px', 
                padding: '12px 0',
                fontSize: '16px',
                fontWeight: 'bold',
                margin: '0 auto'
              }}
              onClick={() => navigate('/diagnostics/chapters')}
            >
              Start
            </button>
          </div>
        </div>

        {/* Achievements Card */}
        <div className="card achievements-card">
          <h4>Your Achievements</h4>
          <div className="icon-case">
            {achievements.map((achievement) => (
              <div
                key={achievement.id}
                className={`circle-icon ${!achievement.isActive ? 'inactive' : ''}`}
                title={achievement.title}
              >
                <i className={`bi bi-${achievement.icon}`}></i>
              </div>
            ))}
          </div>
          {/* 
            TODO: Add achievement details on hover/click
            TODO: Add progress indicators for incomplete achievements
            TODO: Implement achievement unlocking animations
          */}
        </div>

        {/* Important Dates Card */}
        <div className="card dates-card">
          <h4>Important Dates for LST1000:</h4>
          {importantDates.map((date) => (
            <div key={date.id} className="important-date">
              {formatDate(date.date)}: {date.title}
            </div>
          ))}
          {/* 
            TODO: Add calendar integration
            TODO: Implement date reminders
            TODO: Add ability to filter dates by category
          */}
        </div>

        {/* Announcements Card */}
        <div className="card announcements-card">
          <h4>Announcements</h4>
          {announcements.length > 0 ? (
            <div className="announcement">
              <h5>{announcements[0].title}</h5>
              <p>{announcements[0].body}</p>
              <div className="announcement-date">Posted: {formatDate(announcements[0].date)}</div>
            </div>
          ) : (
            <p>No announcements at this time.</p>
          )}
          {/* 
            TODO: Add pagination for multiple announcements
            TODO: Implement filtering by category/importance
            TODO: Add read/unread status tracking
          */}
        </div>

        {/* Resources Card */}
        <div className="card resources-card">
          <h4>Resources</h4>
          
          {/* University Resources */}
          <div className="resource-category">
            <h5>University</h5>
            <div className="resources-list">
              {resources
                .filter(resource => resource.category === 'university')
                .map((resource) => (
                  <div key={resource.id} className="resource-item">
                    <a href={resource.url} target="_blank" rel="noopener noreferrer">
                      {resource.title}
                    </a>
                  </div>
                ))
              }
            </div>
          </div>
          
          {/* Academic Resources */}
          {resources.filter(resource => resource.category === 'academic').length > 0 && (
            <div className="resource-category">
              <h5>Academic</h5>
              <div className="resources-list">
                {resources
                  .filter(resource => resource.category === 'academic')
                  .map((resource) => (
                    <div key={resource.id} className="resource-item">
                      <a href={resource.url} target="_blank" rel="noopener noreferrer">
                        {resource.title}
                      </a>
                    </div>
                  ))
                }
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DiagnosticView;