"""
Tools for the Knowledge Check Agent

This module contains tools used by the Knowledge Check Agent
for database operations and question generation.
"""

import os
import json
import boto3
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

# Define table name based on environment (dev/prod)
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
KNOWLEDGE_CHECK_TABLE = f'knowledge-check-{ENVIRONMENT}'

def store_quiz_result(
    user_id: str,
    chapter_id: str,
    score: int,
    question_count: int,
    answers: List[int]
) -> Dict[str, Any]:
    """
    Store a quiz result in DynamoDB.
    
    Args:
        user_id: The user's ID
        chapter_id: The chapter ID (e.g., 'chapter-1')
        score: Number of correct answers
        question_count: Total number of questions
        answers: List of answers submitted by the user
        
    Returns:
        Dict containing operation results
    """
    try:
        table = dynamodb.Table(KNOWLEDGE_CHECK_TABLE)
        
        # Get current timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Create a unique attempt ID
        attempt_id = f"{user_id}-{chapter_id}-{timestamp}"
        
        # Calculate percentage score
        percentage = (score / question_count) * 100
        
        # Store the quiz result
        response = table.put_item(
            Item={
                'PK': user_id,
                'SK': f"QUIZ#{attempt_id}",
                'userId': user_id,
                'chapterId': chapter_id,
                'score': score,
                'percentage': percentage,
                'questionCount': question_count,
                'answers': answers,
                'timestamp': timestamp,
                'type': 'quiz_attempt'
            }
        )
        
        # Update the user's best score if this is a new best
        update_best_score(user_id, chapter_id, percentage)
        
        return {
            'success': True,
            'message': 'Quiz result stored successfully',
            'data': {
                'attemptId': attempt_id,
                'score': score,
                'percentage': percentage
            }
        }
    except Exception as e:
        print(f"Error storing quiz result: {e}")
        return {
            'success': False,
            'message': f'Error storing quiz result: {str(e)}'
        }

def update_best_score(
    user_id: str,
    chapter_id: str,
    new_score: float
) -> None:
    """
    Update the user's best score for a chapter if this is a new best.
    
    Args:
        user_id: The user's ID
        chapter_id: The chapter ID
        new_score: The new percentage score
    """
    try:
        table = dynamodb.Table(KNOWLEDGE_CHECK_TABLE)
        
        # Get current best score
        response = table.get_item(
            Key={
                'PK': user_id,
                'SK': f"BESTSCORE#{chapter_id}"
            }
        )
        
        current_best = response.get('Item', {}).get('score', 0)
        
        # Update if this is a new best score
        if new_score > current_best:
            table.put_item(
                Item={
                    'PK': user_id,
                    'SK': f"BESTSCORE#{chapter_id}",
                    'userId': user_id,
                    'chapterId': chapter_id,
                    'score': new_score,
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'best_score'
                }
            )
    except Exception as e:
        print(f"Error updating best score: {e}")

def get_user_chapter_stats(
    user_id: str,
    chapter_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a user's statistics for a specific chapter or all chapters.
    
    Args:
        user_id: The user's ID
        chapter_id: Optional chapter ID to filter results
        
    Returns:
        Dict containing user stats
    """
    try:
        table = dynamodb.Table(KNOWLEDGE_CHECK_TABLE)
        
        # Get all items for this user
        response = table.query(
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': user_id
            }
        )
        
        items = response.get('Items', [])
        
        # Filter by chapter if specified
        if chapter_id:
            items = [
                item for item in items 
                if item.get('chapterId') == chapter_id
            ]
        
        # Separate attempts and best scores
        attempts = [item for item in items if item.get('type') == 'quiz_attempt']
        best_scores = [item for item in items if item.get('type') == 'best_score']
        
        # Group attempts by chapter
        attempts_by_chapter = {}
        for attempt in attempts:
            chapter = attempt.get('chapterId')
            if chapter not in attempts_by_chapter:
                attempts_by_chapter[chapter] = []
            attempts_by_chapter[chapter].append(attempt)
        
        # Count attempts per chapter
        attempt_counts = {
            chapter: len(attempts)
            for chapter, attempts in attempts_by_chapter.items()
        }
        
        # Extract best scores
        best_scores_dict = {
            score.get('chapterId'): score.get('score')
            for score in best_scores
        }
        
        return {
            'success': True,
            'data': {
                'userId': user_id,
                'attemptCounts': attempt_counts,
                'bestScores': best_scores_dict,
                'totalAttempts': len(attempts)
            }
        }
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {
            'success': False,
            'message': f'Error getting user stats: {str(e)}'
        }