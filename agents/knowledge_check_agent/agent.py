"""
Knowledge Check Agent

This module implements a Knowledge Check Agent that generates
multiple choice quizzes about various computer science topics
and evaluates user responses.
"""

import json
from typing import Dict, List, Any, Optional
import openai
from openai import OpenAI
import os

from .prompts import (
    GENERATE_QUESTIONS_SYSTEM_PROMPT,
    GENERATE_QUESTIONS_USER_PROMPT,
    EVALUATE_RESPONSE_SYSTEM_PROMPT,
    EVALUATE_RESPONSE_USER_PROMPT
)
from .tools import store_quiz_result, get_user_chapter_stats

# Initialize OpenAI client with fallback
openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
else:
    # Provide mock client functionality for development purposes when no API key is available
    from unittest.mock import MagicMock
    
    # Create a mock OpenAI client
    client = MagicMock()
    
    # Configure the mock to return sample data for completions
    def mock_completion(**kwargs):
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock()]
        mock_resp.choices[0].message = MagicMock()
        
        # Different responses based on the provided system content
        if kwargs.get('messages', [{}])[0].get('content', '').startswith('You are a computer science quiz generator'):
            # Response for generate_questions
            mock_resp.choices[0].message.content = json.dumps({
                "questions": [
                    {
                        "question": "What is a variable in programming?",
                        "options": ["A container for storing data values", "A fixed value", "A programming language", "A function"],
                        "correctIndex": 0,
                        "explanation": "A variable is a named storage location in a program that contains a value."
                    }
                ]
            })
        else:
            # Response for evaluate_text_response
            mock_resp.choices[0].message.content = json.dumps({
                "strengths": "Good understanding of basic concepts",
                "weaknesses": "Some details missing",
                "suggestions": "Consider elaborating more on the core principles",
                "totalScore": 7
            })
        
        return mock_resp
    
    # Set up the chat.completions.create method to use our mock_completion function
    client.chat.completions.create = mock_completion
    
    print("WARNING: OPENAI_API_KEY not set. Using mock OpenAI client with sample responses.")

# Define chapter topics with more specific details to improve question quality
CHAPTER_TOPICS = {
    'chapter-1': 'Introduction to Computer Science and Programming - including computational thinking, algorithms, pseudocode, and basic programming concepts like variables, data types, operators, and control structures',
    'chapter-2': 'Basic Data Structures and Algorithms - including arrays, linked lists, stacks, queues, searching, sorting, and algorithm complexity (Big O notation)',
    'chapter-3': 'Object-Oriented Programming Principles - including classes, objects, inheritance, polymorphism, encapsulation, abstraction, and design patterns',
    'chapter-4': 'Web Development Fundamentals - including HTML, CSS, JavaScript, DOM manipulation, RESTful APIs, client-server architecture, and responsive design',
    'chapter-5': 'Database Design and SQL - including relational database concepts, ER diagrams, normalization, SQL queries, transactions, and indexing',
    'chapter-6': 'Computer Networks and Security - including OSI model, TCP/IP, routing, DNS, encryption, authentication, firewalls, and common security vulnerabilities',
    'chapter-7': 'Software Engineering Practices - including software development life cycle, requirements engineering, testing strategies, version control, agile methodologies, and DevOps',
    'chapter-8': 'Artificial Intelligence and Machine Learning Basics - including supervised/unsupervised learning, neural networks, natural language processing, computer vision, and ethical considerations',
    'chapter-9': 'Operating Systems and Computer Architecture - including processes, threads, memory management, file systems, CPU scheduling, and computer organization',
    'chapter-10': 'Modern Software Development Tools and Practices - including cloud computing, containerization, microservices, CI/CD pipelines, and test-driven development'
}

def generate_questions(chapter_id: str, num_questions: int = 10) -> List[Dict[str, Any]]:
    """
    Generate multiple choice questions for a specific chapter.
    
    Args:
        chapter_id: The chapter ID (e.g., 'chapter-1')
        num_questions: Number of questions to generate (default: 10)
        
    Returns:
        List of question objects
    """
    # Get the topic for this chapter
    topic = CHAPTER_TOPICS.get(chapter_id, 'Computer Science')
    
    # Create prompts
    system_prompt = GENERATE_QUESTIONS_SYSTEM_PROMPT.format(
        num_questions=num_questions,
        topic=topic
    )
    
    user_prompt = GENERATE_QUESTIONS_USER_PROMPT.format(
        num_questions=num_questions,
        topic=topic
    )
    
    try:
        # Generate questions using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,  # Lower temperature for more focused output
            response_format={"type": "json_object"},
            max_tokens=4000  # Ensure enough space for detailed questions and explanations
        )
        
        # Parse the response
        content = response.choices[0].message.content
        questions_data = json.loads(content)
        
        # Extract questions from the response
        if 'questions' in questions_data:
            # If the model wrapped the questions in a 'questions' field
            questions = questions_data['questions']
        elif isinstance(questions_data, list):
            # If the model returned the questions as a list
            questions = questions_data
        else:
            # If the model returned the questions in some other format
            questions = questions_data.get('questions', [])
            
        # Ensure we have the right number of questions
        questions = questions[:num_questions]
        
        return questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        # Return some default questions if generation fails
        return [
            {
                "question": f"Sample question {i} about {topic}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correctIndex": 0,
                "explanation": "This is a sample explanation."
            }
            for i in range(num_questions)
        ]

def score_quiz(
    user_id: str,
    chapter_id: str,
    user_answers: List[int],
    questions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Score a completed quiz and store the results.
    
    Args:
        user_id: The user's ID
        chapter_id: The chapter ID
        user_answers: List of user's answer indices
        questions: List of question objects with correct answers
        
    Returns:
        Dict containing score results
    """
    # Count correct answers
    correct_count = 0
    question_count = len(questions)
    
    for i, user_answer in enumerate(user_answers):
        if i < len(questions):
            correct_index = questions[i].get('correctIndex')
            if user_answer == correct_index:
                correct_count += 1
    
    # Calculate score as percentage
    percentage = (correct_count / question_count) * 100 if question_count > 0 else 0
    
    # Store result in DynamoDB
    storage_result = store_quiz_result(
        user_id=user_id,
        chapter_id=chapter_id,
        score=correct_count,
        question_count=question_count,
        answers=user_answers
    )
    
    # Get user's stats for this chapter
    stats = get_user_chapter_stats(user_id, chapter_id)
    
    # Prepare detailed results
    results = {
        'userId': user_id,
        'chapterId': chapter_id,
        'correct': correct_count,
        'total': question_count,
        'percentage': percentage,
        'userAnswers': user_answers,
        'storage': storage_result,
        'stats': stats.get('data', {})
    }
    
    return results

def evaluate_text_response(
    user_id: str,
    topic: str,
    prompt: str,
    response: str
) -> Dict[str, Any]:
    """
    Evaluate a user's written response to a knowledge check prompt.
    
    Args:
        user_id: The user's ID
        topic: The topic of the prompt
        prompt: The knowledge check prompt
        response: The user's written response
        
    Returns:
        Dict containing evaluation results
    """
    # Create prompts
    system_prompt = EVALUATE_RESPONSE_SYSTEM_PROMPT.format(
        topic=topic,
        prompt=prompt
    )
    
    user_prompt = EVALUATE_RESPONSE_USER_PROMPT.format(
        prompt=prompt,
        response=response
    )
    
    try:
        # Generate evaluation using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        content = response.choices[0].message.content
        evaluation = json.loads(content)
        
        # Store the evaluation in DynamoDB (could be implemented later)
        # store_text_evaluation(user_id, topic, prompt, response, evaluation)
        
        return {
            'success': True,
            'data': evaluation
        }
    except Exception as e:
        print(f"Error evaluating response: {e}")
        return {
            'success': False,
            'message': f'Error evaluating response: {str(e)}'
        }

def process_query(
    query: str,
    session_id: str,
    message_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Process a query to the Knowledge Check Agent.
    
    This function handles different types of queries:
    - Generate quiz questions for a chapter
    - Score a completed quiz
    - Evaluate a text response
    
    Args:
        query: The query string or JSON string with parameters
        session_id: The session ID
        message_history: Optional message history
        
    Returns:
        Dict containing the agent's response
    """
    try:
        # Try to parse the query as JSON
        params = json.loads(query)
        
        # Determine the action based on the parameters
        action = params.get('action')
        
        if action == 'generate_questions':
            chapter_id = params.get('chapter_id')
            num_questions = params.get('num_questions', 10)
            
            questions = generate_questions(chapter_id, num_questions)
            
            return {
                'response': 'Questions generated successfully',
                'data': {
                    'questions': questions,
                    'chapterId': chapter_id
                },
                'message_history': message_history or []
            }
            
        elif action == 'score_quiz':
            user_id = params.get('user_id')
            chapter_id = params.get('chapter_id')
            user_answers = params.get('answers', [])
            questions = params.get('questions', [])
            
            results = score_quiz(user_id, chapter_id, user_answers, questions)
            
            return {
                'response': f'Quiz scored: {results["correct"]}/{results["total"]} correct ({results["percentage"]}%)',
                'data': results,
                'message_history': message_history or []
            }
            
        elif action == 'evaluate_text':
            user_id = params.get('user_id')
            topic = params.get('topic')
            prompt = params.get('prompt')
            response_text = params.get('response')
            
            evaluation = evaluate_text_response(user_id, topic, prompt, response_text)
            
            return {
                'response': f'Response evaluated. Score: {evaluation["data"]["totalScore"]}/10',
                'data': evaluation,
                'message_history': message_history or []
            }
            
        else:
            return {
                'response': 'Unknown action. Supported actions: generate_questions, score_quiz, evaluate_text',
                'message_history': message_history or []
            }
            
    except json.JSONDecodeError:
        # If the query is not JSON, treat it as a simple text query
        return {
            'response': 'Please send a properly formatted JSON query with an action parameter',
            'message_history': message_history or []
        }
    except Exception as e:
        return {
            'response': f'Error processing query: {str(e)}',
            'message_history': message_history or []
        }