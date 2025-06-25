"""
Motivator Agent (Emotional Support Specialist)

This module implements a LangGraph-based agent that provides emotional support,
motivation, and stress management guidance to students. It focuses on:
1. Conducting regular check-ins to assess student morale
2. Offering stress management and test-anxiety reduction strategies
3. Monitoring for signs of severe distress and flagging concerns

The agent maintains emotional context across interactions to provide
personalized support based on the student's history and current state.

Refactored for LangChain 0.3+ and LangGraph 0.1+
"""

import os
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple, TypedDict, Annotated

# LangGraph and LangChain imports - updated for 0.3+
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Try to import from pydantic v2 first, fall back to v1 if needed
try:
    from pydantic import BaseModel, Field
except ImportError:
    # Fall back to pydantic v1 compatibility
    from pydantic.v1 import BaseModel, Field

# Import shared utilities
from tutor.common.utils import setup_logging, safe_json_loads
from tutor.motivator_agent.prompts import SYSTEM_PROMPT, EMOTIONAL_ASSESSMENT_PROMPT, INTERVENTION_PROMPT, CRISIS_SYSTEM_PROMPT
from tutor.motivator_agent.tools import assess_distress_level, format_interaction_history, get_campus_resources, check_for_emergency_terms

# Configure logging
logger = logging.getLogger(__name__)
setup_logging()

# Define typed state for LangGraph
class MotivatorState(TypedDict):
    """State maintained throughout the agent's execution."""
    messages: List[Dict[str, Any]]
    session_id: str
    query: str
    emotional_state: Dict[str, Any]
    intervention_needed: bool
    intervention_type: Optional[str]
    final_response: Optional[str]
    error: Optional[str]

# Define output schema for emotional assessment
class EmotionalAssessment(BaseModel):
    """Schema for emotional state assessment output."""
    mood: str = Field(description="The current mood of the student (e.g. anxious, motivated, stressed)")
    stress_level: int = Field(description="Stress level on a scale of 1-10")
    confidence_level: int = Field(description="Confidence level on a scale of 1-10")
    primary_concern: str = Field(description="The main concern or issue the student is facing")
    risk_factors: List[str] = Field(description="Any potential risk factors or warning signs")
    requires_intervention: bool = Field(description="Whether professional intervention might be needed")


# Initialize the LLM
def get_llm(temperature: float = 0.7) -> ChatOpenAI:
    """
    Initialize the OpenAI chat model with specified parameters.
    
    Args:
        temperature: Controls randomness of responses. Lower is more deterministic.
        
    Returns:
        Configured ChatOpenAI instance
    """
    try:
        return ChatOpenAI(
            model="gpt-3.5-turbo-16k",
            temperature=temperature,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI LLM: {e}")
        raise


def emotional_assessment(state: MotivatorState) -> MotivatorState:
    """
    Analyze the emotional state of the student based on their query and conversation history.
    
    Args:
        state: Current agent state containing the user query and conversation history
        
    Returns:
        Updated state with emotional assessment
    """
    llm = get_llm(temperature=0.2)  # Low temperature for more consistent analysis
    
    # Format conversation history for context
    messages = state["messages"][-10:] if len(state["messages"]) > 10 else state["messages"]
    formatted_history = format_interaction_history(messages)
    
    # Create assessment prompt
    assessment_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=EMOTIONAL_ASSESSMENT_PROMPT),
        HumanMessage(content=f"""
Conversation history:
{formatted_history}

Current message: {state["query"]}

Please assess the student's emotional state based on this conversation.
Return your assessment as a JSON object with the following fields:
- mood: The current mood of the student
- stress_level: Stress level on a scale of 1-10
- confidence_level: Confidence level on a scale of 1-10
- primary_concern: The main concern or issue the student is facing
- risk_factors: Any potential risk factors or warning signs
- requires_intervention: Whether professional intervention might be needed (true/false)
""")
    ])
    
    try:
        # Get assessment result using LangChain 0.3+ chain syntax with JSON parsing
        chain = assessment_prompt | llm | JsonOutputParser(pydantic_model=EmotionalAssessment)
        assessment = chain.invoke({})
        
        # Update state with emotional assessment
        new_state = state.copy()
        
        # Check if assessment is a Pydantic model or a dictionary
        if hasattr(assessment, 'model_dump'):
            # If it's a Pydantic v2 model
            new_state["emotional_state"] = assessment.model_dump()
        elif hasattr(assessment, 'dict'):
            # If it's a Pydantic v1 model
            new_state["emotional_state"] = assessment.dict()
        else:
            # If it's already a dictionary
            new_state["emotional_state"] = assessment
        
        # Determine if intervention is needed
        distress_level, intervention_type = assess_distress_level(new_state["emotional_state"])
        new_state["intervention_needed"] = distress_level > 2  # Threshold for intervention
        new_state["intervention_type"] = intervention_type if distress_level > 2 else None
        
        logger.info(f"Emotional assessment completed: {new_state['emotional_state']}")
        
        return new_state
    except Exception as e:
        logger.error(f"Error in emotional assessment: {e}")
        new_state = state.copy()
        new_state["error"] = f"Failed to assess emotional state: {str(e)}"
        new_state["emotional_state"] = {
            "mood": "unknown",
            "stress_level": 5,
            "confidence_level": 5,
            "primary_concern": "Unable to determine",
            "risk_factors": [],
            "requires_intervention": False
        }
        return new_state


def intervention_checker(state: MotivatorState) -> MotivatorState:
    """
    Check if intervention is needed based on emotional assessment.
    
    Args:
        state: Current agent state containing emotional assessment
        
    Returns:
        Updated state with intervention information
    """
    # Only process if we have an emotional state assessment
    if not state.get("emotional_state"):
        return state
    
    try:
        # Get intervention guidance if needed
        if state["intervention_needed"]:
            llm = get_llm(temperature=0.3)
            
            # Get campus resources using university agent when available
            use_university_agent = True
            session_id = state.get("session_id", "")
            resources = get_campus_resources(use_university_agent, session_id)
            
            # Format resources for the prompt
            formatted_resources = "\n".join([f"- {name}: {details}" for name, details in resources.items()])
            
            # Create intervention prompt
            intervention_prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=INTERVENTION_PROMPT),
                HumanMessage(content=f"""
Student's emotional state:
- Mood: {state["emotional_state"]["mood"]}
- Stress level: {state["emotional_state"]["stress_level"]}/10
- Confidence level: {state["emotional_state"]["confidence_level"]}/10
- Primary concern: {state["emotional_state"]["primary_concern"]}
- Risk factors: {', '.join(state["emotional_state"]["risk_factors"])}

Intervention type needed: {state["intervention_type"]}

Available campus resources:
{formatted_resources}

Please provide specific guidance for this student situation, incorporating appropriate resources when helpful.
""")
            ])
            
            # Get intervention guidance
            chain = intervention_prompt | llm | StrOutputParser()
            intervention_guidance = chain.invoke({})
            
            # Update state
            new_state = state.copy()
            new_state["intervention_guidance"] = intervention_guidance
            new_state["campus_resources"] = resources
            logger.info(f"Intervention guidance generated for type: {state['intervention_type']}")
            
            return new_state
        
        return state
    except Exception as e:
        logger.error(f"Error in intervention checking: {e}")
        new_state = state.copy()
        new_state["error"] = f"Failed to check for intervention: {str(e)}"
        return new_state


def response_generator(state: MotivatorState) -> MotivatorState:
    """
    Generate a supportive response based on the emotional assessment and conversation history.
    
    Args:
        state: Current agent state containing emotional assessment and intervention details
        
    Returns:
        Updated state with the generated response
    """
    # Check if this is a crisis situation requiring the crisis prompt
    is_crisis = False
    if state.get("intervention_needed") and state.get("intervention_type") == "urgent":
        # Check for high-risk terms in the query
        if check_for_emergency_terms(state["query"]):
            is_crisis = True
        # Also check emotional state for severe risk
        if state.get("emotional_state"):
            mood = state["emotional_state"].get("mood", "").lower()
            primary_concern = state["emotional_state"].get("primary_concern", "").lower()
            if any(term in mood.lower() for term in ["suicidal", "giving up", "hopeless"]):
                is_crisis = True
            if any(term in primary_concern.lower() for term in ["suicide", "self-harm", "end life"]):
                is_crisis = True
    
    # Use appropriate temperature and system prompt based on situation
    if is_crisis:
        llm = get_llm(temperature=0.3)  # Lower temperature for more predictable crisis responses
        system_prompt = CRISIS_SYSTEM_PROMPT
    else:
        llm = get_llm(temperature=0.7)  # Higher temperature for more empathetic regular responses
        system_prompt = SYSTEM_PROMPT
    
    # Create response prompt with emotional context
    emotional_context = ""
    if state.get("emotional_state"):
        emotional_context = f"""
Based on my assessment, the student appears to be:
- Current mood: {state["emotional_state"]["mood"]}
- Stress level: {state["emotional_state"]["stress_level"]}/10
- Confidence level: {state["emotional_state"]["confidence_level"]}/10
- Primary concern: {state["emotional_state"]["primary_concern"]}
"""
    
    # Add intervention guidance if available
    intervention_guidance = ""
    if state.get("intervention_needed") and state.get("intervention_guidance"):
        intervention_guidance = f"""
This student may need additional support. Intervention type: {state["intervention_type"]}

Guidance for this situation: {state["intervention_guidance"]}
"""
    
    # Create response prompt
    response_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        MessagesPlaceholder(variable_name="history"),
        HumanMessage(content=f"""
{emotional_context}
{intervention_guidance}

Student's message: {state["query"]}

Please provide a supportive, empathetic response that addresses the student's emotional needs
and offers appropriate guidance, resources, or strategies.
"""
        + ("\nREMEMBER: This is a CRISIS situation. Include ALL crisis resources prominently in your response."
           if is_crisis else ""))
    ])
    
    try:
        # Convert message format for prompt
        history = []
        # Get the last 10 messages (excluding the current query) for context
        for msg in state["messages"][-11:-1]:
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
        new_state["is_crisis"] = is_crisis
        logger.info(f"Generated supportive response: {response[:50]}...")
        
        return new_state
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        new_state = state.copy()
        new_state["error"] = f"Failed to generate response: {str(e)}"
        
        # Even in case of error, provide a safety-focused response for potential crisis situations
        if is_crisis:
            new_state["final_response"] = """I notice you may be in distress right now. Your safety is extremely important. Please reach out immediately to these resources:

- National Suicide Prevention Lifeline: Call or text 988 (Available 24/7)
- Crisis Text Line: Text HOME to 741741 (Available 24/7)
- St. John's University CAPS: 718-990-6384 (During business hours)
- CAPS After-Hours Crisis Helpline: 718-990-6352
- Emergency Services: Call 911 if you're in immediate danger

Please don't hesitate to reach out to one of these resources right now. You don't have to face this alone."""
        else:
            new_state["final_response"] = "I'm having trouble formulating a helpful response right now. Let's take a step back. Could you tell me more about how you're feeling today, and we can start from there?"
        
        return new_state


def router(state: MotivatorState) -> str:
    """
    Determine the next step in the workflow based on the current state.
    
    Args:
        state: Current agent state
        
    Returns:
        Name of the next node to execute or END to finish processing
    """
    # If there's an error, go straight to response generation with a fallback
    if state.get("error"):
        return "response_generator"
    
    # If we need intervention, go to intervention checker
    if state.get("intervention_needed"):
        return "intervention_checker"
    
    # Otherwise, go straight to response generation
    return "response_generator"


def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph workflow for the motivator agent.
    
    Returns:
        Configured StateGraph for the agent
    """
    # Create a new graph with TypedDict state
    workflow = StateGraph(MotivatorState)
    
    # Add nodes to the graph
    workflow.add_node("emotional_assessment", emotional_assessment)
    workflow.add_node("intervention_checker", intervention_checker)
    workflow.add_node("response_generator", response_generator)
    
    # Add conditional edges from emotional_assessment
    workflow.add_conditional_edges(
        "emotional_assessment",
        router,
        {
            "intervention_checker": "intervention_checker",
            "response_generator": "response_generator"
        }
    )
    
    # Add remaining edges
    workflow.add_edge("intervention_checker", "response_generator")
    workflow.add_edge("response_generator", END)
    
    # Set the entry point
    workflow.set_entry_point("emotional_assessment")
    
    # Compile the graph
    return workflow.compile()


def process_query(query: str, session_id: str, message_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Process a user query through the agent workflow.
    
    Args:
        query: The user's message
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
    
    # Initialize agent state
    initial_state: MotivatorState = {
        "messages": message_history,
        "session_id": session_id,
        "query": query,
        "emotional_state": {},
        "intervention_needed": False,
        "intervention_type": None,
        "final_response": None,
        "error": None
    }
    
    try:
        # Create and run the agent graph
        agent_graph = create_agent_graph()
        final_state = agent_graph.invoke(initial_state)
        
        # Get the final response
        response = final_state["final_response"]
        
        # Add the response to message history
        message_history.append({"role": "assistant", "content": response})
        
        # Return result with enriched data for frontend
        return {
            "response": response,
            "message_history": message_history,
            "emotional_state": final_state.get("emotional_state", {}),
            "intervention_needed": final_state.get("intervention_needed", False),
            "intervention_type": final_state.get("intervention_type"),
            "error": final_state.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        error_message = f"I'm having trouble processing your message right now. Let's try a different approach. How are you feeling about your studies today?"
        
        # Add error response to message history
        message_history.append({"role": "assistant", "content": error_message})
        
        return {
            "response": error_message,
            "message_history": message_history,
            "emotional_state": {},
            "intervention_needed": False,
            "intervention_type": None,
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
        result = process_query(query, session_id, message_history)
        
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
    test_query = "I'm really stressed about my upcoming exams and I can't sleep. I don't know if I can handle all this pressure."
    test_session_id = "test-session-123"
    
    result = process_query(test_query, test_session_id)
    print(f"Query: {test_query}")
    print(f"Response: {result['response']}")