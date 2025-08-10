#!/usr/bin/env python3
"""
Test script for the teacher agent.

This script allows testing the teacher agent locally before deployment.
It simulates a conversation by accepting user input and displaying agent responses,
along with the tracked knowledge state.

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
    from tutor.teacher_agent.agent import process_query
except ImportError as e:
    print(f"Error importing the teacher agent: {e}")
    print("Make sure you've set up the project structure correctly.")
    sys.exit(1)

def display_knowledge_state(knowledge_state: Dict[str, Any]) -> None:
    """Display the student's knowledge state in a readable format."""
    if not knowledge_state:
        print("\n[No knowledge state available yet]")
        return
        
    print("\n--- Student Knowledge State ---")
    
    # Display overall mastery level
    mastery_level = knowledge_state.get("mastery_level", "Not assessed")
    print(f"Overall Mastery: {mastery_level.capitalize()}")
    
    # Display topics and understanding levels
    topics = knowledge_state.get("topics", [])
    if topics:
        print("\nTopics:")
        for topic in topics:
            # Handle both formats: {"name": "x", "understanding": 3} and direct string entries
            if isinstance(topic, dict):
                topic_name = topic.get("name", "Unknown")
                understanding = topic.get("understanding", "?")
                print(f"  - {topic_name}: Level {understanding}/5")
            else:
                print(f"  - {topic}")
    
    # Display misconceptions
    misconceptions = knowledge_state.get("misconceptions", [])
    if misconceptions:
        print("\nPotential Misconceptions/Gaps:")
        for item in misconceptions:
            print(f"  - {item}")
    
    # Display recommended focus areas
    focus_areas = knowledge_state.get("recommended_focus", [])
    if focus_areas:
        print("\nRecommended Focus Areas:")
        for area in focus_areas:
            print(f"  - {area}")
    
    print("-" * 30)

def main():
    """Run an interactive test session with the teacher agent."""
    print("=" * 80)
    print("Teacher Agent (Content & Concept Specialist) Test Console")
    print("=" * 80)
    print("Type your questions about course content, or 'exit' to quit.")
    print("This agent will track your knowledge state and provide educational guidance.")
    print("-" * 80)
    
    # Create a unique session ID for this conversation
    session_id = str(uuid.uuid4())
    message_history = []
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Check for exit command
        if user_input.lower() in ("exit", "quit", "bye"):
            print("\nThank you for testing the teacher agent!")
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
            knowledge_state = result.get("knowledge_state", {})
            
            # Display the response
            print(f"\nTeacher: {response}")
            
            # Display knowledge state
            display_knowledge_state(knowledge_state)
            
            # Display any error (for debugging)
            if result.get("error"):
                print(f"\n[Debug] Error: {result['error']}")
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("An unexpected error occurred while processing your query.")
            
        print("-" * 80)

if __name__ == "__main__":
    main()