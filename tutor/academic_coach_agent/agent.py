"""
Academic Coach Agent (Study & Organization Specialist)

This module implements an Academic Coach Agent that focuses on helping students develop 
effective study strategies, time management skills, and academic goals. It provides:

1. Personalized study plans based on learning styles and course load
2. Time management techniques and prioritization tools
3. Goal-setting guidance and progress tracking
4. Strategies for managing academic stress and maintaining motivation
5. Recommendations for effective study techniques tailored to specific subjects
"""

import json
import logging
import os
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

# Set up OpenAI - try to use real API first, fall back to mock if needed
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except (ImportError, Exception) as e:
    # Create a mock OpenAI client for development
    import unittest.mock as mock
    client = mock.MagicMock()
    
    # Configure mock to return reasonable responses
    def mock_completion(**kwargs):
        mock_resp = mock.MagicMock()
        mock_resp.choices = [mock.MagicMock()]
        mock_resp.choices[0].message = mock.MagicMock()
        
        # Create a sample response based on the prompt
        if any(kw in str(kwargs) for kw in ["study plan", "schedule", "time management"]):
            mock_resp.choices[0].message.content = """Here's a personalized study plan for you:

## Weekly Schedule
- Monday: 2-4pm - Computer Science (Focus: Data Structures)
- Tuesday: 3-5pm - Mathematics (Focus: Calculus)
- Wednesday: 2-4pm - Computer Science (Focus: Algorithms)
- Thursday: 3-5pm - Mathematics (Practice Problems)
- Friday: 2-4pm - Review and self-assessment

## Study Techniques
- Use active recall for theoretical concepts
- Implement code examples for programming topics
- Take breaks using the Pomodoro Technique (25min work, 5min break)
- Review material within 24 hours to improve retention

Would you like me to adjust this plan or provide more specific techniques for any subject?"""
        elif any(kw in str(kwargs) for kw in ["goal", "objective", "target"]):
            mock_resp.choices[0].message.content = """I've created a structured goal framework for you:

## Academic Goals
1. Short-term (2 weeks): Complete all practice problems for Chapter 3
   - Measure: 100% completion rate with 80%+ accuracy
   - Schedule: 30 minutes daily

2. Mid-term (1 month): Improve test scores by 15%
   - Measure: Compare next exam score to previous average
   - Strategy: Focused study on weak areas identified from knowledge checks

3. Long-term (semester): Achieve 3.7+ GPA
   - Measure: Final course grades
   - Strategy: Consistent weekly reviews and practice tests

Would you like to refine these goals or develop strategies for any specific one?"""
        else:
            mock_resp.choices[0].message.content = """I understand you're looking for academic coaching support. I can help you with:

1. Creating a personalized study plan
2. Developing effective time management strategies
3. Setting realistic academic goals
4. Managing academic stress and maintaining motivation
5. Recommending study techniques for specific subjects

What would you like to focus on today?"""
        
        return mock_resp
    
    # Set up the chat.completions.create method to use our mock function
    client.chat.completions.create = mock_completion
    print("WARNING: Using mock OpenAI client for development purposes.")

from .prompts import (
    SYSTEM_PROMPT,
    STUDY_PLAN_PROMPT,
    PROGRESS_ANALYSIS_PROMPT,
    GOAL_SETTING_PROMPT,
    TIME_MANAGEMENT_PROMPT,
    MOTIVATION_PROMPT
)

from .tools import (
    get_study_plan,
    save_study_plan,
    get_user_goals,
    add_user_goal,
    update_goal_progress,
    get_time_blocks,
    add_time_block,
    get_progress_metrics,
    update_progress_metrics,
    get_subject_performance
)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def detect_intent(query: str) -> Tuple[str, float]:
    """
    Detect the primary intent of the user's query.
    
    Args:
        query: The user's question or request
        
    Returns:
        Tuple of (intent_type, confidence_score)
    """
    # Intent categories with related keywords
    intents = {
        "study_plan": [
            "study plan", "schedule", "routine", "timetable", "study schedule",
            "weekly plan", "daily plan", "plan my study", "organize my studying",
            "how should I study", "when should I study", "study routine"
        ],
        "time_management": [
            "time management", "manage my time", "prioritize", "procrastination",
            "getting things done", "too much to do", "not enough time",
            "balance", "organizing my time", "time blocking", "pomodoro"
        ],
        "goal_setting": [
            "goal", "objective", "target", "aim", "achievement", "milestone",
            "set goals", "achieve goals", "track progress", "track my progress",
            "tracking goals", "academic goals", "learning objectives"
        ],
        "study_techniques": [
            "study technique", "study method", "how to study", "memorize",
            "remember", "retain", "comprehend", "understand better", "learn faster",
            "effective learning", "active recall", "spaced repetition"
        ],
        "motivation": [
            "motivation", "motivated", "procrastinating", "procrastination",
            "lazy", "can't focus", "distracted", "overwhelmed", "burnt out",
            "burnout", "stressed", "anxiety", "worried", "concentrate"
        ],
        "progress_analysis": [
            "progress", "improvement", "getting better", "track progress",
            "how am I doing", "performance", "results", "grades", "scores",
            "analytics", "statistics", "data", "improvement"
        ]
    }
    
    # Convert query to lowercase for case-insensitive matching
    query_lower = query.lower()
    
    # Find matches
    matches = {}
    for intent, keywords in intents.items():
        # Count how many keywords match
        count = sum(1 for keyword in keywords if keyword in query_lower)
        if count > 0:
            # Calculate a simple confidence score based on match count and keyword length
            # Longer keyword matches get higher confidence
            matched_keywords = [kw for kw in keywords if kw in query_lower]
            avg_length = sum(len(kw) for kw in matched_keywords) / len(matched_keywords) if matched_keywords else 0
            confidence = count * (avg_length / 10)  # Normalize to 0-1 range approximately
            matches[intent] = min(confidence, 1.0)  # Cap at 1.0
    
    # If no matches found, default to general coaching
    if not matches:
        return "general_coaching", 0.5
    
    # Return the intent with highest confidence
    best_intent = max(matches.items(), key=lambda x: x[1])
    return best_intent

def generate_study_plan(user_id: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate a personalized study plan based on the user's needs and context.
    
    Args:
        user_id: The student's unique identifier
        query: The user's request
        context: Additional context like course load, preferences, etc.
        
    Returns:
        Dictionary containing the generated study plan
    """
    # Get existing study plan if available
    existing_plan = get_study_plan(user_id)
    
    # Try to get subject performance data to inform the study plan
    performance_data = get_subject_performance(user_id)
    
    # Get any goals the user has set
    goals = get_user_goals(user_id)
    
    # Combine all context for the LLM
    prompt_context = {
        "existing_plan": existing_plan,
        "performance_data": performance_data,
        "goals": goals,
        "additional_context": context or {}
    }
    
    # Format the prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + STUDY_PLAN_PROMPT},
        {"role": "user", "content": f"""
User ID: {user_id}
User Query: {query}

Context Information:
{json.dumps(prompt_context, indent=2)}

Please generate a personalized study plan based on this information.
The plan should include:
1. A weekly schedule with recommended study times
2. Subject prioritization based on performance data and goals
3. Specific study techniques for each subject
4. Integration with any existing goals
5. Flexibility to accommodate changing needs
"""}
    ]
    
    try:
        # Generate the study plan using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )
        
        # Extract the response
        plan_text = response.choices[0].message.content
        
        # Create a structured plan object
        plan = {
            "plan_text": plan_text,
            "generated_at": datetime.now().isoformat(),
            "based_on": {
                "query": query,
                "performance_data": performance_data.get('data', {}) if isinstance(performance_data, dict) else {},
                "goals": [goal.get('title', '') for goal in goals]
            }
        }
        
        # Save the plan
        save_result = save_study_plan(user_id, plan)
        
        if save_result.get("success", False):
            return {
                "success": True,
                "message": "Study plan generated and saved successfully",
                "plan": plan,
                "display_text": plan_text
            }
        else:
            return {
                "success": False,
                "message": f"Study plan generated but failed to save: {save_result.get('message', '')}",
                "plan": plan,
                "display_text": plan_text
            }
    except Exception as e:
        logger.error(f"Error generating study plan: {e}")
        return {
            "success": False,
            "message": f"Failed to generate study plan: {str(e)}",
            "display_text": "I'm sorry, but I encountered an error while creating your study plan. Let's try again with a different approach."
        }

def analyze_progress(user_id: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Analyze a student's academic progress and provide recommendations.
    
    Args:
        user_id: The student's unique identifier
        query: The user's request
        context: Additional context
        
    Returns:
        Dictionary containing the progress analysis
    """
    # Get user's progress metrics
    metrics = get_progress_metrics(user_id)
    
    # Get subject performance data
    performance = get_subject_performance(user_id)
    
    # Get user's goals and their progress
    goals = get_user_goals(user_id)
    
    # Get study plan for context
    plan = get_study_plan(user_id)
    
    # Combine all context for the LLM
    prompt_context = {
        "progress_metrics": metrics,
        "subject_performance": performance.get('data', {}),
        "goals": goals,
        "study_plan": plan,
        "additional_context": context or {}
    }
    
    # Format the prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + PROGRESS_ANALYSIS_PROMPT},
        {"role": "user", "content": f"""
User ID: {user_id}
User Query: {query}

Context Information:
{json.dumps(prompt_context, indent=2)}

Please analyze this student's progress and provide personalized recommendations.
Include:
1. Analysis of strengths and areas for improvement
2. Effectiveness of current study strategies
3. Progress toward goals
4. Specific, actionable recommendations for improvement
5. Key metrics to track going forward
"""}
    ]
    
    try:
        # Generate the analysis using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5  # Lower temperature for more factual analysis
        )
        
        # Extract the response
        analysis_text = response.choices[0].message.content
        
        # Create a structured analysis object
        analysis = {
            "analysis_text": analysis_text,
            "generated_at": datetime.now().isoformat(),
            "based_on": {
                "query": query,
                "metrics": metrics,
                "subject_performance": performance.get('data', {})
            }
        }
        
        # Update progress metrics with this analysis
        updated_metrics = metrics.copy()
        updated_metrics["last_analysis"] = analysis
        update_progress_metrics(user_id, updated_metrics)
        
        return {
            "success": True,
            "message": "Progress analysis completed",
            "analysis": analysis,
            "display_text": analysis_text
        }
    except Exception as e:
        logger.error(f"Error analyzing progress: {e}")
        return {
            "success": False,
            "message": f"Failed to analyze progress: {str(e)}",
            "display_text": "I'm sorry, but I encountered an error while analyzing your progress. Let's try a different approach."
        }

def create_academic_goal(user_id: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Help a student create academic goals.
    
    Args:
        user_id: The student's unique identifier
        query: The user's request
        context: Additional context
        
    Returns:
        Dictionary containing the created goal
    """
    # Get existing goals for context
    existing_goals = get_user_goals(user_id)
    
    # Get performance data for context
    performance = get_subject_performance(user_id)
    
    # Combine all context for the LLM
    prompt_context = {
        "existing_goals": existing_goals,
        "performance_data": performance.get('data', {}),
        "additional_context": context or {}
    }
    
    # Format the prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + GOAL_SETTING_PROMPT},
        {"role": "user", "content": f"""
User ID: {user_id}
User Query: {query}

Context Information:
{json.dumps(prompt_context, indent=2)}

Please help this student create academic goals based on their query and context.
Generate structured goals that are:
1. Specific and measurable
2. Achievable yet challenging
3. Relevant to their academic needs
4. Time-bound with clear deadlines
5. Hierarchical (mix of short and long-term goals)

Format each goal with a title, description, target date, measure of success, and key milestones.
"""}
    ]
    
    try:
        # Generate goals using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )
        
        # Extract the response
        goals_text = response.choices[0].message.content
        
        # Create a structured goal object
        # For now, we'll store the whole text and let the frontend parse it
        # In a production system, we would parse this into structured goals
        goal_data = {
            "title": f"Goals based on: {query[:50]}...",
            "description": goals_text,
            "created_from_query": query,
            "target_date": (datetime.now() + timedelta(days=90)).isoformat()  # Default to 90 days
        }
        
        # Save the goal
        save_result = add_user_goal(user_id, goal_data)
        
        if save_result.get("success", False):
            return {
                "success": True,
                "message": "Academic goals created successfully",
                "goal": save_result.get("goal", {}),
                "display_text": goals_text
            }
        else:
            return {
                "success": False,
                "message": f"Goals generated but failed to save: {save_result.get('message', '')}",
                "display_text": goals_text
            }
    except Exception as e:
        logger.error(f"Error creating academic goals: {e}")
        return {
            "success": False,
            "message": f"Failed to create academic goals: {str(e)}",
            "display_text": "I'm sorry, but I encountered an error while creating your academic goals. Let's try a different approach."
        }

def provide_time_management_advice(user_id: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Provide personalized time management advice.
    
    Args:
        user_id: The student's unique identifier
        query: The user's request
        context: Additional context
        
    Returns:
        Dictionary containing time management advice
    """
    # Get time blocks for context
    time_blocks = get_time_blocks(user_id)
    
    # Get study plan for context
    plan = get_study_plan(user_id)
    
    # Get user's goals for context
    goals = get_user_goals(user_id)
    
    # Combine all context for the LLM
    prompt_context = {
        "time_blocks": time_blocks,
        "study_plan": plan,
        "goals": goals,
        "additional_context": context or {}
    }
    
    # Format the prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + TIME_MANAGEMENT_PROMPT},
        {"role": "user", "content": f"""
User ID: {user_id}
User Query: {query}

Context Information:
{json.dumps(prompt_context, indent=2)}

Please provide personalized time management advice for this student.
Include:
1. Specific techniques that address their needs
2. A structured approach to organizing their time
3. Methods to prioritize tasks effectively
4. Strategies to overcome procrastination
5. Tools or systems they could use
6. Implementation steps to start using these techniques immediately
"""}
    ]
    
    try:
        # Generate advice using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )
        
        # Extract the response
        advice_text = response.choices[0].message.content
        
        return {
            "success": True,
            "message": "Time management advice generated successfully",
            "display_text": advice_text
        }
    except Exception as e:
        logger.error(f"Error generating time management advice: {e}")
        return {
            "success": False,
            "message": f"Failed to generate time management advice: {str(e)}",
            "display_text": "I'm sorry, but I encountered an error while creating time management advice for you. Let's try a different approach."
        }

def provide_motivation_support(user_id: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Provide motivation and academic stress management support.
    
    Args:
        user_id: The student's unique identifier
        query: The user's request
        context: Additional context
        
    Returns:
        Dictionary containing motivation support
    """
    # Get progress metrics for context
    metrics = get_progress_metrics(user_id)
    
    # Get user's goals for context
    goals = get_user_goals(user_id)
    
    # Combine all context for the LLM
    prompt_context = {
        "progress_metrics": metrics,
        "goals": goals,
        "additional_context": context or {}
    }
    
    # Format the prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + MOTIVATION_PROMPT},
        {"role": "user", "content": f"""
User ID: {user_id}
User Query: {query}

Context Information:
{json.dumps(prompt_context, indent=2)}

Please provide personalized motivation and academic stress management support.
Include:
1. Strategies to maintain or rebuild motivation
2. Techniques for managing academic stress
3. Approaches for overcoming burnout or anxiety
4. Mindset shifts that can help
5. Self-care practices that support academic performance
6. Ways to reconnect with the purpose behind their academic work
"""}
    ]
    
    try:
        # Generate support using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.8  # Higher temperature for more empathetic responses
        )
        
        # Extract the response
        support_text = response.choices[0].message.content
        
        return {
            "success": True,
            "message": "Motivation support generated successfully",
            "display_text": support_text
        }
    except Exception as e:
        logger.error(f"Error generating motivation support: {e}")
        return {
            "success": False,
            "message": f"Failed to generate motivation support: {str(e)}",
            "display_text": "I'm sorry, but I encountered an error while creating motivation support for you. Let's try a different approach."
        }

def provide_general_coaching(user_id: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Provide general academic coaching when the intent is unclear.
    
    Args:
        user_id: The student's unique identifier
        query: The user's request
        context: Additional context
        
    Returns:
        Dictionary containing general coaching advice
    """
    # Get study plan for context
    plan = get_study_plan(user_id)
    
    # Get user's goals for context
    goals = get_user_goals(user_id)
    
    # Get performance data for context
    performance = get_subject_performance(user_id)
    
    # Combine all context for the LLM
    prompt_context = {
        "study_plan": plan,
        "goals": goals,
        "performance_data": performance.get('data', {}),
        "additional_context": context or {}
    }
    
    # Format the prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""
User ID: {user_id}
User Query: {query}

Context Information:
{json.dumps(prompt_context, indent=2)}

The user's intent is not clearly defined. Please provide general academic coaching that:
1. Addresses their query thoughtfully
2. Offers helpful guidance based on available context
3. Presents options for more specific support if needed
4. Maintains a supportive and encouraging tone
5. Includes actionable next steps
"""}
    ]
    
    try:
        # Generate coaching using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )
        
        # Extract the response
        coaching_text = response.choices[0].message.content
        
        return {
            "success": True,
            "message": "General coaching generated successfully",
            "display_text": coaching_text
        }
    except Exception as e:
        logger.error(f"Error generating general coaching: {e}")
        return {
            "success": False,
            "message": f"Failed to generate general coaching: {str(e)}",
            "display_text": "I'm sorry, but I encountered an error while providing academic coaching. Please try asking a more specific question, or let me know if you'd like help with study planning, time management, or goal setting."
        }

def process_query(query: str, session_id: str, message_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Process a query to the Academic Coach Agent.
    
    Args:
        query: The query string
        session_id: Unique session identifier
        message_history: Previous messages in the conversation
        
    Returns:
        Dict containing the agent's response
    """
    try:
        # Initialize message history if not provided
        if message_history is None:
            message_history = []
        
        # Extract user ID from session (in production, this would be a real user ID)
        user_id = session_id
        
        # Detect intent from query
        intent, confidence = detect_intent(query)
        logger.info(f"Detected intent: {intent} (confidence: {confidence:.2f})")
        
        # Extract context from message history
        context = {"message_history": message_history}
        
        # Process based on intent
        if intent == "study_plan":
            result = generate_study_plan(user_id, query, context)
        elif intent == "progress_analysis":
            result = analyze_progress(user_id, query, context)
        elif intent == "goal_setting":
            result = create_academic_goal(user_id, query, context)
        elif intent == "time_management":
            result = provide_time_management_advice(user_id, query, context)
        elif intent == "motivation":
            result = provide_motivation_support(user_id, query, context)
        elif intent == "study_techniques":
            # For now, handle study techniques as part of study planning
            result = generate_study_plan(user_id, query, context)
        else:
            # Default to general coaching
            result = provide_general_coaching(user_id, query, context)
        
        # Get response text from result
        response_text = result.get("display_text", "I'm sorry, but I'm having trouble processing your request right now.")
        
        # Add the query and response to message history
        message_history.append({"role": "user", "content": query})
        message_history.append({"role": "assistant", "content": response_text})
        
        # Return the complete result
        return {
            "response": response_text,
            "message_history": message_history,
            "intent": intent,
            "confidence": confidence,
            "session_id": session_id,
            "user_id": user_id,
            "success": result.get("success", False),
            "error": result.get("message") if not result.get("success", False) else None
        }
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        error_message = f"I'm sorry, but I encountered an error while processing your request. Please try again with a more specific question about your academic needs."
        
        # Add error response to message history
        message_history.append({"role": "user", "content": query})
        message_history.append({"role": "assistant", "content": error_message})
        
        return {
            "response": error_message,
            "message_history": message_history,
            "session_id": session_id,
            "success": False,
            "error": str(e)
        }

# For local testing
if __name__ == "__main__":
    # Test the agent
    test_query = "I need help creating a study plan for my computer science course. I'm struggling with time management."
    test_session_id = "test-user-123"
    
    result = process_query(test_query, test_session_id)
    print(f"Query: {test_query}")
    print(f"Intent: {result.get('intent', 'unknown')}")
    print(f"Response: {result['response']}")