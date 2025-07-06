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
