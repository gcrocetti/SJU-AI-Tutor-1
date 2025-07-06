"""
Teacher Agent (Content & Concept Specialist)

This module implements a LangGraph-based agent that delivers course content without simply giving away answers.
It provides educational support by:
1. Retrieving relevant course content from Pinecone vector database
2. Delivering supplemental course materials (syllabi, rubrics, PDFs)
3. Asking probing questions to encourage deeper understanding
4. Generating concise lesson reviews and summaries
5. Tracking student progress over time

Refactored for LangChain 0.3+ and LangGraph 0.1+
"""

import os
import json
import logging
import uuid
import re
from typing import Dict, List, Optional, Any, Tuple, TypedDict, Annotated

# LangGraph and LangChain imports - updated for 0.3+
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Import shared utilities
from tutor.common.utils import setup_logging, safe_json_loads
from tutor.teacher_agent.prompts import SYSTEM_PROMPT, QUERY_ANALYSIS_PROMPT
# Import knowledge check evaluation prompts 
from tutor.knowledge_check_agent.prompts import (
    EVALUATE_RESPONSE_SYSTEM_PROMPT, 
    EVALUATE_RESPONSE_USER_PROMPT
)
from tutor.teacher_agent.tools import (
    pinecone_content_retrieval, 
    analyze_content_relevance, 
    generate_probing_questions,
    get_syllabus_topics,
    get_topic_content,
    get_document_names,
    get_syllabus_document_content
)

# Configure logging
logger = logging.getLogger(__name__)
setup_logging()

def extract_numbered_topics(text: str) -> List[str]:
    """
    Extract topics that are presented in a numbered format from text.
    
    Args:
        text: The text containing numbered topics
        
    Returns:
        List of extracted topic names/titles
    """
    topics = []
    
    # Pattern 1: Look for numbered items (1. Topic Name: description)
    numbered_pattern = r'(?:\d+\.|\([0-9]+\)|\*)\s*([^:.]+)(?::|\.)'
    matches = re.findall(numbered_pattern, text)
    if matches:
        for match in matches:
            # Clean up the topic
            topic = match.strip()
            if len(topic) > 3 and len(topic) < 100:  # Reasonable topic length
                topics.append(topic)
    
    # Pattern 2: Look for bold or emphasized topics
    emphasized_pattern = r'\*\*([^*]+)\*\*'
    matches = re.findall(emphasized_pattern, text)
    if matches:
        for match in matches:
            topic = match.strip()
            if len(topic) > 3 and len(topic) < 100 and ":" not in topic and topic not in topics:
                topics.append(topic)
    
    # If still no topics found, try lines that start with capital letters and end with punctuation
    if not topics:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and line[0].isupper() and len(line) < 100 and len(line) > 10:
                # Look for potential topic names at the beginning of sentences
                parts = line.split('.')
                if len(parts) > 1:
                    potential_topic = parts[0].strip()
                    # Check if it looks like a topic (not too long/short, contains nouns)
                    if 3 < len(potential_topic.split()) < 7 and potential_topic not in topics:
                        topics.append(potential_topic)
    
    return topics

def calculate_topic_similarity(topic1: str, topic2: str) -> float:
    """
    Calculate a simple similarity score between two topic strings.
    
    Args:
        topic1: First topic string
        topic2: Second topic string
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    # Convert to lowercase and split into words
    words1 = set(topic1.lower().split())
    words2 = set(topic2.lower().split())
    
    # Remove common stop words
    stop_words = {"a", "an", "the", "and", "or", "but", "is", "are", "of", "for", "in", "to", "with"}
    words1 = words1.difference(stop_words)
    words2 = words2.difference(stop_words)
    
    # Calculate Jaccard similarity
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union

# Define typed state for LangGraph
class AgentState(TypedDict):
    """State maintained throughout the agent's execution."""
    messages: List[Dict[str, Any]]
    session_id: str
    query: str
    needs_content: bool
    content_results: List[Dict[str, Any]]
    student_knowledge_state: Dict[str, Any]  # Tracking student progress/knowledge
    is_knowledge_check: bool  # Whether this is a knowledge check request
    knowledge_check_topic: Optional[str]  # Topic for knowledge check
    knowledge_check_prompt: Optional[str]  # Generated prompt for knowledge check
    knowledge_check_evaluation: Optional[Dict[str, Any]]  # Evaluation results
    final_response: Optional[str]
    error: Optional[str]


# Initialize the LLM
def get_llm(temperature: float = 0.7) -> ChatOpenAI:
    """
    Initialize the OpenAI chat model with specified parameters.
    For testing, returns a mock LLM if no API key is available.
    
    Args:
        temperature: Controls randomness of responses. Lower is more deterministic.
        
    Returns:
        Configured ChatOpenAI instance or mock LLM
    """
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            return ChatOpenAI(
                model="gpt-3.5-turbo-16k",
                temperature=temperature,
                api_key=api_key
            )
        else:
            # For testing, use a simple mock implementation
            logger.info("No API key found, using mock LLM for testing")
            
            # Create a simple mock LLM that returns fixed responses
            from langchain_core.language_models.chat_models import BaseChatModel
            from langchain_core.messages import AIMessage, BaseMessage
            from typing import List, Optional, Any, Dict
            
            class MockChatModel(BaseChatModel):
                def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[Any] = None, **kwargs: Any) -> AIMessage:
                    # Log the received messages for debugging
                    logger.info(f"Mock LLM received {len(messages)} messages")
                    
                    # Get the last user message as the query
                    user_msgs = [msg for msg in messages if msg.type == "human"]
                    if user_msgs:
                        query = user_msgs[-1].content
                    else:
                        query = "No query found"
                    
                    # Generate a simple response based on the query
                    if "object-oriented programming" in query.lower():
                        response = """Object-oriented programming (OOP) is a programming paradigm based on the concept of "objects", which can contain data and code.

Let me break down the key concepts for you:

1. Classes and Objects: A class is like a blueprint for creating objects. Objects are instances of classes.

2. Encapsulation: This principle bundles the data (attributes) and methods (functions) together within a class and restricts access to some of the object's components.

3. Inheritance: This allows you to create a new class that is a modified version of an existing class.

4. Polymorphism: This allows objects of different classes to be treated as objects of a common superclass.

[Source: Programming Fundamentals, Page 42]

Would you like me to explain any of these concepts in more detail? Or perhaps you'd like to see an example of a simple class implementation?"""
                    elif "neural network" in query.lower():
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
                    
                    return AIMessage(content=response)
                
                @property
                def _llm_type(self) -> str:
                    return "mock-chat-model"
                    
                def _combine_llm_outputs(self, llm_outputs: List[Optional[dict]]) -> dict:
                    return {}
                    
            return MockChatModel()
            
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise


def query_analyzer(state: AgentState) -> AgentState:
    """
    Analyze the user query to determine if content retrieval from Pinecone is needed.
    
    Args:
        state: Current agent state containing the user query and conversation history
        
    Returns:
        Updated state with a decision on whether to retrieve content
    """
    llm = get_llm(temperature=0.1)  # Low temperature for more deterministic analysis
    
    # Format conversation history for context
    messages = state["messages"][-5:] if len(state["messages"]) > 5 else state["messages"]
    formatted_history = "\n".join([
        f"User: {msg['content']}" if msg["role"] == "user" else f"Assistant: {msg['content']}" 
        for msg in messages[:-1]  # Exclude the current query
    ])
    
    # Create analysis prompt
    analysis_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=QUERY_ANALYSIS_PROMPT),
        HumanMessage(content=f"""
Conversation history:
{formatted_history}

Current query: {state["query"]}

Do I need to retrieve educational content from the knowledge base to properly answer this query?
""")
    ])
    
    try:
        # Get analysis result using LangChain 0.3+ chain syntax
        chain = analysis_prompt | llm | StrOutputParser()
        result = chain.invoke({})
        
        # Parse decision - look for YES/NO pattern
        needs_content = "YES" in result.upper() and not "NO" in result.upper()
        
        # Update state
        new_state = state.copy()
        new_state["needs_content"] = needs_content
        logger.info(f"Query analysis decided: needs_content={needs_content}")
        
        return new_state
    except Exception as e:
        logger.error(f"Error in query analysis: {e}")
        new_state = state.copy()
        new_state["error"] = f"Failed to analyze query: {str(e)}"
        new_state["needs_content"] = True  # Default to retrieval if analysis fails
        return new_state


def content_retriever(state: AgentState) -> AgentState:
    """
    Retrieve relevant course content from Pinecone vector database.
    This function handles different types of queries, including syllabus overview
    requests and specific topic inquiries, using actual document metadata.
    
    Args:
        state: Current agent state containing the query to search for
        
    Returns:
        Updated state with retrieved content
    """
    try:
        query = state["query"]
        logger.info(f"Retrieving educational content for: {query}")
        
        new_state = state.copy()
        
        # Get available documents for initial context
        syllabus_documents = get_document_names(content_type="syllabus")
        new_state["available_syllabi"] = syllabus_documents
        
        # Check if this is a request about specific course or syllabus
        course_codes = ["CS101", "MATH250", "PHYS201", "ENG301", "BUS220"]
        requested_course = next((code for code in course_codes if code.lower() in query.lower()), None)
        
        if requested_course:
            # Find the matching syllabus document
            matching_syllabus = next((doc for doc in syllabus_documents if requested_course in doc), None)
            
            if matching_syllabus:
                logger.info(f"Retrieving specific course syllabus: {matching_syllabus}")
                syllabus_content = get_syllabus_document_content(matching_syllabus)
                
                # Store the full syllabus content
                new_state["content_results"] = [syllabus_content]
                new_state["is_specific_syllabus"] = True
                new_state["syllabus_document"] = matching_syllabus
                logger.info(f"Retrieved content for syllabus: {matching_syllabus}")
                
        # Check if this is a request for syllabus/course overview
        elif any(keyword in query.lower() for keyword in [
            # Traditional syllabus keywords
            "syllabus", "course overview", "course content", "course topics", 
            "what topics", "what will we cover", "class topics", "overview of topics",
            "available courses", "what courses", "list of courses",
            
            # Student conversational variations
            "topics are up for discussion", "topics for discussion", 
            "material is on the syllabus", "material on the syllabus",
            "topics for this week", "topics this week", "studying",
            "main subjects", "subjects covered", "overview of what we're learning",
            "topics should i focus", "covered in the course", "should i be studying",
            "syllabus for this semester", "key topics", "course outline",
            "subjects included", "summarize what we're learning",
            "what are we learning", "what am i supposed to learn",
            "what's included in this course", "what's on the agenda",
            "what are the areas", "what should we discuss", "topics available"
        ]):
            # Get all available syllabi and their topics
            logger.info("Retrieving overview of all available syllabi")
            
            all_syllabi_content = []
            for syllabus_doc in syllabus_documents[:3]:  # Limit to 3 for performance in real system
                syllabus_content = get_syllabus_document_content(syllabus_doc)
                all_syllabi_content.append(syllabus_content)
            
            # Also get the structured topics
            syllabus_topics = get_syllabus_topics()
            
            # Store both formats for comprehensive overview
            new_state["content_results"] = syllabus_topics
            new_state["syllabi_documents"] = all_syllabi_content
            new_state["is_syllabus_overview"] = True
            logger.info(f"Retrieved {len(syllabus_topics)} syllabus topics across {len(all_syllabi_content)} courses")
            
        # Check if this is a request for a specific topic from any syllabus
        else:
            # Get all syllabus topics first
            syllabus_topics = get_syllabus_topics()
            
            # Check for follow-up queries that reference topics from previous messages
            follow_up_reference = False
            conversation_topics = []
            referenced_topic = None
            
            # Detect references to "first topic", "second topic", etc. or "topic one", "topic two", etc.
            topic_references = {
                "first": 0, "1": 0, "one": 0,
                "second": 1, "2": 1, "two": 1,
                "third": 2, "3": 2, "three": 2,
                "fourth": 3, "4": 3, "four": 3,
                "fifth": 4, "5": 4, "five": 4
            }
            
            # Look for references to numbered topics
            for ref_word, index in topic_references.items():
                if f"{ref_word} topic" in query.lower() or f"topic {ref_word}" in query.lower():
                    follow_up_reference = True
                    
                    # Check previous assistant messages for topic lists
                    if len(state["messages"]) > 2:
                        for msg in reversed(state["messages"][:-1]):  # Skip current query
                            if msg["role"] == "assistant" and any(kw in msg["content"].lower() for kw in ["topic", "syllabus", "course content"]):
                                # Found previous message with topic information
                                conversation_topics = extract_numbered_topics(msg["content"])
                                if len(conversation_topics) > index:
                                    referenced_topic = conversation_topics[index]
                                    logger.info(f"Follow-up reference to topic '{referenced_topic}' detected")
                                break
                    break
            
            # Look for direct references to "diving into" topics
            dive_keywords = ["dive into", "discuss", "talk about", "learn about", "tell me about", "explore"]
            if any(kw in query.lower() for kw in dive_keywords) and not referenced_topic:
                # Check if a previous message had topic information
                if len(state["messages"]) > 2:
                    for msg in reversed(state["messages"][:-1]):  # Skip current query
                        if msg["role"] == "assistant" and any(kw in msg["content"].lower() for kw in ["topic", "syllabus", "course content"]):
                            # Found previous message with topic information
                            conversation_topics = extract_numbered_topics(msg["content"])
                            if conversation_topics:
                                referenced_topic = conversation_topics[0]  # Default to first topic
                                logger.info(f"Follow-up dive request to topic '{referenced_topic}' detected")
                            break
            
            # Handle follow-up reference if found
            if referenced_topic:
                # Search for the referenced topic in syllabus topics
                matched_topics = []
                for topic_data in syllabus_topics:
                    # More flexible matching for conversation-extracted topics
                    if (referenced_topic.lower() in topic_data["topic"].lower() or 
                        any(word in topic_data["topic"].lower() for word in referenced_topic.lower().split() if len(word) > 3)):
                        matched_topics.append(topic_data)
                
                # If no direct match, find the most similar topic
                if not matched_topics:
                    for topic_data in syllabus_topics:
                        # Calculate similarity between referenced topic and each syllabus topic
                        similarity = calculate_topic_similarity(referenced_topic, topic_data["topic"])
                        if similarity > 0.5:  # Threshold for considering it a match
                            topic_data["similarity"] = similarity
                            matched_topics.append(topic_data)
                    
                    # Sort by similarity if we have matches
                    if matched_topics:
                        matched_topics.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            
            # Check if query matches any specific syllabus topic
            if not matched_topics:
                for topic_data in syllabus_topics:
                    topic = topic_data["topic"]
                    if topic.lower() in query.lower() or any(keyword in query.lower() for keyword in topic.lower().split()):
                        matched_topics.append(topic_data)
            
            if matched_topics:
                # Found specific topic matches
                primary_topic = matched_topics[0]["topic"]
                logger.info(f"Retrieving detailed content for syllabus topic: {primary_topic}")
                
                # Get source syllabus for this topic
                source_syllabus = matched_topics[0]["source"]
                syllabus_content = get_syllabus_document_content(source_syllabus)
                
                # Get topic-specific content
                topic_content = get_topic_content(primary_topic)
                
                # Combine with general content
                general_content = pinecone_content_retrieval(primary_topic)  # Use the specific topic, not the ambiguous query
                all_content = topic_content + general_content
                
                # Analyze relevance of combined content
                relevant_content = analyze_content_relevance(primary_topic, all_content)
                
                # Store all the context
                new_state["content_results"] = relevant_content
                new_state["matched_syllabus_topics"] = matched_topics
                new_state["source_syllabus"] = syllabus_content
                new_state["primary_topic"] = primary_topic
                new_state["is_follow_up_reference"] = follow_up_reference
                new_state["referenced_topic"] = referenced_topic
                logger.info(f"Retrieved information for topic: {primary_topic} from {source_syllabus}")
            else:
                # No specific topic match, perform general content retrieval
                content_results = pinecone_content_retrieval(query)
                relevant_content = analyze_content_relevance(query, content_results)
                new_state["content_results"] = relevant_content
                logger.info(f"Retrieved {len(relevant_content)} general content items")
        
        return new_state
    except Exception as e:
        logger.error(f"Error retrieving content: {e}")
        new_state = state.copy()
        new_state["error"] = f"Failed to retrieve content: {str(e)}"
        new_state["content_results"] = []  # Empty results on error
        return new_state


def detect_knowledge_check_request(query: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Detect if a query is requesting a knowledge check and extract the topic.
    
    Args:
        query: The user query to analyze
        
    Returns:
        Tuple of (is_knowledge_check, topic, prompt)
    """
    # Keywords that indicate a knowledge check request
    knowledge_check_keywords = [
        "check my knowledge", "test my knowledge", "evaluate my knowledge",
        "assess my understanding", "test my understanding", "quiz me", "test me",
        "knowledge check", "how well do i understand", "check if i know",
        "evaluate what i know", "see if i understand", "check my mastery"
    ]
    
    # Check if any knowledge check keyword is in the query
    is_knowledge_check = any(keyword in query.lower() for keyword in knowledge_check_keywords)
    
    if not is_knowledge_check:
        return (False, None, None)
    
    # Try to extract the topic from the query
    # Common patterns:
    # - "Check my knowledge on [topic]"
    # - "Test me on [topic]"
    # - "Can you evaluate my understanding of [topic]?"
    
    # Get the LLM for topic extraction
    llm = get_llm(temperature=0.1)
    
    topic_extraction_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""
        You are an expert at extracting specific topics from knowledge check requests.
        Given a query asking for a knowledge check, identify the specific topic the user wants to be tested on.
        If no specific topic is mentioned, identify the most likely topic based on recent conversation context if provided.
        If you can't determine a specific topic, return "general".
        
        Return your answer as a JSON object with these fields:
        - topic: The specific subject or concept to test (e.g., "object-oriented programming", "neural networks")
        - prompt: A specific knowledge check question about this topic that requires a detailed explanation (not a yes/no or multiple choice)
        """),
        HumanMessage(content=f"Query: {query}")
    ])
    
    try:
        # Extract topic using LLM
        chain = topic_extraction_prompt | llm | JsonOutputParser()
        result = chain.invoke({})
        
        topic = result.get("topic", "general")
        prompt = result.get("prompt", f"Please explain your understanding of {topic}.")
        
        return (True, topic, prompt)
    except Exception as e:
        logger.error(f"Error extracting knowledge check topic: {e}")
        return (True, "general", "Please explain your understanding of this topic.")

def track_student_knowledge(state: AgentState) -> AgentState:
    """
    Track student knowledge and detect knowledge check requests.
    
    Args:
        state: Current agent state containing conversation history
        
    Returns:
        Updated state with knowledge tracking information
    """
    new_state = state.copy()
    
    # Create basic knowledge state
    new_state["student_knowledge_state"] = {
        "topics": [{"name": "topic", "understanding": 3}],
        "mastery_level": "intermediate",
        "recommended_focus": ["Natural conversation", "Critical thinking"]
    }
    
    # Set default knowledge check fields
    new_state["is_knowledge_check"] = False
    new_state["knowledge_check_topic"] = None
    new_state["knowledge_check_prompt"] = None
    new_state["knowledge_check_evaluation"] = None
    
    # Check if this is a knowledge check request
    is_knowledge_check, topic, prompt = detect_knowledge_check_request(state["query"])
    if is_knowledge_check:
        logger.info(f"Detected knowledge check request on topic: {topic}")
        new_state["is_knowledge_check"] = True
        new_state["knowledge_check_topic"] = topic
        new_state["knowledge_check_prompt"] = prompt
    
    return new_state


def evaluate_free_response(
    topic: str,
    prompt: str,
    response_text: str,
    user_id: str = "anonymous"
) -> Dict[str, Any]:
    """
    Evaluate a user's free-text response to a knowledge check.
    
    Args:
        topic: The topic being assessed
        prompt: The knowledge check prompt
        response_text: The user's written response
        user_id: Identifier for the user (email or unique ID)
        
    Returns:
        Dict containing evaluation results
    """
    try:
        # Use the knowledge check agent's evaluation prompts
        system_prompt = EVALUATE_RESPONSE_SYSTEM_PROMPT.format(
            topic=topic,
            prompt=prompt
        )
        
        user_prompt = EVALUATE_RESPONSE_USER_PROMPT.format(
            prompt=prompt,
            response=response_text
        )
        
        # Get the LLM for evaluation (lower temperature for consistent evaluations)
        llm = get_llm(temperature=0.3)
        
        # Create the evaluation prompt
        evaluation_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # Generate the evaluation
        chain = evaluation_prompt | llm | JsonOutputParser()
        evaluation = chain.invoke({})
        
        # Store the evaluation in DynamoDB (future implementation)
        from datetime import datetime
        
        storage_data = {
            "userId": user_id,
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response_text[:500],  # Store truncated response
            "scores": evaluation.get("scores", {}),
            "totalScore": evaluation.get("totalScore", 0),
            "feedback": evaluation.get("feedback", "")
        }
        
        logger.info(f"Knowledge check completed for user {user_id} on topic {topic}, score: {evaluation.get('totalScore', 0)}")
        
        return {
            'success': True,
            'data': evaluation
        }
    except Exception as e:
        logger.error(f"Error evaluating response: {e}")
        
        # Return a fallback evaluation
        fallback_evaluation = {
            "scores": {
                "accuracy": 2,
                "depth": 2,
                "clarity": 1,
                "application": 1
            },
            "totalScore": 6,
            "feedback": "I had trouble generating a detailed evaluation. Your response shows some understanding of the topic."
        }
        
        return {
            'success': False,
            'data': fallback_evaluation,
            'message': f'Error evaluating response: {str(e)}'
        }

def process_knowledge_check_response(
    topic: str,
    prompt: str,
    response_text: str,
    user_id: str = "anonymous"
) -> Dict[str, Any]:
    """
    Process a student's response to a knowledge check.
    
    Args:
        topic: The topic being assessed
        prompt: The original knowledge check prompt
        response_text: The student's answer
        user_id: The user's identifier
        
    Returns:
        Dict containing the evaluation and response message
    """
    # Evaluate the response
    evaluation_result = evaluate_free_response(topic, prompt, response_text, user_id)
    evaluation = evaluation_result.get('data', {})
    
    # Create a detailed feedback message
    feedback_template = f"""
    Topic: {topic}
    
    I've evaluated your response based on:
    - Accuracy (3 points): Correctness of technical information
    - Depth (3 points): Demonstration of deep understanding vs. surface knowledge
    - Clarity (2 points): Clear organization and explanation of concepts
    - Application (2 points): Ability to apply concepts to problems or scenarios
    
    OVERALL SCORE: {evaluation.get('totalScore', 0)}/10
    
    DETAILED BREAKDOWN:
    - Accuracy: {evaluation.get('scores', {}).get('accuracy', 0)}/3
    - Depth: {evaluation.get('scores', {}).get('depth', 0)}/3
    - Clarity: {evaluation.get('scores', {}).get('clarity', 0)}/2
    - Application: {evaluation.get('scores', {}).get('application', 0)}/2
    
    FEEDBACK:
    {evaluation.get('feedback', 'Your response shows some understanding of the topic.')}
    
    Would you like to dive deeper into any specific aspect of this topic?
    """
    
    # Get the LLM for generating a more natural response
    llm = get_llm(temperature=0.7)
    
    # Create a prompt for generating a natural, educational response
    response_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are an expert educational assessment provider. 
        Your goal is to provide constructive, detailed feedback on a student's knowledge check.
        Be encouraging but honest, and always offer specific ways to improve."""),
        HumanMessage(content=feedback_template)
    ])
    
    try:
        # Generate the response
        chain = response_prompt | llm | StrOutputParser()
        final_response = chain.invoke({})
        
        return {
            "response": final_response,
            "evaluation": evaluation,
            "topic": topic,
            "success": evaluation_result.get('success', False)
        }
    except Exception as e:
        logger.error(f"Error generating feedback response: {e}")
        return {
            "response": feedback_template.strip(),
            "evaluation": evaluation,
            "topic": topic,
            "success": False,
            "error": str(e)
        }

def response_generator(state: AgentState) -> AgentState:
    """
    Generate a response based on retrieved content and conversation history.
    Focuses on natural conversation and critical thinking.
    Special handling for syllabus-related queries with detailed document references.
    Special handling for knowledge check requests with evaluation prompts.
    
    Args:
        state: Current agent state containing content
        
    Returns:
        Updated state with the generated response
    """
    llm = get_llm(temperature=0.7)  # Higher temperature for more creative responses
    
    # Check what type of request we're handling
    is_syllabus_overview = state.get("is_syllabus_overview", False)
    is_specific_syllabus = state.get("is_specific_syllabus", False)
    is_follow_up_reference = state.get("is_follow_up_reference", False)
    is_knowledge_check = state.get("is_knowledge_check", False)
    knowledge_check_topic = state.get("knowledge_check_topic", None)
    knowledge_check_prompt = state.get("knowledge_check_prompt", None)
    referenced_topic = state.get("referenced_topic", None)
    matched_topics = state.get("matched_syllabus_topics", [])
    primary_topic = state.get("primary_topic", None)
    available_syllabi = state.get("available_syllabi", [])
    
    # Format content as context
    content_context = ""
    
    # CASE 1: Overview of all courses/syllabi
    if is_syllabus_overview:
        # Format list of available courses
        syllabi_documents = state.get("syllabi_documents", [])
        content_context = "Available courses in the knowledge base:\n\n"
        
        for i, syllabus in enumerate(syllabi_documents, 1):
            content_context += f"Course {i}: {syllabus.get('title', 'Unknown Course')}\n"
            content_context += f"Course Code: {syllabus.get('course_code', 'Unknown')}\n"
            content_context += f"Instructor: {syllabus.get('instructor', 'Unknown')}\n"
            content_context += f"Semester: {syllabus.get('semester', 'Unknown')}\n"
            
            # List topics for this course
            topics = syllabus.get("topics", [])
            if topics:
                content_context += "Topics covered:\n"
                for topic in topics:
                    content_context += f"- {topic.get('name', 'Unknown Topic')}: {topic.get('description', '')}\n"
            
            content_context += f"Source: {syllabus.get('source', 'Unknown')}\n\n"
        
        # Also add the structured topic list
        if state["content_results"]:
            content_context += "Topics across all courses:\n\n"
            for i, topic in enumerate(state["content_results"], 1):
                content_context += f"Topic {i}: {topic.get('topic', 'Unknown Topic')}\n"
                content_context += f"Description: {topic.get('description', '')}\n"
                content_context += f"Course: {topic.get('course', 'Unknown')}\n"
                content_context += f"Timeframe: {topic.get('week', 'TBD')}\n"
                content_context += f"Source: {topic.get('source', 'Unknown')}\n\n"
    
    # CASE 2: Specific course syllabus
    elif is_specific_syllabus and state["content_results"]:
        syllabus = state["content_results"][0]
        syllabus_doc = state.get("syllabus_document", "Unknown")
        
        content_context = f"Course Syllabus: {syllabus.get('title', 'Unknown Course')}\n\n"
        content_context += f"Course Code: {syllabus.get('course_code', 'Unknown')}\n"
        content_context += f"Instructor: {syllabus.get('instructor', 'Unknown')}\n"
        content_context += f"Semester: {syllabus.get('semester', 'Unknown')}\n\n"
        content_context += f"Overview: {syllabus.get('text', '')}\n\n"
        
        # List topics for this course
        topics = syllabus.get("topics", [])
        if topics:
            content_context += "Topics covered in this course:\n"
            for topic in topics:
                content_context += f"- {topic.get('name', 'Unknown Topic')} (Weeks {topic.get('weeks', 'TBD')})\n"
                content_context += f"  Description: {topic.get('description', '')}\n"
                if 'readings' in topic:
                    content_context += f"  Readings: {', '.join(topic.get('readings', []))}\n"
        
        content_context += f"\nSource Document: {syllabus_doc}\n"
    
    # CASE 3: Specific topic from a syllabus
    elif primary_topic and matched_topics:
        # Get source syllabus information
        source_syllabus = state.get("source_syllabus", {})
        
        content_context = f"Information about topic: {primary_topic}\n\n"
        content_context += f"From course: {source_syllabus.get('title', 'Unknown Course')} ({source_syllabus.get('course_code', 'Unknown')})\n"
        
        # Find the specific topic in the syllabus
        for topic_data in matched_topics:
            content_context += f"Topic: {topic_data.get('topic', 'Unknown Topic')}\n"
            content_context += f"Description: {topic_data.get('description', '')}\n"
            content_context += f"Timeframe: {topic_data.get('week', 'TBD')}\n"
            content_context += f"Source: {topic_data.get('source', 'Unknown')}\n\n"
        
        # Add related content
        if state["content_results"]:
            content_context += "Related content for this topic:\n\n"
            for i, result in enumerate(state["content_results"], 1):
                if isinstance(result, dict) and 'text' in result:
                    content_context += f"Content {i}:\n"
                    content_context += f"Text: {result.get('text', '')}\n"
                    metadata = result.get('metadata', {})
                    if metadata:
                        content_context += f"Source: {metadata.get('source', 'Unknown')}\n"
                        content_context += f"Page: {metadata.get('page', 'Unknown')}\n"
                        if metadata.get('keywords'):
                            content_context += f"Keywords: {metadata.get('keywords', '')}\n"
                    content_context += "\n"
    
    # CASE 4: General content for other queries
    elif state["content_results"]:
        content_context = "Here is relevant course content:\n\n"
        for i, result in enumerate(state["content_results"], 1):
            if isinstance(result, dict) and 'text' in result:
                content_context += f"Content {i}:\n"
                content_context += f"Text: {result.get('text', '')}\n"
                metadata = result.get('metadata', {})
                if metadata:
                    content_context += f"Source: {metadata.get('source', 'Unknown')}\n"
                    content_context += f"Page: {metadata.get('page', 'Unknown')}\n"
                    if metadata.get('keywords'):
                        content_context += f"Keywords: {metadata.get('keywords', '')}\n"
            content_context += "\n"
    
    # List available syllabi and courses if we have them
    syllabi_context = ""
    if available_syllabi and not is_syllabus_overview and not is_specific_syllabus:
        syllabi_context = "Available courses in the knowledge base:\n"
        for doc in available_syllabi:
            course_code = next((code for code in ["CS101", "MATH250", "PHYS201", "ENG301", "BUS220"] if code in doc), "Unknown")
            syllabi_context += f"- {course_code}: {doc}\n"
        syllabi_context += "\n"
    
    # Generate appropriate probing questions based on query type
    if is_syllabus_overview:
        # Questions about available courses
        probing_questions = [
            "Which of these courses are you most interested in exploring?",
            "Would you like more information about a specific course?",
            "Is there a particular topic across these courses that interests you?",
            "Do you have any questions about how these courses relate to each other?"
        ]
    elif is_specific_syllabus:
        # Questions about the specific course
        course_code = state["content_results"][0].get("course_code", "this course")
        probing_questions = [
            f"Which topic in {course_code} would you like to explore first?",
            f"Do you have any questions about the structure of the {course_code} course?",
            f"Is there a specific concept in {course_code} you'd like to discuss in more detail?",
            f"How does this course align with your learning goals?"
        ]
    elif primary_topic:
        # Questions about the specific topic
        probing_questions = generate_probing_questions(primary_topic, "intermediate")
    else:
        # General probing questions
        topic = state["query"].split()[0] if state["query"] else "this topic"
        probing_questions = generate_probing_questions(topic, "intermediate")
    
    questions_context = "\n".join([f"- {q}" for q in probing_questions])
    
    # Create appropriate response prompt based on query type
    if is_knowledge_check:
        # For knowledge check requests, generate a specialized prompt
        response_template = f"""
User has requested a knowledge check on: {knowledge_check_topic}

You should create a free-response knowledge assessment. This is NOT a multiple-choice quiz.

Please respond with:
1. A formal acknowledgment that you'll be evaluating their knowledge
2. A clear, specific prompt that asks them to explain their understanding of {knowledge_check_topic}
3. Instructions that their response should be comprehensive and demonstrate both factual knowledge and conceptual understanding
4. Explanation that you'll evaluate their response based on accuracy, depth, clarity, and practical application
5. The specific prompt: "{knowledge_check_prompt}"

Format the knowledge check as a special message that stands out visually.
Make it clear the student should take this as a formal assessment opportunity.
Do NOT provide any answers or hints - this is purely an assessment.

This is the FIRST step of a two-part interaction - you will evaluate their response in a follow-up message.
"""
    elif is_syllabus_overview:
        response_template = f"""
{content_context}

Suggested discussion questions about the available courses:
{questions_context}

User query: {state["query"]}

Please provide a structured, guided introduction to the available course topics by:
1. First, clearly listing the available courses and their key topics (like a course menu)
2. Presenting the topics in a sequential, easy-to-digest format (almost like a simple bullet list initially)
3. Then elaborating on the importance and relevance of these topics
4. Explaining how these topics build upon each other throughout the semester
5. Highlighting connections between topics across different courses
6. Explicitly inviting the student to select a specific topic for deeper discussion
7. Ending with a direct question like "Which of these topics would you like to explore first?"

When referencing courses and topics, cite the specific syllabus document directly.
Remember to "spoon-feed" the topic information first before engaging in deeper conversation - make it very clear what topics are available for discussion.
Your goal is to help the student understand what's available to learn and guide them toward selecting a specific topic.
"""
    elif is_specific_syllabus:
        syllabus = state["content_results"][0]
        course_code = syllabus.get("course_code", "this course")
        
        response_template = f"""
{content_context}

Suggested discussion questions about {course_code}:
{questions_context}

User query: {state["query"]}

Please provide a structured, guided introduction to this course syllabus by:
1. First, clearly presenting a simple list of all topics in this course (almost like a table of contents)
2. Organizing topics by week or logical progression as indicated in the syllabus
3. Then elaborating on the course structure, learning objectives, and topic progression
4. Highlighting 2-3 foundational topics that are especially important to understand early
5. Explaining how these topics build upon each other throughout the semester
6. Making connections between different topics within the course
7. Explicitly inviting the student to select a specific topic from the syllabus for deeper discussion
8. Ending with a direct question like "Which of these topics would you like to discuss first?"

When referencing the syllabus, cite it directly in your response using the format:
"[Source: {state.get('syllabus_document', 'Course Syllabus')}]"

Remember to "spoon-feed" the topic information first before engaging in deeper conversation - make it very clear what topics are available for discussion.
Your goal is to help the student understand the scope and value of this course, and to guide them toward selecting a specific topic to explore in more detail.
"""
    elif primary_topic:
        source_syllabus = state.get("source_syllabus", {})
        course_code = source_syllabus.get("course_code", "the course")
        
        # Add special context for follow-up references
        follow_up_context = ""
        if is_follow_up_reference and referenced_topic:
            follow_up_context = f"""
This is a follow-up request to explore the topic "{referenced_topic}" from the previous conversation.
The system has identified this as corresponding to the syllabus topic "{primary_topic}".
"""
        
        response_template = f"""
{content_context}

Suggested discussion questions for this topic:
{questions_context}

User query: {state["query"]}
Topic: {primary_topic}
From Course: {course_code}
{follow_up_context}

Please provide an educational response about this specific topic that follows this progression:
1. Begin with a clear, concise definition of {primary_topic} and its importance in {course_code}
2. Then act as a professor conducting a one-on-one lecture on {primary_topic}
3. Explain the core concepts and principles within this topic area in a structured way
4. Provide concrete examples and applications of these concepts
5. Reference specific learning materials from the course with ACTUAL page numbers and source names
6. Connect this topic to other topics in {course_code}
7. Throughout your response, pause to engage the student with questions that encourage critical thinking
8. End with 2-3 thought-provoking questions that invite deeper exploration of {primary_topic}

IMPORTANT: When referencing learning materials, cite the SPECIFIC source directly in your response using the format:
"[Source: Material Name, Page X]"

Each citation MUST include both the material name AND specific page number to be considered valid.
DO NOT use placeholder text like "Material Name" or "Page X" - use the ACTUAL source information.

Remember to encourage the user to think critically throughout your response and engage in a meaningful discussion about {primary_topic}. Use a Socratic teaching style to guide their understanding rather than just presenting information.
"""
    else:
        response_template = f"""
{syllabi_context}
{content_context}

Suggested discussion questions to encourage critical thinking:
{questions_context}

User query: {state["query"]}

Please provide an educational response that:
1. Acts as a professor conducting a one-on-one lecture
2. Encourages a natural conversation about the topic
3. Promotes critical thinking and healthy debate
4. References specific learning materials when appropriate
5. Guides the user to engage meaningfully with the material
6. Asks thought-provoking questions at the end
7. If appropriate, mentions what courses in our knowledge base might cover this topic

When referencing learning materials, cite the source directly in your response using the format:
"[Source: Material Name, Page X]"

Remember to encourage the user to think critically about your response and engage in a meaningful discussion.
"""
    
    # Create response prompt
    response_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        HumanMessage(content=response_template)
    ])
    
    try:
        # Convert message format for prompt
        history = []
        # Get the last 10 messages (excluding the current query) for context
        for msg in state["messages"][-11:-1]:  # Increased context window from 5 to 10 messages
            if msg["role"] == "user":
                history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                history.append(AIMessage(content=msg["content"]))
        
        # Generate response using LangChain 0.3+ chain syntax
        chain = response_prompt | llm | StrOutputParser()
        response = chain.invoke({"history": history})
        
        # Update state
        new_state = state.copy()
        new_state["final_response"] = response
        logger.info(f"Generated response: {response[:50]}...")
        
        return new_state
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        new_state = state.copy()
        new_state["error"] = f"Failed to generate response: {str(e)}"
        new_state["final_response"] = "I'm sorry, but I encountered an error while trying to answer your question. Please try again later."
        return new_state


def router(state: AgentState) -> str:
    """
    Determine the next step in the workflow based on the current state.
    
    Args:
        state: Current agent state
        
    Returns:
        Name of the next node to execute or END to finish processing
    """
    # If there's an error, go to track knowledge before response generation
    if state.get("error"):
        return "track_student_knowledge"
    
    # If we need to retrieve content, go to content retriever
    if state["needs_content"]:
        return "content_retriever"
    
    # Otherwise, go straight to tracking student knowledge
    return "track_student_knowledge"


def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph workflow for the teacher agent.
    
    Returns:
        Configured StateGraph for the agent
    """
    # Create a new graph with TypedDict state
    workflow = StateGraph(AgentState)
    
    # Add nodes to the graph
    workflow.add_node("query_analyzer", query_analyzer)
    workflow.add_node("content_retriever", content_retriever)
    workflow.add_node("track_student_knowledge", track_student_knowledge)
    workflow.add_node("response_generator", response_generator)
    
    # Add conditional edges from query_analyzer
    workflow.add_conditional_edges(
        "query_analyzer",
        router,
        {
            "content_retriever": "content_retriever",
            "track_student_knowledge": "track_student_knowledge"
        }
    )
    
    # Add remaining edges
    workflow.add_edge("content_retriever", "track_student_knowledge")
    workflow.add_edge("track_student_knowledge", "response_generator")
    workflow.add_edge("response_generator", END)
    
    # Set the entry point
    workflow.set_entry_point("query_analyzer")
    
    # Compile the graph
    return workflow.compile()


def process_query(query: str, session_id: str, message_history: Optional[List[Dict[str, Any]]] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Process a user query through the agent workflow.
    
    Args:
        query: The user's question
        session_id: Unique identifier for the conversation session
        message_history: Previous messages in the conversation
        metadata: Additional metadata, including knowledge check responses
        
    Returns:
        Dict containing the agent's response and updated conversation history
    """
    # Initialize message history if not provided
    if message_history is None:
        message_history = []
    
    # Initialize metadata if not provided
    if metadata is None:
        metadata = {}
    
    # Check if this is a response to a knowledge check
    knowledge_check_response = metadata.get('knowledge_check_response', False)
    
    if knowledge_check_response:
        # Process this as a knowledge check response
        topic = metadata.get('topic', 'general')
        prompt = metadata.get('prompt', 'Explain your understanding of this topic.')
        response_text = query
        user_id = metadata.get('user_id', 'anonymous')
        
        logger.info(f"Processing knowledge check response for topic: {topic}")
        
        # Use the specialized function for knowledge check responses
        result = process_knowledge_check_response(topic, prompt, response_text, user_id)
        
        # Format the response for the frontend
        evaluation = result.get('evaluation', {})
        
        # Add the response to message history
        message_history.append({
            "role": "user", 
            "content": query,
            "metadata": {
                "knowledge_check_response": True,
                "topic": topic
            }
        })
        
        message_history.append({
            "role": "assistant", 
            "content": result.get('response', ''),
            "metadata": {
                "knowledge_check_evaluation": evaluation
            }
        })
        
        return {
            "response": result.get('response', ''),
            "message_history": message_history,
            "knowledge_check_evaluation": evaluation,
            "success": result.get('success', False),
            "error": result.get('error')
        }
    
    # Regular query processing flow
    # Add the current query to message history
    message_history.append({"role": "user", "content": query})
    
    # Initialize agent state
    initial_state: AgentState = {
        "messages": message_history,
        "session_id": session_id,
        "query": query,
        "needs_content": False,
        "content_results": [],
        "student_knowledge_state": {},  # Will be populated during analysis
        "is_knowledge_check": False,
        "knowledge_check_topic": None,
        "knowledge_check_prompt": None,
        "knowledge_check_evaluation": None,
        "final_response": None,
        "error": None
    }
    
    try:
        # Create and run the agent graph
        agent_graph = create_agent_graph()
        final_state = agent_graph.invoke(initial_state)
        
        # Get the final response
        response = final_state["final_response"]
        
        # Extract knowledge state for frontend reference
        knowledge_state = final_state.get("student_knowledge_state", {})
        
        # Add the response to message history
        message_history.append({"role": "assistant", "content": response})
        
        # Check if this was a knowledge check request
        is_knowledge_check = final_state.get("is_knowledge_check", False)
        knowledge_check_data = None
        
        if is_knowledge_check:
            knowledge_check_data = {
                "topic": final_state.get("knowledge_check_topic", "general"),
                "prompt": final_state.get("knowledge_check_prompt", ""),
                "awaiting_response": True,
                "type": "free-response"
            }
            
        # Return result with enriched data for frontend
        return {
            "response": response,
            "message_history": message_history,
            "knowledge_state": knowledge_state,  # Include knowledge state for frontend visualization
            "knowledge_check": knowledge_check_data,  # Include knowledge check data if applicable
            "error": final_state.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        error_message = f"I'm sorry, but I encountered an error while processing your query: {str(e)}"
        
        # Add error response to message history
        message_history.append({"role": "assistant", "content": error_message})
        
        return {
            "response": error_message,
            "message_history": message_history,
            "knowledge_state": {},
            "error": str(e)
        }


# Lambda handler
def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    Args:
        event: Lambda event object containing the request data
        context: Lambda context object
        
    Returns:
        Response object containing the agent's response
    """
    try:
        # Parse request body
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = safe_json_loads(body)
        
        # Extract request parameters
        query = body.get('query', '')
        session_id = body.get('session_id', '')
        message_history = body.get('message_history', [])
        metadata = body.get('metadata', {})
        
        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session ID: {session_id}")
        
        # Validate required parameters
        if not query:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Query is required'})
            }
        
        # Process the query
        result = process_query(query, session_id, message_history, metadata)
        
        # Add session ID to response
        result['session_id'] = session_id
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }


# For local testing
if __name__ == "__main__":
    # Set up environment for testing
    if not os.environ.get("OPENAI_API_KEY"):
        from dotenv import load_dotenv
        load_dotenv()
    
    # Test the agent
    test_query = "Can you help me understand the concept of object-oriented programming?"
    test_session_id = "test-session-123"
    
    result = process_query(test_query, test_session_id)
    print(f"Query: {test_query}")
    print(f"Response: {result['response']}")
    print(f"Knowledge State: {json.dumps(result['knowledge_state'], indent=2)}")