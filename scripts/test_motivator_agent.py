#!/usr/bin/env python3
"""
Test script for the motivator agent.

This script allows testing the motivator agent locally before deployment.
It simulates a conversation by accepting user input and displaying agent responses,
including emotional assessments and intervention recommendations.

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

# Import the agent processing function
try:
    from tutor.motivator_agent.agent import process_query
except ImportError as e:
    print(f"Error importing the motivator agent: {e}")
    print("Make sure you've set up the project structure correctly.")
    sys.exit(1)

def main():
    """Run an interactive test session with the motivator agent."""
    print("=" * 80)
    print("Motivator Agent (Emotional Support Specialist) Test Console")
    print("=" * 80)
    print("Express your concerns, stress, or academic challenges, or type 'exit' to quit.")
    print("Type 'debug on' to see the emotional assessment details.")
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
            print("\nThank you for testing the motivator agent!")
            break
            
        # Check for debug toggle
        if user_input.lower() in ("debug on", "debug true"):
            show_debug = True
            print("Debug mode enabled - showing emotional assessments")
            continue
        elif user_input.lower() in ("debug off", "debug false"):
            show_debug = False
            print("Debug mode disabled")
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
            
            # Display the response
            print(f"\nSupport Specialist: {response}")
            
            # Display debug information if enabled
            if show_debug:
                print("\n[Debug] Emotional Assessment:")
                emotional_state = result.get("emotional_state", {})
                for key, value in emotional_state.items():
                    print(f"  - {key}: {value}")
                
                print(f"\n[Debug] Intervention needed: {result.get('intervention_needed', False)}")
                if result.get("intervention_needed"):
                    print(f"[Debug] Intervention type: {result.get('intervention_type', 'none')}")
                
            # Display any error (for debugging)
            if result.get("error"):
                print(f"\n[Debug] Error: {result['error']}")
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("An unexpected error occurred while processing your message.")
            
        print("-" * 80)

if __name__ == "__main__":
    main()