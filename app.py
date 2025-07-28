"""
Flask API Server for Ciro AI Tutor

This module implements a REST API for the Ciro AI Tutor system,
exposing endpoints that connect the React frontend to the agent
backend.

Usage:
    python app.py
"""

from quart import Quart, request, jsonify
from quart_cors import cors
import uuid
import asyncio
import os
import boto3
from botocore.exceptions import ClientError
import json

# updated Tutor Agent
from tutor.graph.workflows.ciro import CiroTutor

# Create the Flask application
app = Quart(__name__)

# Configure CORS properly for development
# This allows requests from any origin with any headers and methods
app=cors(app, allow_origin="*", allow_headers="*", expose_headers="*" )

# In-memory storage for conversation sessions
# In production, this would be replaced with a database
sessions = {}

# Initialize DynamoDB client for the existing Users table
try:
    # Check if AWS credentials are available
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    if aws_access_key and aws_secret_key:
        print("Using AWS credentials from environment variables")
        dynamodb = boto3.resource(
            'dynamodb', 
            region_name=os.environ.get('AWS_REGION', 'us-east-2'),
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
    else:
        print("Using default AWS credentials (profile/IAM role)")
        dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-2'))
    
    users_table = dynamodb.Table('Users')  # Using existing Users table
    print("DynamoDB connected to Users table")
except Exception as e:
    print(f"Warning: DynamoDB connection failed: {e}")
    print("Survey responses will be logged to console for debugging")
    dynamodb = None
    users_table = None

# Initialize LangGraph once before any requests
@app.before_serving
async def startup():
    await CiroTutor.init_graph()
    print("LangGraph initialized")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running."""
    return jsonify({
        'status': 'ok',
        'message': 'API is running'
    })

@app.route('/api/chat', methods=['POST'])
async def chat():
    """
    Main chat endpoint that processes messages through the orchestrator.
    
    Expected request body:
    {
        "message": "User's message text",
        "session_id": "Optional session ID"
    }
    
    Returns:
    {
        "response": "Agent's response text",
        "session_id": "Session ID for this conversation",
        "used_agents": ["List of tutor used to generate the response"]
    }
    """
    data = await request.get_json()
    tutor = CiroTutor(thread_id=data.get("session_id", str(uuid.uuid4())))
    response = await tutor.process_message(data["message"])
    return jsonify({"response": response})


@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """(Stub) Return session history metadata — can be expanded later."""
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify({'session_id': session_id})

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    return jsonify({'sessions': list(sessions.keys())})

@app.route('/api/survey', methods=['POST'])
async def save_survey():
    """
    Save survey responses to the Users table in DynamoDB.
    
    Expected request body:
    {
        "userId": "user-id-from-auth",
        "surveyResponses": {
            "responses": {
                "intendedMajor": "Computer Science",
                "majorReason": "I love programming...",
                "supportNeeds": ["Math skills", "Study skills"],
                "participationInterests": ["Student organizations"],
                "workHours": "10-15",
                "potentialIssues": ["Keeping up with academics"]
            },
            "submittedAt": "2025-01-28T..."
        }
    }
    
    Returns:
    {
        "success": true,
        "message": "Survey responses saved successfully"
    }
    """
    try:
        data = await request.get_json()
        
        # Validate required fields
        if not data or 'userId' not in data or 'surveyResponses' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: userId and surveyResponses'
            }), 400
        
        user_id = data['userId']
        survey_responses = data['surveyResponses']
        
        print(f"Attempting to save survey for user: {user_id}")
        print(f"Survey data: {json.dumps(survey_responses, indent=2)}")
        
        # Check if DynamoDB is available
        if not users_table:
            print("DynamoDB not available - logging survey data to console")
            print(f"SURVEY DATA FOR USER {user_id}:")
            print(json.dumps(survey_responses, indent=2))
            
            # Return success even without DynamoDB for development purposes
            return jsonify({
                'success': True,
                'message': 'Survey responses logged to console (DynamoDB not available)',
                'note': 'Configure AWS credentials to save to DynamoDB'
            })
        
        # Update the user record in DynamoDB with survey responses
        # Add survey responses as a new attribute to the existing user record
        response = users_table.update_item(
            Key={'sub': user_id},  # Assuming 'sub' is the primary key in Users table
            UpdateExpression='SET surveyResponses = :survey, surveyCompletedAt = :completed_at',
            ExpressionAttributeValues={
                ':survey': survey_responses,
                ':completed_at': survey_responses.get('submittedAt', 'unknown')
            },
            ReturnValues='UPDATED_NEW'
        )
        
        print(f"Survey responses saved to DynamoDB for user {user_id}")
        print(f"Updated attributes: {response.get('Attributes', {})}")
        
        return jsonify({
            'success': True,
            'message': 'Survey responses saved successfully to DynamoDB',
            'updatedAttributes': response.get('Attributes', {})
        })
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"DynamoDB error: {error_code} - {error_message}")
        
        # Handle credential issues by falling back to console logging
        if error_code in ['UnrecognizedClientException', 'InvalidSignatureException', 'TokenRefreshRequired']:
            print("AWS credentials invalid - falling back to console logging")
            print(f"SURVEY DATA FOR USER {user_id}:")
            print(json.dumps(survey_responses, indent=2))
            
            return jsonify({
                'success': True,
                'message': 'Survey responses logged to console (AWS credentials invalid)',
                'note': 'Configure valid AWS credentials to save to DynamoDB'
            })
        elif error_code == 'ResourceNotFoundException':
            return jsonify({
                'success': False,
                'error': 'User not found in database'
            }), 404
        else:
            # For other DynamoDB errors, also fall back to console logging
            print("DynamoDB error - falling back to console logging")
            print(f"SURVEY DATA FOR USER {user_id}:")
            print(json.dumps(survey_responses, indent=2))
            
            return jsonify({
                'success': True,
                'message': f'Survey responses logged to console (DynamoDB error: {error_message})',
                'note': 'Check AWS configuration to save to DynamoDB'
            })
            
    except Exception as e:
        print(f"Survey save error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

if __name__ == '__main__':
    if not os.environ.get("OPENAI_API_KEY"):
        from dotenv import load_dotenv
        load_dotenv()

    print("\n=== API Routes ===")
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
        print(f"{methods} {rule}")
  
    # Run the server
    app.run(host='0.0.0.0', port=5001, debug=True)
