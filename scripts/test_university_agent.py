#!/usr/bin/env python3
"""
Test script for the university agent.

This script allows testing the university agent locally before deployment.
It simulates a conversation by accepting user input and displaying agent responses.
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
required_vars = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_CSE_ID"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    print(f"Error: The following required environment variables are missing: {', '.join(missing_vars)}")
    print("Please set them in your .env file or environment.")
    sys.exit(1)

# Import the agent processing function
try:
    from agents.university_agent.agent import process_query
except ImportError as e:
    print(f"Error importing the university agent: {e}")
    print("Make sure you've set up the project structure correctly.")
    sys.exit(1)

def main():
    """Run an interactive test session with the university agent."""
    print("=" * 80)
    print("University Agent Test Console")
    print("=" * 80)
    print("Type your questions about the university, or 'exit' to quit.")
    print("-" * 80)
    
    # Create a unique session ID for this conversation
    session_id = str(uuid.uuid4())
    message_history = []
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Check for exit command
        if user_input.lower() in ("exit", "quit", "bye"):
            print("\nThank you for testing the university agent!")
            break
            
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
            print(f"\nAssistant: {response}")
            
            # Display any error (for debugging)
            if result.get("error"):
                print(f"\n[Debug] Error: {result['error']}")
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("An unexpected error occurred while processing your query.")
            
        print("-" * 80)

if __name__ == "__main__":
    main()