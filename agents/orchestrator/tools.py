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
            "expertise": "Academic programs, admissions, campus resources, policies, procedures, deadlines",
            "best_for": "Factual questions about university information, procedures, requirements",
            "avoid_for": "Emotional support, motivation, personal well-being issues, ANY syllabus or course content questions",
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
            "avoid_for": "Specific factual information about university policies or procedures, course content or syllabi, study planning and organization",
            "example_queries": [
                "I'm feeling overwhelmed with my coursework",
                "How do I stay motivated during finals?",
                "I'm anxious about my upcoming exams",
                "I'm struggling to balance school and work",
                "I don't feel confident in my abilities"
            ]
        },
        
        "teacher": {
            "id": "teacher",
            "name": "Teacher Agent (Content & Concept Specialist)",
            "expertise": "Course content delivery, syllabus information, supplemental materials, probing questions, lesson reviews, progress tracking",
            "best_for": "Deep learning of course material, understanding concepts, study guidance, content exploration, ALL syllabus and course topics",
            "exclusive_for": "Any syllabus-related queries, course content overview, class topics, discussion topics",
            "avoid_for": "University policies, general university information, emotional support, study planning and time management",
            "example_queries": [
                "Can you help me understand object-oriented programming?",
                "I'm confused about the concept of neural networks",
                "What are the key components of a literature review?",
                "What topics are covered in the syllabus?",
                "What should I be studying for this course?",
                "Can you summarize the main points from today's lecture?",
                "What topics are up for discussion today?",
                "Can you give me an overview of what we're learning?"
            ]
        },
        
        "knowledge_check": {
            "id": "knowledge_check",
            "name": "Knowledge Check Agent (Assessment Specialist)",
            "expertise": "Quiz generation, knowledge assessment, understanding evaluation, learning gap identification",
            "best_for": "Testing knowledge retention, checking understanding of concepts, preparing for exams, identifying knowledge gaps",
            "avoid_for": "Emotional support, university information, detailed concept explanations",
            "example_queries": [
                "Test my knowledge on object-oriented programming",
                "Give me a quiz on data structures",
                "Check my understanding of neural networks",
                "I want to practice with some questions on database design",
                "Can you evaluate what I know about software engineering?"
            ]
        },
        
        "academic_coach": {
            "id": "academic_coach",
            "name": "Academic Coach Agent (Study & Organization Specialist)",
            "expertise": "Study planning, time management, goal setting, academic organization, progress tracking, learning strategy development",
            "best_for": "Creating study plans, developing time management strategies, setting academic goals, organizing study materials, tracking progress",
            "exclusive_for": "Study planning, time management, academic organization, goal setting, tracking progress",
            "avoid_for": "Specific course content explanations, emotional support, university policies and procedures",
            "example_queries": [
                "Help me create a study plan for my computer science course",
                "I need strategies for managing my time better",
                "Can you help me set academic goals for this semester?",
                "I need a better system for organizing my study materials",
                "How can I track my progress in my courses?",
                "What study techniques work best for memorizing formulas?",
                "I keep procrastinating on my assignments",
                "How do I prioritize my studying when I have multiple exams?"
            ]
        }
    }
    
    formatted_text = []
    for agent_id, agent in descriptions.items():
        formatted_text.append(f"AGENT ID: {agent['id']}")
        formatted_text.append(f"NAME: {agent['name']}")
        formatted_text.append(f"EXPERTISE: {agent['expertise']}")
        formatted_text.append(f"BEST FOR: {agent['best_for']}")
        if "exclusive_for" in agent:
            formatted_text.append(f"EXCLUSIVE FOR: {agent['exclusive_for']}")
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


def identify_educational_content(text: str) -> Tuple[bool, float]:
    """
    Identify content requesting educational content or concept explanation.
    
    Args:
        text: The text to analyze
        
    Returns:
        Tuple of (has_educational_content, confidence_score)
    """
    # Keywords related to learning and understanding course content
    educational_terms = [
        "understand", "concept", "explain", "confused", "learning", "learn",
        "help me with", "topic", "subject", "material", "lecture", "textbook",
        "chapter", "homework", "assignment", "problem", "exercise", "quiz", 
        "test", "exam", "study", "practice", "example", "theory", "principle",
        "method", "technique", "formula", "equation", "definition", "summarize",
        "review", "notes", "reading"
    ]
    
    # Terms specific to asking for deeper understanding
    deeper_understanding = [
        "why", "how does", "explain", "help me understand", "confused about",
        "clarify", "don't get", "don't understand", "struggling with", 
        "having trouble with", "what does this mean", "can you help me",
        "elaborate", "more detail", "examples", "simplify"
    ]
    
    # Count occurrences
    text_lower = text.lower()
    educational_count = sum(term in text_lower for term in educational_terms)
    understanding_count = sum(term in text_lower for term in deeper_understanding)
    
    # Calculate confidence score
    confidence = min(1.0, (educational_count * 0.15) + (understanding_count * 0.25))
    
    # Determine if educational content is requested
    has_educational = educational_count > 0 or understanding_count > 0
    
    return has_educational, confidence


def identify_study_planning_content(text: str) -> Tuple[bool, float]:
    """
    Identify content requesting study planning and organization help.
    
    Args:
        text: The text to analyze
        
    Returns:
        Tuple of (has_study_planning_content, confidence_score)
    """
    # Keywords related to study planning and time management
    study_planning_terms = [
        "study plan", "schedule", "time management", "organize", "prioritize",
        "procrastination", "productivity", "focus", "concentration", "distracted",
        "plan", "planning", "goal", "goals", "objective", "target", "track progress",
        "tracking", "method", "strategy", "technique", "approach", "system",
        "balance", "juggle", "manage", "organize", "routine", "habit", "effective",
        "efficient", "productive", "calendar", "timetable", "deadline", "due date",
        "task", "todo", "to-do", "list", "prioritization", "overwhelmed"
    ]
    
    # First-person indicators related to planning
    planning_context = [
        "i need", "i want", "i'm trying", "i am trying", "i'd like", "i would like",
        "how do i", "how can i", "help me", "i have trouble", "i struggle with",
        "i'm struggling with", "my study", "my time", "my goals", "my schedule"
    ]
    
    # Count occurrences
    text_lower = text.lower()
    planning_count = sum(term in text_lower for term in study_planning_terms)
    context_count = sum(term in text_lower for term in planning_context)
    
    # Calculate confidence score
    confidence = min(1.0, (planning_count * 0.2) + (context_count * 0.15))
    
    # Determine if study planning content is requested
    has_planning = planning_count > 0 and context_count > 0
    
    return has_planning, confidence

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
        "educational_content": False,
        "study_planning_content": False,
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
    
    # Check for educational content requests
    educational, edu_conf = identify_educational_content(text)
    components["educational_content"] = educational
    components["educational_confidence"] = edu_conf
    
    if educational and edu_conf > 0.25:
        components["suggested_agents"].add("teacher")
    
    # Check for study planning content
    planning, planning_conf = identify_study_planning_content(text)
    components["study_planning_content"] = planning
    components["study_planning_confidence"] = planning_conf
    
    if planning and planning_conf > 0.3:
        components["suggested_agents"].add("academic_coach")
    
    # Convert set to list for serialization
    components["suggested_agents"] = list(components["suggested_agents"])
    
    return components