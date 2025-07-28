import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import './SurveyPage.css';

// Interface defining the structure of survey response data
interface SurveyFormData {
  intendedMajor: string;
  majorReason: string;
  supportNeeds: string[];
  participationInterests: string[];
  workHours: string;
  potentialIssues: string[];
}

interface SurveyPageProps {
  onComplete?: () => void;
}

/**
 * SurveyPage Component
 * 
 * Renders a welcome survey for new St. John's University students.
 * Collects information about their academic goals, support needs,
 * participation interests, work schedule, and potential challenges.
 * 
 * The survey responses are stored in JSON format in AWS DynamoDB
 * associated with the user's account.
 */
const SurveyPage = ({ onComplete }: SurveyPageProps) => {
  const navigate = useNavigate();

  // State to manage form data for all survey questions
  const [formData, setFormData] = useState<SurveyFormData>({
    intendedMajor: '',
    majorReason: '',
    supportNeeds: [],
    participationInterests: [],
    workHours: '',
    potentialIssues: []
  });

  // State to handle loading and error states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handles input changes for text fields (questions 1a and 1b)
   */
  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  /**
   * Handles checkbox changes for multiple-answer questions (questions 2, 3, 5)
   * Manages arrays of selected options
   */
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>, fieldName: keyof SurveyFormData) => {
    const { value, checked } = e.target;
    const field = fieldName as 'supportNeeds' | 'participationInterests' | 'potentialIssues';
    
    setFormData(prev => ({
      ...prev,
      [field]: checked 
        ? [...(prev[field] as string[]), value]
        : (prev[field] as string[]).filter(item => item !== value)
    }));
  };

  /**
   * Handles radio button changes for single-answer questions (question 4)
   */
  const handleRadioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  /**
   * Submits the survey responses to the backend API
   * The responses are stored in JSON format in the AWS DynamoDB Users table
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Get the current user's ID from the auth service
      const userId = authService.getUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Prepare the survey data in JSON format as requested
      const surveyData = {
        userId,
        surveyResponses: {
          responses: formData,
          submittedAt: new Date().toISOString()
        }
      };

      // Send the survey data to the backend API endpoint
      // Use the local development server endpoint
      const response = await fetch('http://localhost:5001/api/survey', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authService.getAuthToken()}`
        },
        body: JSON.stringify(surveyData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to submit survey');
      }

      const result = await response.json();
      console.log('Survey submitted successfully to DynamoDB:', result);

      // Also save to localStorage for immediate UI state updates
      await authService.saveSurveyResponses({
        responses: formData,
        submittedAt: new Date().toISOString()
      });

      // Call the completion callback or navigate to the main app
      if (onComplete) {
        onComplete();
      } else {
        navigate('/');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit survey');
      console.error('Survey submission error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="survey-page-container">
      <div className="survey-header">
        <h1>Welcome to St. John's University in NYC</h1>
        <p>Please take a few minutes to answer these questions to help us better support your academic journey.</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="survey-form">
        {/* Question 1: Intended Major and Reason */}
        <div className="question-section">
          <label htmlFor="intendedMajor" className="question-label">
            1. What is your intended major?
          </label>
          <input
            type="text"
            id="intendedMajor"
            name="intendedMajor"
            value={formData.intendedMajor}
            onChange={handleTextChange}
            required
            className="text-input"
            placeholder="Enter your intended major"
          />
          
          <label htmlFor="majorReason" className="question-label">
            Why?
          </label>
          <textarea
            id="majorReason"
            name="majorReason"
            value={formData.majorReason}
            onChange={handleTextChange}
            required
            className="text-area"
            placeholder="Explain why you chose this major"
            rows={3}
          />
        </div>

        {/* Question 2: Support Needs (Multiple Choice) */}
        <div className="question-section">
          <fieldset>
            <legend className="question-label">
              2. Where do you think you might need some support? (Select all that apply)
            </legend>
            <div className="checkbox-group">
              {[
                'Writing composition/Reading comprehension',
                'Math skills',
                'Science skills',
                'Time management',
                'Study skills',
                'Other',
                "I don't feel I need support at this time"
              ].map((option) => (
                <label key={option} className="checkbox-label">
                  <input
                    type="checkbox"
                    value={option}
                    checked={formData.supportNeeds.includes(option)}
                    onChange={(e) => handleCheckboxChange(e, 'supportNeeds')}
                  />
                  {option}
                </label>
              ))}
            </div>
          </fieldset>
        </div>

        {/* Question 3: Participation Interests (Multiple Choice) */}
        <div className="question-section">
          <fieldset>
            <legend className="question-label">
              3. Which of the following would you consider participating in? (Select all that apply)
            </legend>
            <div className="checkbox-group">
              {[
                'Intramural sports',
                'Student functions (concerts, sporting events, lectures)',
                'Student organizations',
                'Volunteer activities',
                'Student worker program',
                'Other'
              ].map((option) => (
                <label key={option} className="checkbox-label">
                  <input
                    type="checkbox"
                    value={option}
                    checked={formData.participationInterests.includes(option)}
                    onChange={(e) => handleCheckboxChange(e, 'participationInterests')}
                  />
                  {option}
                </label>
              ))}
            </div>
          </fieldset>
        </div>

        {/* Question 4: Work Hours (Single Choice) */}
        <div className="question-section">
          <fieldset>
            <legend className="question-label">
              4. How many hours of employment do you work each week? (Select one)
            </legend>
            <div className="radio-group">
              {[
                '1-5 hours',
                '6-10',
                '10-15',
                'over 15',
                "I don't have outside employment"
              ].map((option) => (
                <label key={option} className="radio-label">
                  <input
                    type="radio"
                    name="workHours"
                    value={option}
                    checked={formData.workHours === option}
                    onChange={handleRadioChange}
                    required
                  />
                  {option}
                </label>
              ))}
            </div>
          </fieldset>
        </div>

        {/* Question 5: Potential Issues (Multiple Choice) */}
        <div className="question-section">
          <fieldset>
            <legend className="question-label">
              5. Please select the areas you might have issues with during your current year here at SJU. (Select all that apply)
            </legend>
            <div className="checkbox-group">
              {[
                'Health issues',
                'Financial issues',
                'Personal relationships',
                'Living situation',
                'Keeping up with the academics',
                'Other',
                "I don't foresee any issues now"
              ].map((option) => (
                <label key={option} className="checkbox-label">
                  <input
                    type="checkbox"
                    value={option}
                    checked={formData.potentialIssues.includes(option)}
                    onChange={(e) => handleCheckboxChange(e, 'potentialIssues')}
                  />
                  {option}
                </label>
              ))}
            </div>
          </fieldset>
        </div>

        {/* Submit Button */}
        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? 'Submitting...' : 'Complete Survey'}
        </button>
      </form>
    </div>
  );
};

export default SurveyPage;