"""
Tools for the Survey Agent

This module contains tools used by the Survey Agent
for storing and retrieving survey responses in DynamoDB.
"""

import os
import json
import boto3
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

# Define table name - using the SurveyResponses table you created
SURVEY_RESPONSES_TABLE = 'SurveyResponses'

def store_survey_response(
    user_sub: str,
    survey_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Store a survey response in DynamoDB.
    
    Args:
        user_sub: The user's sub (username/primary key)
        survey_data: The complete survey response data
        
    Returns:
        Dict containing operation results
    """
    try:
        table = dynamodb.Table(SURVEY_RESPONSES_TABLE)
        
        # Get current timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Store the survey response
        response = table.put_item(
            Item={
                'sub': user_sub,
                'surveyData': survey_data,
                'submittedAt': timestamp,
                'createdAt': timestamp
            }
        )
        
        return {
            'success': True,
            'message': 'Survey response stored successfully',
            'data': {
                'sub': user_sub,
                'submittedAt': timestamp
            }
        }
    except Exception as e:
        print(f"Error storing survey response: {e}")
        return {
            'success': False,
            'message': f'Error storing survey response: {str(e)}'
        }

def get_survey_response(user_sub: str) -> Dict[str, Any]:
    """
    Get a user's survey response from DynamoDB.
    
    Args:
        user_sub: The user's sub (username/primary key)
        
    Returns:
        Dict containing the survey response or error
    """
    try:
        table = dynamodb.Table(SURVEY_RESPONSES_TABLE)
        
        # Get the survey response for this user
        response = table.get_item(
            Key={
                'sub': user_sub
            }
        )
        
        if 'Item' in response:
            return {
                'success': True,
                'data': response['Item']
            }
        else:
            return {
                'success': False,
                'message': 'No survey response found for this user'
            }
    except Exception as e:
        print(f"Error retrieving survey response: {e}")
        return {
            'success': False,
            'message': f'Error retrieving survey response: {str(e)}'
        }

def update_survey_response(
    user_sub: str,
    survey_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update an existing survey response in DynamoDB.
    
    Args:
        user_sub: The user's sub (username/primary key)
        survey_data: The updated survey response data
        
    Returns:
        Dict containing operation results
    """
    try:
        table = dynamodb.Table(SURVEY_RESPONSES_TABLE)
        
        # Get current timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Update the survey response
        response = table.update_item(
            Key={
                'sub': user_sub
            },
            UpdateExpression='SET surveyData = :survey_data, submittedAt = :timestamp',
            ExpressionAttributeValues={
                ':survey_data': survey_data,
                ':timestamp': timestamp
            },
            ReturnValues='UPDATED_NEW'
        )
        
        return {
            'success': True,
            'message': 'Survey response updated successfully',
            'data': {
                'sub': user_sub,
                'submittedAt': timestamp
            }
        }
    except Exception as e:
        print(f"Error updating survey response: {e}")
        return {
            'success': False,
            'message': f'Error updating survey response: {str(e)}'
        }

def get_all_survey_responses() -> Dict[str, Any]:
    """
    Get all survey responses from DynamoDB (for admin/analytics purposes).
    
    Returns:
        Dict containing all survey responses or error
    """
    try:
        table = dynamodb.Table(SURVEY_RESPONSES_TABLE)
        
        # Scan all items in the table
        response = table.scan()
        
        items = response.get('Items', [])
        
        return {
            'success': True,
            'data': {
                'responses': items,
                'count': len(items)
            }
        }
    except Exception as e:
        print(f"Error retrieving all survey responses: {e}")
        return {
            'success': False,
            'message': f'Error retrieving all survey responses: {str(e)}'
        }