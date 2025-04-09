"""
Academic Coach Agent Tools

This module contains tools for the Academic Coach Agent to manage student goals,
study plans, and progress tracking information.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Mock database for development/testing purposes when no DynamoDB is available
# In production, this would be replaced with DynamoDB calls
MOCK_DB = {
    "study_plans": {},
    "goals": {},
    "time_blocks": {},
    "progress_metrics": {}
}

def get_study_plan(user_id: str) -> Dict[str, Any]:
    """
    Retrieve a student's current study plan.
    
    Args:
        user_id: The student's unique identifier
        
    Returns:
        Dictionary containing the study plan or empty dict if none exists
    """
    try:
        # In production, this would query DynamoDB
        # For now, use mock database
        if user_id in MOCK_DB["study_plans"]:
            return MOCK_DB["study_plans"][user_id]
        
        # Return empty plan if none exists
        return {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "weekly_schedule": {},
            "subject_priorities": [],
            "study_techniques": {},
            "notes": ""
        }
    except Exception as e:
        logger.error(f"Error getting study plan for user {user_id}: {e}")
        return {"error": str(e)}

def save_study_plan(user_id: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save or update a student's study plan.
    
    Args:
        user_id: The student's unique identifier
        plan_data: The study plan data to save
        
    Returns:
        Dictionary indicating success/failure
    """
    try:
        # Add metadata
        plan_data["user_id"] = user_id
        plan_data["last_updated"] = datetime.now().isoformat()
        
        if user_id not in MOCK_DB["study_plans"]:
            plan_data["created_at"] = datetime.now().isoformat()
        
        # In production, this would update DynamoDB
        # For now, use mock database
        MOCK_DB["study_plans"][user_id] = plan_data
        
        return {
            "success": True,
            "message": "Study plan saved successfully",
            "plan_id": user_id
        }
    except Exception as e:
        logger.error(f"Error saving study plan for user {user_id}: {e}")
        return {
            "success": False,
            "message": f"Error saving study plan: {str(e)}"
        }

def get_user_goals(user_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve a student's academic goals.
    
    Args:
        user_id: The student's unique identifier
        
    Returns:
        List of goal objects
    """
    try:
        # In production, this would query DynamoDB
        # For now, use mock database
        if user_id in MOCK_DB["goals"]:
            return MOCK_DB["goals"][user_id]
        
        # Return empty list if no goals exist
        return []
    except Exception as e:
        logger.error(f"Error getting goals for user {user_id}: {e}")
        return []

def add_user_goal(user_id: str, goal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a new academic goal for a student.
    
    Args:
        user_id: The student's unique identifier
        goal_data: The goal data to save
        
    Returns:
        Dictionary indicating success/failure and the saved goal
    """
    try:
        # Add metadata
        goal_id = str(uuid.uuid4())
        goal_data["goal_id"] = goal_id
        goal_data["user_id"] = user_id
        goal_data["created_at"] = datetime.now().isoformat()
        goal_data["last_updated"] = datetime.now().isoformat()
        goal_data["progress"] = 0
        
        # In production, this would update DynamoDB
        # For now, use mock database
        if user_id not in MOCK_DB["goals"]:
            MOCK_DB["goals"][user_id] = []
        
        MOCK_DB["goals"][user_id].append(goal_data)
        
        return {
            "success": True,
            "message": "Goal added successfully",
            "goal": goal_data
        }
    except Exception as e:
        logger.error(f"Error adding goal for user {user_id}: {e}")
        return {
            "success": False,
            "message": f"Error adding goal: {str(e)}"
        }

def update_goal_progress(user_id: str, goal_id: str, progress: int, notes: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the progress for an existing academic goal.
    
    Args:
        user_id: The student's unique identifier
        goal_id: The goal's unique identifier
        progress: Progress percentage (0-100)
        notes: Optional notes about the progress update
        
    Returns:
        Dictionary indicating success/failure
    """
    try:
        # Validate progress value
        if not (0 <= progress <= 100):
            return {
                "success": False,
                "message": "Progress must be between 0 and 100"
            }
        
        # In production, this would update DynamoDB
        # For now, use mock database
        if user_id not in MOCK_DB["goals"]:
            return {
                "success": False,
                "message": "User has no goals"
            }
        
        # Find the goal to update
        found = False
        for goal in MOCK_DB["goals"][user_id]:
            if goal["goal_id"] == goal_id:
                goal["progress"] = progress
                goal["last_updated"] = datetime.now().isoformat()
                if notes:
                    goal["notes"] = notes
                found = True
                break
        
        if not found:
            return {
                "success": False,
                "message": f"Goal with ID {goal_id} not found"
            }
        
        return {
            "success": True,
            "message": "Goal progress updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating goal progress for user {user_id}, goal {goal_id}: {e}")
        return {
            "success": False,
            "message": f"Error updating goal progress: {str(e)}"
        }

def get_time_blocks(user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve a student's scheduled time blocks.
    
    Args:
        user_id: The student's unique identifier
        start_date: Optional ISO format start date to filter time blocks
        end_date: Optional ISO format end date to filter time blocks
        
    Returns:
        List of time block objects
    """
    try:
        # In production, this would query DynamoDB
        # For now, use mock database
        if user_id not in MOCK_DB["time_blocks"]:
            return []
        
        # Return all time blocks for this user
        time_blocks = MOCK_DB["time_blocks"][user_id]
        
        # Filter by date range if provided
        if start_date or end_date:
            start = datetime.fromisoformat(start_date) if start_date else datetime.min
            end = datetime.fromisoformat(end_date) if end_date else datetime.max
            
            filtered_blocks = [
                block for block in time_blocks
                if start <= datetime.fromisoformat(block["start_time"]) <= end
            ]
            return filtered_blocks
        
        return time_blocks
    except Exception as e:
        logger.error(f"Error getting time blocks for user {user_id}: {e}")
        return []

def add_time_block(user_id: str, time_block: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a new study time block for a student.
    
    Args:
        user_id: The student's unique identifier
        time_block: The time block data to save
        
    Returns:
        Dictionary indicating success/failure
    """
    try:
        # Add metadata
        block_id = str(uuid.uuid4())
        time_block["block_id"] = block_id
        time_block["user_id"] = user_id
        time_block["created_at"] = datetime.now().isoformat()
        
        # Validate required fields
        required_fields = ["subject", "start_time", "end_time"]
        for field in required_fields:
            if field not in time_block:
                return {
                    "success": False,
                    "message": f"Missing required field: {field}"
                }
        
        # In production, this would update DynamoDB
        # For now, use mock database
        if user_id not in MOCK_DB["time_blocks"]:
            MOCK_DB["time_blocks"][user_id] = []
        
        MOCK_DB["time_blocks"][user_id].append(time_block)
        
        return {
            "success": True,
            "message": "Time block added successfully",
            "block_id": block_id
        }
    except Exception as e:
        logger.error(f"Error adding time block for user {user_id}: {e}")
        return {
            "success": False,
            "message": f"Error adding time block: {str(e)}"
        }

def get_progress_metrics(user_id: str) -> Dict[str, Any]:
    """
    Retrieve a student's academic progress metrics.
    
    Args:
        user_id: The student's unique identifier
        
    Returns:
        Dictionary containing progress metrics
    """
    try:
        # In production, this would query DynamoDB and aggregate data from multiple sources
        # For now, use mock database
        if user_id in MOCK_DB["progress_metrics"]:
            return MOCK_DB["progress_metrics"][user_id]
        
        # Return empty metrics if none exist
        return {
            "user_id": user_id,
            "last_updated": datetime.now().isoformat(),
            "quiz_scores": {},
            "study_consistency": 0,
            "goal_completion_rate": 0,
            "focus_areas": [],
            "strengths": [],
            "improvement_areas": []
        }
    except Exception as e:
        logger.error(f"Error getting progress metrics for user {user_id}: {e}")
        return {"error": str(e)}

def update_progress_metrics(user_id: str, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a student's academic progress metrics.
    
    Args:
        user_id: The student's unique identifier
        metrics_data: The metrics data to update
        
    Returns:
        Dictionary indicating success/failure
    """
    try:
        # Update last_updated timestamp
        metrics_data["last_updated"] = datetime.now().isoformat()
        metrics_data["user_id"] = user_id
        
        # In production, this would update DynamoDB
        # For now, use mock database
        MOCK_DB["progress_metrics"][user_id] = metrics_data
        
        return {
            "success": True,
            "message": "Progress metrics updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating progress metrics for user {user_id}: {e}")
        return {
            "success": False,
            "message": f"Error updating progress metrics: {str(e)}"
        }

def get_subject_performance(user_id: str) -> Dict[str, Any]:
    """
    Get performance metrics by subject for a student.
    This compiles data from knowledge checks and other sources.
    
    Args:
        user_id: The student's unique identifier
        
    Returns:
        Dictionary mapping subjects to performance metrics
    """
    try:
        # In production, this would query and aggregate from Knowledge Check Agent results
        # For now, return mock data
        
        # First try to use the knowledge check agent directly if available
        try:
            from agents.knowledge_check_agent.tools import get_user_chapter_stats
            # Aggregate stats from various chapters
            chapters = ['chapter-1', 'chapter-2', 'chapter-3', 'chapter-4', 'chapter-5']
            subject_data = {}
            
            for chapter in chapters:
                result = get_user_chapter_stats(user_id, chapter)
                if result.get('success', False):
                    chapter_data = result.get('data', {})
                    subject_name = {
                        'chapter-1': 'Introduction to Computer Science',
                        'chapter-2': 'Data Structures and Algorithms',
                        'chapter-3': 'Object-Oriented Programming',
                        'chapter-4': 'Web Development',
                        'chapter-5': 'Database Design'
                    }.get(chapter, chapter)
                    
                    subject_data[subject_name] = {
                        'best_score': chapter_data.get('best_score', 0),
                        'attempts': chapter_data.get('attempts', 0),
                        'last_attempt_date': chapter_data.get('last_attempt_date', None),
                        'improvement_rate': chapter_data.get('improvement_rate', 0)
                    }
            
            if subject_data:
                return {
                    'success': True,
                    'data': subject_data
                }
        except ImportError:
            # Knowledge check agent not available, fall back to mock data
            pass
        
        # Mock data as fallback
        return {
            'success': True,
            'data': {
                'Introduction to Computer Science': {
                    'best_score': 85,
                    'attempts': 2,
                    'last_attempt_date': (datetime.now() - timedelta(days=5)).isoformat(),
                    'improvement_rate': 15
                },
                'Data Structures and Algorithms': {
                    'best_score': 72,
                    'attempts': 3,
                    'last_attempt_date': (datetime.now() - timedelta(days=2)).isoformat(),
                    'improvement_rate': 8
                },
                'Object-Oriented Programming': {
                    'best_score': 90,
                    'attempts': 1,
                    'last_attempt_date': (datetime.now() - timedelta(days=10)).isoformat(),
                    'improvement_rate': 0
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting subject performance for user {user_id}: {e}")
        return {
            'success': False,
            'message': f"Error retrieving subject performance: {str(e)}"
        }