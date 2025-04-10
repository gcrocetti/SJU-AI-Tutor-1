"""
Flask API Server for Ciro AI Tutor

This module implements a REST API for the Ciro AI Tutor system,
exposing endpoints that connect the React frontend to the agent
backend.

Usage:
    python app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os

# Import the agents
from agents.orchestrator.agent import process_query as orchestrator_process
from agents.university_agent.agent import process_query as university_process
from agents.motivator_agent.agent import process_query as motivator_process
from agents.knowledge_check_agent.agent import process_query as knowledge_check_process

# Create the Flask application
app = Flask(__name__)

# Configure CORS properly for development
# This allows requests from any origin with any headers and methods
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}})

# In-memory storage for conversation sessions
# In production, this would be replaced with a database
sessions = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running."""
    return jsonify({
        'status': 'ok',
        'message': 'API is running'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
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
        "used_agents": ["List of agents used to generate the response"]
    }
    """
    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({
            'error': 'Missing required parameters'
        }), 400
    
    # Get or create session ID
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    # Get message history or initialize new one
    message_history = sessions.get(session_id, [])
    
    try:
        # Process through orchestrator
        result = orchestrator_process(
            query=data['message'],
            session_id=session_id,
            message_history=message_history
        )
        
        # Update session storage
        sessions[session_id] = result.get('message_history', message_history)
        
        return jsonify({
            'response': result.get('response', ''),
            'session_id': session_id,
            'used_agents': result.get('used_agents', [])
        })
    except Exception as e:
        app.logger.error(f"Error processing message: {str(e)}")
        return jsonify({
            'error': str(e),
            'session_id': session_id
        }), 500

@app.route('/api/agent/<agent_id>', methods=['POST'])
def direct_agent(agent_id):
    """
    Route messages directly to a specific agent, bypassing the orchestrator.
    Useful for development/testing.
    
    Expected request body:
    {
        "message": "User's message text",
        "session_id": "Optional session ID"
    }
    """
    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({
            'error': 'Missing required parameters'
        }), 400
    
    # Get or create session ID
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    # Get message history or initialize new one
    message_history = sessions.get(session_id, [])
    
    try:
        # Route to appropriate agent
        if agent_id == 'university':
            result = university_process(
                query=data['message'],
                session_id=session_id,
                message_history=message_history
            )
        elif agent_id == 'motivator':
            result = motivator_process(
                query=data['message'],
                session_id=session_id,
                message_history=message_history
            )
        elif agent_id == 'knowledge_check':
            result = knowledge_check_process(
                query=data['message'],
                session_id=session_id,
                message_history=message_history
            )
            
            # The knowledge check agent may return additional data
            return jsonify({
                'response': result.get('response', ''),
                'data': result.get('data', {}),
                'session_id': session_id
            })
        else:
            return jsonify({
                'error': f'Unknown agent: {agent_id}'
            }), 400
        
        # Update session storage
        sessions[session_id] = result.get('message_history', message_history)
        
        return jsonify({
            'response': result.get('response', ''),
            'session_id': session_id
        })
    except Exception as e:
        app.logger.error(f"Error processing message: {str(e)}")
        return jsonify({
            'error': str(e),
            'session_id': session_id
        }), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    Retrieve the message history for a given session.
    
    Returns:
    {
        "session_id": "Session ID",
        "messages": [List of message objects]
    }
    """
    if session_id not in sessions:
        return jsonify({
            'error': 'Session not found'
        }), 404
    
    return jsonify({
        'session_id': session_id,
        'messages': sessions[session_id]
    })

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """
    List all active session IDs.
    
    Returns:
    {
        "sessions": [List of session IDs]
    }
    """
    return jsonify({
        'sessions': list(sessions.keys())
    })

if __name__ == '__main__':
    # Set up OpenAI API key from environment
    if not os.environ.get("OPENAI_API_KEY"):
        from dotenv import load_dotenv
        load_dotenv()
    
    # Print all routes for debugging
    print("\n=== API Routes ===")
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
        print(f"{methods} {rule}")
    
    # Run the server
    app.run(host='0.0.0.0', port=5000, debug=True)