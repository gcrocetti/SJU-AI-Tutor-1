"""
Tools for the Orchestrator Agent (Primary Gatekeeper).

This module provides utility functions for the orchestrator agent, including:
1. Formatting agent descriptions
2. Processing conversation history
3. Analyzing query intents and characteristics
"""

import logging
from typing import List, Dict, Any, Tuple, Set

# Set up logging
logger = logging.getLogger(__name__)

def format_agent_descriptions() -> str:
    """
    Format descriptions of available specialized agents.
    
    Returns:
        Formatted string with agent descriptions
    """
    descriptions = {
        "university": {
            "id": "university",
            "name": "University Information Agent",
            "expertise": "Academic programs, admissions, campus resources, policies, procedures, courses, deadlines",
            "best_for": "Factual questions about university information, procedures, requirements",
            "avoid_for": "Emotional support, motivation, personal well-being issues",
            "example_queries": [
                "What are the requirements for the computer science major?",
                "When is the registration deadline for fall semester?",
                "How do I apply for on-campus housing?",
                "What dining options are available on campus?",
                "Where is the financial aid office located?"
            ]
        },
        
        "motivator": {
            "id": "motivator",
            "name": "Motivator Agent (Emotional Support Specialist)",
            "expertise": "Stress management, motivation, academic anxiety, emotional well-being, confidence building",
            "best_for": "Emotional support, motivation strategies, stress management techniques",
            "avoid_for": "Specific factual information about university policies or procedures",
            "example_queries": [
                "I'm feeling overwhelmed with my coursework",
                "How do I stay motivated during finals?",
                "I'm anxious about my upcoming exams",
                "I'm struggling to balance school and work",
                "I don't feel confident in my abilities"
            ]
        }
    }
    
    formatted_text = []
    for agent_id, agent in descriptions.items():
        formatted_text.append(f"AGENT ID: {agent['id']}")
        formatted_text.append(f"NAME: {agent['name']}")
        formatted_text.append(f"EXPERTISE: {agent['expertise']}")
        formatted_text.append(f"BEST FOR: {agent['best_for']}")
        formatted_text.append(f"AVOID FOR: {agent['avoid_for']}")
        formatted_text.append("EXAMPLE QUERIES:")
        for example in agent['example_queries']:
            formatted_text.append(f"  - \"{example}\"")
        formatted_text.append("")
    
    return "\n".join(formatted_text)


def format_conversation_history(messages: List[Dict[str, Any]]) -> str:
    """
    Format conversation history for query analysis.
    
    Args:
        messages: List of message dictionaries with role and content
        
    Returns:
        Formatted history string
    """
    if not messages:
        return "No previous conversation history."
        
    formatted_history = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        
        if role == "user":
            formatted_history.append(f"Student: {content}")
        elif role == "assistant":
            formatted_history.append(f"Assistant: {content}")
            
    return "\n\n".join(formatted_history)


def identify_emotional_content(text: str) -> Tuple[bool, float]:
    """
    Identify emotional content in text that might suggest the need for motivational support.
    
    Args:
        text: The text to analyze
        
    Returns:
        Tuple of (has_emotional_content, confidence_score)
    """
    # Simple keyword-based detection for emotional terms
    emotional_terms = [
        "stress", "anxious", "anxiety", "worried", "fear", "scared", "overwhelmed",
        "depressed", "sad", "unhappy", "struggling", "tired", "exhausted",
        "frustrated", "angry", "upset", "confused", "lost", "hopeless",
        "motivated", "unmotivated", "confidence", "insecure", "doubt"
    ]
    
    # First-person indicators
    first_person = ["i'm", "im", "i am", "i feel", "i'm feeling", "my", "me", "i"]
    
    # Count occurrences
    text_lower = text.lower()
    emotional_count = sum(term in text_lower for term in emotional_terms)
    first_person_count = sum(term in text_lower for term in first_person)
    
    # Calculate confidence score (simple heuristic)
    # Higher if both emotional terms and first-person indicators are present
    confidence = min(1.0, (emotional_count * 0.3) + (first_person_count * 0.1))
    
    # Determine if emotional content is present
    has_emotional = emotional_count > 0 and first_person_count > 0
    
    return has_emotional, confidence


def identify_university_information_content(text: str) -> Tuple[bool, float]:
    """
    Identify content requesting university information.
    
    Args:
        text: The text to analyze
        
    Returns:
        Tuple of (has_university_content, confidence_score)
    """
    # Simple keyword-based detection for university information terms
    university_terms = [
        "course", "class", "major", "minor", "degree", "program", "requirement",
        "credit", "professor", "instructor", "faculty", "department", "school",
        "college", "campus", "application", "admission", "financial aid", "scholarship",
        "deadline", "date", "schedule", "registration", "enroll", "tuition",
        "fee", "policy", "procedure", "resource", "office", "building", "location"
    ]
    
    # Question indicators
    question_indicators = [
        "what", "how", "when", "where", "who", "why", "which", "can i", 
        "do i need", "is there", "are there", "?", "tell me about"
    ]
    
    # Count occurrences
    text_lower = text.lower()
    university_count = sum(term in text_lower for term in university_terms)
    question_count = sum(indicator in text_lower for indicator in question_indicators)
    
    # Calculate confidence score (simple heuristic)
    confidence = min(1.0, (university_count * 0.2) + (question_count * 0.1))
    
    # Determine if university information is requested
    has_university = university_count > 0
    
    return has_university, confidence


def extract_query_components(text: str) -> Dict[str, Any]:
    """
    Extract key components from a query to help with routing.
    
    Args:
        text: Query text to analyze
        
    Returns:
        Dictionary with extracted components
    """
    components = {
        "emotional_content": False,
        "information_request": False,
        "question_marks_count": text.count("?"),
        "word_count": len(text.split()),
        "suggested_agents": set()
    }
    
    # Check for emotional content
    emotional, emotional_conf = identify_emotional_content(text)
    components["emotional_content"] = emotional
    components["emotional_confidence"] = emotional_conf
    
    if emotional and emotional_conf > 0.3:
        components["suggested_agents"].add("motivator")
    
    # Check for university information content
    information, info_conf = identify_university_information_content(text)
    components["information_request"] = information
    components["information_confidence"] = info_conf
    
    if information and info_conf > 0.2:
        components["suggested_agents"].add("university")
    
    # Convert set to list for serialization
    components["suggested_agents"] = list(components["suggested_agents"])
    
    return components