#!/usr/bin/env python3
"""
Simplified test file for the Teacher Agent

This implements a basic version of the teacher agent that doesn't depend on external APIs.
"""

import os
import sys
import json
import uuid
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock data for testing
MOCK_CONTENT = [
    {
        "text": "Object-oriented programming (OOP) is a programming paradigm based on the concept of objects, which can contain data and code. The data is in the form of attributes, and the code is in the form of methods. A key feature of objects is that they can access and modify their own data.",
        "metadata": {
            "source": "Programming Fundamentals Textbook",
            "page": "42",
            "keywords": "OOP, classes, objects, encapsulation, inheritance",
            "categories": "programming, computer science"
        }
    },
    {
        "text": "The four main principles of OOP are encapsulation, abstraction, inheritance, and polymorphism. Encapsulation refers to bundling data and methods together. Abstraction means hiding complex implementation details. Inheritance allows a class to inherit properties from another class. Polymorphism enables using a single interface for different data types.",
        "metadata": {
            "source": "Advanced Programming Concepts",
            "page": "78",
            "keywords": "polymorphism, inheritance, encapsulation, abstraction",
            "categories": "programming, design patterns"
        }
    }
]

def process_query(query: str, session_id: str, message_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Process a user query - simplified version for testing.
    
    Args:
        query: The user's question
        session_id: Unique identifier for the conversation session
        message_history: Previous messages in the conversation
        
    Returns:
        Dict containing the agent's response and updated conversation history
    """
    # Initialize message history if not provided
    if message_history is None:
        message_history = []
    
    # Add the current query to message history
    message_history.append({"role": "user", "content": query})
    
    try:
        # Generate a response based on the query
        query_lower = query.lower()
        
        # Track student knowledge
        topics = []
        if "object" in query_lower and "programming" in query_lower:
            topics.append({"name": "object-oriented programming", "understanding": 2})
        elif "neural" in query_lower:
            topics.append({"name": "neural networks", "understanding": 2})
        else:
            topics.append({"name": "general concepts", "understanding": 2})
            
        # Check for confusion or misconceptions
        misconceptions = []
        if "confused" in query_lower or "don't understand" in query_lower:
            misconceptions.append("Possible confusion about core concepts")
            
        # Create knowledge state
        knowledge_state = {
            "topics": topics,
            "misconceptions": misconceptions,
            "mastery_level": "beginner",
            "recommended_focus": ["Basic concepts", "Practical examples"]
        }
        
        # Generate response based on query content
        if "object" in query_lower and "programming" in query_lower:
            response = """Object-oriented programming (OOP) is a programming paradigm based on the concept of "objects", which can contain data and code.

Let me break down the key concepts for you:

1. Classes and Objects: A class is like a blueprint for creating objects. Objects are instances of classes.

2. Encapsulation: This principle bundles the data (attributes) and methods (functions) together within a class and restricts access to some of the object's components.

3. Inheritance: This allows you to create a new class that is a modified version of an existing class.

4. Polymorphism: This allows objects of different classes to be treated as objects of a common superclass.

[Source: Programming Fundamentals, Page 42]

Would you like me to explain any of these concepts in more detail? Or perhaps you'd like to see an example of a simple class implementation?"""
        elif "neural" in query_lower and "network" in query_lower:
            response = """Neural networks are computing systems inspired by the biological neural networks in animal brains. Here are the fundamentals:

1. Neurons: Basic units that receive inputs, apply weights, and output a signal
2. Layers: Networks typically have input, hidden, and output layers
3. Weights: Connections between neurons have weights that adjust during learning
4. Activation Functions: Functions that determine if and how strongly a neuron fires

[Source: Machine Learning Fundamentals, Page 15]

What specific aspect of neural networks would you like to understand better?"""
        else:
            response = """I'd be happy to help you understand this concept. Let me explain the fundamentals and provide some examples.

The key principles are:
1. First, understand the basic definitions
2. Second, look at how these components interact
3. Finally, see how they're applied in real-world scenarios

[Source: Course Materials, Page 15]

What specific questions do you have about this topic? Would you like me to provide more concrete examples?"""
        
        # Add the response to message history
        message_history.append({"role": "assistant", "content": response})
        
        return {
            "response": response,
            "message_history": message_history,
            "knowledge_state": knowledge_state,
            "error": None
        }
        
    except Exception as e:
        error_message = f"I'm sorry, but I encountered an error while processing your query: {str(e)}"
        logger.error(f"Error processing query: {e}")
        
        # Add error response to message history
        message_history.append({"role": "assistant", "content": error_message})
        
        return {
            "response": error_message,
            "message_history": message_history,
            "knowledge_state": {},
            "error": str(e)
        }

# Test the function directly
if __name__ == "__main__":
    # Test queries
    test_queries = [
        "Can you help me understand object-oriented programming?",
        "I'm confused about neural networks, can you explain them?",
        "What's the difference between a class and an object?",
        "exit"  # Special command to exit
    ]
    
    # Create session
    session_id = str(uuid.uuid4())
    message_history = []
    
    print("=" * 80)
    print("Teacher Agent (Content & Concept Specialist) Test Console")
    print("=" * 80)
    print("Type your questions about course content, or 'exit' to quit.")
    print("-" * 80)
    
    # Interactive loop
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
        result = process_query(user_input, session_id, message_history)
        
        # Extract the response and updated message history
        response = result["response"]
        message_history = result["message_history"]
        knowledge_state = result.get("knowledge_state", {})
        
        # Display the response
        print(f"\nTeacher: {response}")
        
        # Display knowledge state
        print("\n--- Student Knowledge State ---")
        print(f"Topics: {', '.join([topic.get('name', '') for topic in knowledge_state.get('topics', [])])}")
        print(f"Mastery: {knowledge_state.get('mastery_level', 'unknown')}")
        if knowledge_state.get('misconceptions'):
            print(f"Misconceptions: {', '.join(knowledge_state.get('misconceptions', []))}")
        print(f"Focus Areas: {', '.join(knowledge_state.get('recommended_focus', []))}")
        print("-" * 30)
        
        # Display any error
        if result.get("error"):
            print(f"\n[Debug] Error: {result['error']}")
            
        print("-" * 80)