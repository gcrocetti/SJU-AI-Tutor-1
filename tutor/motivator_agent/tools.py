"""
Tools for the Motivator Agent (Emotional Support Specialist).

This module provides specialized tools for emotional assessment,
intervention decisions, and conversation history formatting.
"""

import logging
from typing import List, Dict, Any, Tuple

# Set up logging
logger = logging.getLogger(__name__)

def assess_distress_level(assessment: Dict[str, Any]) -> Tuple[int, str]:
    """
    Determine the level of distress and type of intervention needed based on emotional assessment.
    
    Args:
        assessment: Dictionary containing emotional assessment data
        
    Returns:
        Tuple of (distress_level, intervention_type)
        Distress levels:
        - 0: None needed
        - 1: Mild support
        - 2: Moderate support
        - 3: Urgent support
    """
    # Initialize distress level
    distress_level = 0
    
    try:
        # Check for suicide or self-harm risk indicators in query or assessment
        # These terms immediately trigger highest level intervention
        if assessment.get("requires_intervention", False):
            distress_level = 3
            return distress_level, "urgent"
        
        # Check risk factors for emergency indicators
        risk_factors = assessment.get("risk_factors", [])
        primary_concern = assessment.get("primary_concern", "").lower()
        mood = assessment.get("mood", "").lower()
        
        # Emergency terms that should trigger highest level intervention
        emergency_terms = [
            "suicide", "kill myself", "end my life", "don't want to live", 
            "hurt myself", "self-harm", "die", "better off dead",
            "no point", "can't go on", "won't be around", "something drastic"
        ]
        
        # Check risk factors, mood, and primary concern for emergency terms
        for term in emergency_terms:
            # Check in risk factors (could be a list or a string)
            if isinstance(risk_factors, list):
                if any(term in factor.lower() for factor in risk_factors):
                    distress_level = 3
                    return distress_level, "urgent"
            elif isinstance(risk_factors, str) and term in risk_factors.lower():
                distress_level = 3
                return distress_level, "urgent"
                
            # Check in primary concern
            if term in primary_concern:
                distress_level = 3
                return distress_level, "urgent"
                
            # Check in mood
            if term in mood:
                distress_level = 3
                return distress_level, "urgent"
            
        # Check stress level
        stress_level = assessment.get("stress_level", 0)
        if stress_level >= 8:
            distress_level = max(distress_level, 2)
        elif stress_level >= 6:
            distress_level = max(distress_level, 1)
            
        # Check confidence level
        confidence_level = assessment.get("confidence_level", 10)
        if confidence_level <= 3:
            distress_level = max(distress_level, 2)
        elif confidence_level <= 5:
            distress_level = max(distress_level, 1)
            
        # Check for concerning mood indicators
        high_concern_moods = ["hopeless", "despairing", "suicidal", "worthless", "desperate"]
        medium_concern_moods = ["depressed", "overwhelmed", "anxious", "panicked", "devastated"]
        
        if any(concern in mood for concern in high_concern_moods):
            distress_level = max(distress_level, 3)
        elif any(concern in mood for concern in medium_concern_moods):
            distress_level = max(distress_level, 2)
            
        # Check risk factors count
        if isinstance(risk_factors, list):
            if len(risk_factors) >= 3:
                distress_level = max(distress_level, 3)  # Increased from 2 to 3
            elif len(risk_factors) >= 1:
                distress_level = max(distress_level, 2)  # Increased from 1 to 2
            
        # Determine intervention type based on distress level
        if distress_level == 3:
            intervention_type = "urgent"
        elif distress_level == 2:
            intervention_type = "moderate"
        elif distress_level == 1:
            intervention_type = "mild"
        else:
            intervention_type = "none"
            
        return distress_level, intervention_type
        
    except Exception as e:
        logger.error(f"Error assessing distress level: {e}")
        return 0, "none"


def format_interaction_history(messages: List[Dict[str, Any]]) -> str:
    """
    Format conversation history for emotional assessment.
    
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
            formatted_history.append(f"Support Specialist: {content}")
            
    return "\n\n".join(formatted_history)


def get_campus_resources(use_university_agent: bool = False, session_id: str = None) -> Dict[str, str]:
    """
    Retrieve campus mental health and support resources.
    
    Args:
        use_university_agent: Whether to use the university agent to fetch resources
        session_id: Session ID for the university agent (required if use_university_agent is True)
        
    Returns:
        Dictionary of resource names and contact information
    """
    # Always include these national resources
    resources = {
        "Crisis Text Line": "Text HOME to 741741 | Available 24/7",
        "National Suicide Prevention Lifeline": "988 or 1-800-273-8255 | Available 24/7"
    }
    
    # If we're not using the university agent or no session_id provided, use default resources
    if not use_university_agent or not session_id:
        # Add default campus resources
        default_campus_resources = {
            "University Counseling Center": "Contact your university's counseling center for support",
            "Campus Health Services": "Visit your campus health services for assistance",
            "Academic Success Center": "Check with your university's academic success center for resources"
        }
        resources.update(default_campus_resources)
        return resources
        
    # Use university agent to get campus-specific resources
    try:
        from tutor.university_agent.agent import process_query as university_query
        
        # Create targeted queries for different types of campus resources
        resource_queries = [
            "What are the contact details and hours for the university counseling center?",
            "What mental health resources are available on campus?",
            "What academic support services does the university offer?",
            "How can students access health services on campus?"
        ]
        
        # Query the university agent for each resource type
        campus_resources = {}
        for query in resource_queries:
            # Use empty message history to get direct factual responses
            result = university_query(query, session_id, [])
            if result and "response" in result:
                # Extract resource information from the response
                # Parse the response to identify resources and their details
                response = result["response"]
                lines = response.split('\n')
                
                # Look for resource patterns (resource name followed by contact details)
                for line in lines:
                    # Simple heuristic to identify resource information
                    if ':' in line and len(line) > 10:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            name = parts[0].strip()
                            details = parts[1].strip()
                            if name and details and len(name) < 50:  # Reasonable resource name length
                                campus_resources[name] = details
                
        # If we found campus resources, add them to the results
        if campus_resources:
            resources.update(campus_resources)
        
        return resources
        
    except Exception as e:
        # Log the error but continue with default resources
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching campus resources from university agent: {e}")
        
        # Add default campus resources as fallback
        default_campus_resources = {
            "University Counseling Center": "Contact your university's counseling center for support",
            "Campus Health Services": "Visit your campus health services for assistance",
            "Academic Success Center": "Check with your university's academic success center for resources"
        }
        resources.update(default_campus_resources)
        return resources


def check_for_emergency_terms(text: str) -> bool:
    """
    Check if message contains emergency terms that require immediate attention.
    This function catches direct mentions of self-harm, suicide, or severe distress.
    
    Args:
        text: Message text to check
        
    Returns:
        True if emergency terms are detected, False otherwise
    """
    # In order to ensure students in crisis are identified adequately, we need to capture some emergency terms
    emergency_terms = [
        "kill myself", "suicide", "suicidal", "end my life", "don't want to live", 
        "hurt myself", "self-harm", "die", "better off dead", "take my own life",
        "no point in living", "can't go on", "won't be around", "not worth living",
        "ending it all", "want to die", "going to end it", "not worth it",
        "do something drastic", "harm myself", "not be here", "putting an end to",
        "take my life", "life is pointless", "can't handle it anymore", "rather be dead"
    ]
    
    text_lower = text.lower()
    
    # Check for direct mentions of emergency terms
    if any(term in text_lower for term in emergency_terms):
        return True
        
    # Check for more subtle indicators with contextual awareness
    subtle_indicators = [
        "goodbye forever", "last message", "final note", "won't be here tomorrow",
        "can't take this anymore", "giving up", "no way out", "too much to handle",
        "nobody would miss me", "they'd be better off without me", "just want it to end",
        "no hope", "nothing to live for", "what's the point", "no future"
    ]
    
    if any(indicator in text_lower for indicator in subtle_indicators):
        return True
        
    return False