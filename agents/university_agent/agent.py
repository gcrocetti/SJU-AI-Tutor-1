"""
University Information Agent

This module implements a LangGraph-based agent that answers university-related questions.
It uses a combination of conversation history and information retrieval to provide
accurate, helpful responses about university topics.

The agent follows these steps:
1. Analyze the query to determine if external information is needed
2. Retrieve relevant information from Google Custom Search if needed
3. Generate a coherent, helpful response using the conversation history and retrieved information
4. Maintain conversation context across interactions
"""

import os
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple, Callable

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# Import shared utilities
from agents.common.utils import setup_logging, safe_json_loads
from agents.university_agent.prompts import SYSTEM_PROMPT, QUERY_ANALYSIS_PROMPT
from agents.university_agent.tools import google_search_query

# Configure logging
logger = logging.getLogger(__name__)
setup_logging()

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


# Type for the graph state
class AgentState(dict):
    """State maintained throughout the agent's execution."""
    messages: List[Dict[str, Any]]
    session_id: str
    query: str
    needs_search: bool = False
    search_results: List[Dict[str, str]] = []
    final_response: Optional[str] = None
    error: Optional[str] = None


def query_analyzer(state: AgentState) -> Dict:
    """
    Analyze the user query to determine if external information retrieval is needed.
    
    Args:
        state: Current agent state containing the user query and conversation history
        
    Returns:
        Updated state with a decision on whether to perform a search
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

Do I need to search for external information to properly answer this query?
""")
    ])
    
    try:
        # Get analysis result
        chain = analysis_prompt | llm | StrOutputParser()
        result = chain.invoke({})
        
        # Parse decision - look for YES/NO pattern
        needs_search = "YES" in result.upper() and not "NO" in result.upper()
        
        # Update state
        state["needs_search"] = needs_search
        logger.info(f"Query analysis decided: needs_search={needs_search}")
        
        return state
    except Exception as e:
        logger.error(f"Error in query analysis: {e}")
        state["error"] = f"Failed to analyze query: {str(e)}"
        state["needs_search"] = True  # Default to search if analysis fails
        return state


def information_retriever(state: AgentState) -> Dict:
    """
    Retrieve relevant information for the query using Google Custom Search.
    
    Args:
        state: Current agent state containing the query to search for
        
    Returns:
        Updated state with search results
    """
    try:
        query = state["query"]
        logger.info(f"Retrieving information for: {query}")
        
        # Get search results
        search_results = google_search_query(query)
        
        # Add results to state
        state["search_results"] = search_results
        logger.info(f"Retrieved {len(search_results)} search results")
        
        return state
    except Exception as e:
        logger.error(f"Error retrieving information: {e}")
        state["error"] = f"Failed to retrieve information: {str(e)}"
        state["search_results"] = []  # Empty results on error
        return state


def response_generator(state: AgentState) -> Dict:
    """
    Generate a response based on the conversation history and retrieved information.
    
    Args:
        state: Current agent state containing conversation history and search results
        
    Returns:
        Updated state with the generated response
    """
    llm = get_llm(temperature=0.7)  # Higher temperature for more creative responses
    
    # Format search results as context
    search_context = ""
    if state["search_results"]:
        search_context = "Here are some relevant sources:\n\n"
        for i, result in enumerate(state["search_results"], 1):
            search_context += f"Source {i}: {result['title']}\n"
            search_context += f"URL: {result['link']}\n"
            search_context += f"Snippet: {result['snippet']}\n\n"
    
    # Create response prompt
    response_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        HumanMessage(content=f"""
{search_context}

User query: {state["query"]}

Please provide a helpful response. If you used any of the sources above, 
please include the source URLs directly in your response in the following format:
"[Source: https://example.com]" rather than just [Source 1].

When including multiple sources, name each one separately with its URL:
"According to [Source: https://example1.com] and [Source: https://example2.com], ..."

If you don't know the answer or need more specific information, please say so.
""")
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
        
        # Generate response
        chain = response_prompt | llm | StrOutputParser()
        response = chain.invoke({"history": history})
        
        # Update state
        state["final_response"] = response
        logger.info(f"Generated response: {response[:50]}...")
        
        return state
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        state["error"] = f"Failed to generate response: {str(e)}"
        state["final_response"] = "I'm sorry, but I encountered an error while trying to answer your question. Please try again later."
        return state


def router(state: AgentState) -> str:
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
    
    # If we need to search, go to information retrieval
    if state["needs_search"]:
        return "information_retriever"
    
    # Otherwise, go straight to response generation
    return "response_generator"


def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph workflow for the university agent.
    
    Returns:
        Configured StateGraph for the agent
    """
    # Create a new graph
    workflow = StateGraph(AgentState)
    
    # Add nodes to the graph
    workflow.add_node("query_analyzer", query_analyzer)
    workflow.add_node("information_retriever", information_retriever)
    workflow.add_node("response_generator", response_generator)
    
    # Add conditional edges from query_analyzer
    workflow.add_conditional_edges(
        "query_analyzer",
        router,
        {
            "information_retriever": "information_retriever",
            "response_generator": "response_generator"
        }
    )
    
    # Add remaining edges
    workflow.add_edge("information_retriever", "response_generator")
    workflow.add_edge("response_generator", END)
    
    # Set the entry point
    workflow.set_entry_point("query_analyzer")
    
    # Compile the graph
    return workflow.compile()


def process_query(query: str, session_id: str, message_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Process a user query through the agent workflow.
    
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
    
    # Initialize agent state
    initial_state = AgentState(
        messages=message_history,
        session_id=session_id,
        query=query,
        needs_search=False,
        search_results=[],
        final_response=None,
        error=None
    )
    
    try:
        # Create and run the agent graph
        agent_graph = create_agent_graph()
        final_state = agent_graph.invoke(initial_state)
        
        # Get the final response
        response = final_state["final_response"]
        
        # Extract search results for frontend reference
        search_results = final_state.get("search_results", [])
        
        # Add the response to message history
        message_history.append({"role": "assistant", "content": response})
        
        # Return result with enriched data for frontend
        return {
            "response": response,
            "message_history": message_history,
            "sources": search_results,  # Include full source details for frontend formatting
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
            "sources": [],
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
    test_query = "What are the requirements for the computer science major?"
    test_session_id = "test-session-123"
    
    result = process_query(test_query, test_session_id)
    print(f"Query: {test_query}")
    print("\nFull response object:")
    print(json.dumps(result, indent=2))