#!/usr/bin/env python3
"""
Test script for the orchestrator agent.

This script allows testing the orchestrator agent locally before deployment.
It simulates a conversation by accepting user input, routing to appropriate
specialized agents, and displaying the aggregated response.

Updated for LangChain 0.3+ compatibility.
"""

import os
import sys
import uuid
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add the project root to the Python path to enable imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Load environment variables from .env file
load_dotenv()

# Check for required environment variables
required_vars = ["OPENAI_API_KEY"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    print(f"Error: The following required environment variables are missing: {', '.join(missing_vars)}")
    print("Please set them in your .env file or environment.")
    sys.exit(1)

# Additional check for Google API keys needed by the university agent
if not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GOOGLE_CSE_ID"):
    print("Warning: GOOGLE_API_KEY and/or GOOGLE_CSE_ID environment variables are not set.")
    print("The university agent's search functionality will be limited.")

# Import the agent processing function
try:
    from agents.orchestrator.agent import process_query
except ImportError as e:
    print(f"Error importing the orchestrator agent: {e}")
    print("Make sure you've set up the project structure correctly.")
    sys.exit(1)

def main():
    """Run an interactive test session with the orchestrator agent."""
    print("=" * 80)
    print("Orchestrator Agent Test Console")
    print("=" * 80)
    print("Ask any question about university information, academic challenges, or emotional support.")
    print("Type 'exit' to quit, 'debug on' to see agent selection details, or 'clear' to reset conversation.")
    print("-" * 80)
    
    # Create a unique session ID for this conversation
    session_id = str(uuid.uuid4())
    message_history = []
    show_debug = False
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Check for exit command
        if user_input.lower() in ("exit", "quit", "bye"):
            print("\nThank you for testing the orchestrator agent!")
            break
            
        # Check for debug toggle
        if user_input.lower() in ("debug on", "debug true"):
            show_debug = True
            print("Debug mode enabled - showing agent selection details")
            continue
        elif user_input.lower() in ("debug off", "debug false"):
            show_debug = False
            print("Debug mode disabled")
            continue
            
        # Check for conversation reset
        if user_input.lower() in ("clear", "reset"):
            message_history = []
            print("Conversation history cleared")
            continue
            
        # Skip empty input
        if not user_input:
            continue
            
        # Process the query
        print("\nProcessing...")
        try:
            result = process_query(user_input, session_id, message_history)
            
            # Extract the response and updated message history
            response = result["response"]
            message_history = result["message_history"]
            used_agents = result.get("used_agents", [])
            
            # Display the response
            print(f"\nAssistant: {response}")
            
            # Display debug information if enabled
            if show_debug:
                print("\n[Debug] Agents used:")
                for agent in used_agents:
                    print(f"  - {agent}")
                
            # Display any error (for debugging)
            if result.get("error"):
                print(f"\n[Debug] Error: {result['error']}")
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("An unexpected error occurred while processing your query.")
            
        print("-" * 80)

if __name__ == "__main__":
    main()