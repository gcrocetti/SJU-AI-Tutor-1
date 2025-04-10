"""
Orchestrator Agent (Primary Gatekeeper)

This module implements a LangGraph-based orchestrator agent that oversees the entire
student interaction flow and determines which specialized agents should handle each query.
It performs:

1. Query analysis to understand the student's intent
2. Agent selection based on query characteristics
3. Query reformulation for specialized agents when needed
4. Maintenance of conversation context across multiple agents

Refactored for LangChain 0.3+ and LangGraph 0.1+
"""

import os
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple, TypedDict, Annotated, Set

# LangGraph and LangChain imports - updated for 0.3+
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Try to import from pydantic v2 first, fall back to v1 if needed
try:
    from pydantic import BaseModel, Field, validator
except ImportError:
    # Fall back to pydantic v1 compatibility
    from pydantic.v1 import BaseModel, Field, validator

# Import shared utilities
from agents.common.utils import setup_logging, safe_json_loads
from agents.orchestrator.prompts import SYSTEM_PROMPT, QUERY_ANALYSIS_PROMPT
from agents.orchestrator.tools import format_agent_descriptions, format_conversation_history

# Configure logging
logger = logging.getLogger(__name__)
setup_logging()

# Define output schema for query analysis
class AgentSelection(BaseModel):
    """Schema for agent selection and query routing."""
    selected_agents: List[str] = Field(
        description="List of agent IDs that should handle this query", 
        default_factory=list
    )
    subqueries: Dict[str, str] = Field(
        description="Reformulated queries for each selected agent",
        default_factory=dict
    )
    primary_intent: str = Field(
        description="The primary intent or purpose of the user's query",
        default=""
    )
    require_aggregation: bool = Field(
        description="Whether the results from multiple agents need to be aggregated",
        default=False
    )
    
    @validator('selected_agents')
    def validate_selected_agents(cls, v):
        valid_agents = {"university", "motivator", "teacher", "knowledge_check", "academic_coach"}
        for agent in v:
            if agent not in valid_agents:
                raise ValueError(f"Invalid agent ID: {agent}. Must be one of {valid_agents}")
        return v
    
    @validator('subqueries')
    def validate_subqueries(cls, v, values):
        if 'selected_agents' in values:
            for agent in values['selected_agents']:
                if agent not in v:
                    raise ValueError(f"Missing subquery for selected agent: {agent}")
        return v

# Define typed state for LangGraph
class OrchestratorState(TypedDict):
    """State maintained throughout the orchestrator's execution."""
    messages: List[Dict[str, Any]]
    session_id: str
    query: str
    agent_selection: Dict[str, Any]
    agent_responses: Dict[str, Any]
    final_response: Optional[str]
    error: Optional[str]

# Initialize the LLM
def get_llm(temperature: float = 0.2) -> ChatOpenAI:
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


def query_analyzer(state: OrchestratorState) -> OrchestratorState:
    """
    Analyze the user query to determine which agents should handle it.
    
    Args:
        state: Current orchestrator state containing the user query and conversation history
        
    Returns:
        Updated state with agent selection and subqueries
    """
    llm = get_llm(temperature=0.2)  # Low temperature for more deterministic analysis
    
    # Format conversation history for context
    messages = state["messages"][-10:] if len(state["messages"]) > 10 else state["messages"]
    formatted_history = format_conversation_history(messages)
    
    # Get agent descriptions for context
    agent_descriptions = format_agent_descriptions()
    
    # Create analysis prompt
    analysis_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=QUERY_ANALYSIS_PROMPT),
        HumanMessage(content=f"""
Agent descriptions:
{agent_descriptions}

Conversation history:
{formatted_history}

Current query: {state["query"]}

Determine which specialized agents should handle this query.
Return your analysis as a JSON object with:
- selected_agents: List of agent IDs that should handle this query
- subqueries: Reformulated queries for each selected agent
- primary_intent: The primary intent of the user's query
- require_aggregation: Whether responses need to be aggregated
""")
    ])
    
    try:
        # Get analysis result using LangChain 0.3+ chain syntax
        chain = analysis_prompt | llm | JsonOutputParser(pydantic_model=AgentSelection)
        selection = chain.invoke({})
        
        # Update state
        new_state = state.copy()
        # Check if selection is a Pydantic model or a dictionary
        if hasattr(selection, 'model_dump'):
            # If it's a Pydantic v2 model
            new_state["agent_selection"] = selection.model_dump()
        elif hasattr(selection, 'dict'):
            # If it's a Pydantic v1 model
            new_state["agent_selection"] = selection.dict()
        else:
            # If it's already a dictionary
            new_state["agent_selection"] = selection
            
        logger.info(f"Query analysis selected agents: {new_state['agent_selection'].get('selected_agents', [])}")
        
        return new_state
    except Exception as e:
        logger.error(f"Error in query analysis: {e}")
        new_state = state.copy()
        new_state["error"] = f"Failed to analyze query: {str(e)}"
        
        # If query mentions syllabus, route to teacher agent by default
        query_lower = state["query"].lower()
        syllabus_keywords = [
            # Traditional syllabus keywords
            "syllabus", "syllabi", "topics", "course content", "we're learning", 
            "studying", "topics for this week", "topics this week",
            
            # Student conversational variations
            "topics are up for discussion", "topics for discussion", 
            "material is on the syllabus", "material on the syllabus",
            "main subjects", "subjects covered", "overview of what we're learning",
            "topics should i focus", "covered in the course", "should i be studying",
            "syllabus for this semester", "key topics", "course outline",
            "subjects included", "summarize what we're learning",
            "what are we learning", "what am i supposed to learn",
            "what's included in this course", "what's on the agenda",
            "what are the areas", "what should we discuss", "topics available",
            "course overview", "what will we cover", "class topics", "overview of topics",
            "available courses", "what courses", "list of courses"
        ]
        
        if any(keyword in query_lower for keyword in syllabus_keywords):
            # Default to teacher agent for syllabus-related queries
            new_state["agent_selection"] = {
                "selected_agents": ["teacher"],
                "subqueries": {"teacher": state["query"]},
                "primary_intent": "syllabus information",
                "require_aggregation": False
            }
            logger.info(f"Detected syllabus-related query, routing to teacher agent: {state['query']}")
        else:
            # Default to university agent for other queries
            new_state["agent_selection"] = {
                "selected_agents": ["university"],
                "subqueries": {"university": state["query"]},
                "primary_intent": "information",
                "require_aggregation": False
            }
        return new_state


def route_to_agents(state: OrchestratorState) -> OrchestratorState:
    """
    Route the query to the selected agents and collect their responses.
    
    Args:
        state: Current orchestrator state containing agent selection
        
    Returns:
        Updated state with agent responses
    """
    try:
        # Initialize empty responses
        agent_responses = {}
        
        # Get agent selection from state
        selection = state["agent_selection"]
        
        # For each selected agent, route the appropriate subquery
        for agent_id in selection["selected_agents"]:
            subquery = selection["subqueries"].get(agent_id, state["query"])
            
            logger.info(f"Routing query to {agent_id} agent: {subquery}")
            
            # Call the appropriate agent
            if agent_id == "university":
                from agents.university_agent.agent import process_query as university_process
                response = university_process(subquery, state["session_id"], state["messages"])
                agent_responses[agent_id] = response
                
            elif agent_id == "motivator":
                from agents.motivator_agent.agent import process_query as motivator_process
                response = motivator_process(subquery, state["session_id"], state["messages"])
                agent_responses[agent_id] = response
                
            elif agent_id == "teacher":
                from agents.teacher_agent.agent import process_query as teacher_process
                response = teacher_process(subquery, state["session_id"], state["messages"])
                agent_responses[agent_id] = response
                
            elif agent_id == "knowledge_check":
                from agents.knowledge_check_agent.agent import process_query as knowledge_check_process
                response = knowledge_check_process(subquery, state["session_id"], state["messages"])
                agent_responses[agent_id] = response
                
            elif agent_id == "academic_coach":
                from agents.academic_coach_agent.agent import process_query as academic_coach_process
                response = academic_coach_process(subquery, state["session_id"], state["messages"])
                agent_responses[agent_id] = response
                
            else:
                logger.warning(f"Unknown agent ID: {agent_id}")
        
        # Update state with collected responses
        new_state = state.copy()
        new_state["agent_responses"] = agent_responses
        
        return new_state
    except Exception as e:
        logger.error(f"Error routing to agents: {e}")
        new_state = state.copy()
        new_state["error"] = f"Failed to route to agents: {str(e)}"
        return new_state


def generate_final_response(state: OrchestratorState) -> OrchestratorState:
    """
    Generate the final response based on all agent responses.
    If aggregation is required, combine multiple responses coherently.
    
    Args:
        state: Current orchestrator state containing agent responses
        
    Returns:
        Updated state with final response
    """
    try:
        # Get agent responses
        agent_responses = state["agent_responses"]
        require_aggregation = state["agent_selection"].get("require_aggregation", False)
        
        # If no responses, handle error
        if not agent_responses:
            new_state = state.copy()
            new_state["error"] = "No agent responses received"
            new_state["final_response"] = "I'm sorry, but I'm having trouble processing your request right now. Could you please try again or rephrase your question?"
            return new_state
        
        # If only one agent response or no aggregation needed, use that directly
        if len(agent_responses) == 1 or not require_aggregation:
            # Get the first (and possibly only) response
            agent_id = list(agent_responses.keys())[0]
            response_text = agent_responses[agent_id].get("response", "")
            
            new_state = state.copy()
            new_state["final_response"] = response_text
            return new_state
        
        # If multiple responses need to be aggregated, use the aggregator agent
        else:
            from agents.aggregator.agent import aggregate_responses
            
            # Get all response texts
            response_texts = {agent_id: response.get("response", "") 
                             for agent_id, response in agent_responses.items()}
            
            # Get primary intent for context
            primary_intent = state["agent_selection"].get("primary_intent", "")
            
            # Aggregate responses
            final_response = aggregate_responses(
                response_texts, 
                state["query"], 
                primary_intent
            )
            
            new_state = state.copy()
            new_state["final_response"] = final_response
            return new_state
            
    except Exception as e:
        logger.error(f"Error generating final response: {e}")
        new_state = state.copy()
        new_state["error"] = f"Failed to generate final response: {str(e)}"
        new_state["final_response"] = "I'm sorry, but I'm having trouble processing your request right now. Could you please try again or rephrase your question?"
        return new_state


def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph workflow for the orchestrator agent.
    
    Returns:
        Configured StateGraph for the agent
    """
    # Create a new graph with TypedDict state
    workflow = StateGraph(OrchestratorState)
    
    # Add nodes to the graph
    workflow.add_node("query_analyzer", query_analyzer)
    workflow.add_node("route_to_agents", route_to_agents)
    workflow.add_node("generate_final_response", generate_final_response)
    
    # Add edges
    workflow.add_edge("query_analyzer", "route_to_agents")
    workflow.add_edge("route_to_agents", "generate_final_response")
    workflow.add_edge("generate_final_response", END)
    
    # Set the entry point
    workflow.set_entry_point("query_analyzer")
    
    # Compile the graph
    return workflow.compile()


def process_query(query: str, session_id: str, message_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Process a user query through the orchestrator workflow.
    
    Args:
        query: The user's question
        session_id: Unique identifier for the conversation session
        message_history: Previous messages in the conversation
        
    Returns:
        Dict containing the final response and updated conversation history
    """
    # Initialize message history if not provided
    if message_history is None:
        message_history = []
    
    # Add the current query to message history
    message_history.append({"role": "user", "content": query})
    
    # Initialize orchestrator state
    initial_state: OrchestratorState = {
        "messages": message_history,
        "session_id": session_id,
        "query": query,
        "agent_selection": {},
        "agent_responses": {},
        "final_response": None,
        "error": None
    }
    
    try:
        # Create and run the orchestrator graph
        orchestrator_graph = create_agent_graph()
        final_state = orchestrator_graph.invoke(initial_state)
        
        # Get the final response
        response = final_state["final_response"]
        
        # Add the response to message history
        message_history.append({"role": "assistant", "content": response})
        
        # Determine which agents were used
        used_agents = list(final_state.get("agent_responses", {}).keys())
        
        # Return result with enriched data for frontend
        return {
            "response": response,
            "message_history": message_history,
            "used_agents": used_agents,
            "session_id": session_id,
            "error": final_state.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        error_message = f"I'm sorry, but I encountered an error while processing your query. Please try again or rephrase your question."
        
        # Add error response to message history
        message_history.append({"role": "assistant", "content": error_message})
        
        return {
            "response": error_message,
            "message_history": message_history,
            "used_agents": [],
            "session_id": session_id,
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
        Response object containing the orchestrated response
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
    
    # Test the orchestrator
    test_query = "What are the requirements for the computer science major? I'm feeling really anxious about whether I'll be able to handle the coursework."
    test_session_id = "test-session-123"
    
    result = process_query(test_query, test_session_id)
    print(f"Query: {test_query}")
    print(f"Used agents: {result.get('used_agents', [])}")
    print(f"Response: {result['response']}")