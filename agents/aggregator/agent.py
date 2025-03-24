"""
Aggregator Agent

This module implements the aggregator agent that combines responses from multiple specialized agents
into a coherent, unified response. It ensures that responses are integrated seamlessly without
redundancy, contradictions, or disjointed information.

It's designed to:
1. Analyze responses from different agents
2. Identify complementary and overlapping information
3. Structure a cohesive response that addresses all aspects of the student's query
4. Maintain a consistent tone and format

Updated for LangChain 0.3+ compatibility
"""

import os
import logging
from typing import Dict, List, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agents.common.utils import setup_logging
from agents.aggregator.prompts import SYSTEM_PROMPT

# Configure logging
logger = logging.getLogger(__name__)
setup_logging()

def get_llm(temperature: float = 0.4) -> ChatOpenAI:
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

def aggregate_responses(
    agent_responses: Dict[str, str], 
    original_query: str, 
    primary_intent: Optional[str] = None
) -> str:
    """
    Aggregate responses from multiple agents into a coherent, unified response.
    
    Args:
        agent_responses: Dictionary mapping agent IDs to their responses
        original_query: The original user query that generated these responses
        primary_intent: The primary intent or purpose of the user's query
        
    Returns:
        A unified, cohesive response
    """
    try:
        # Format agent responses for the prompt
        formatted_responses = []
        for agent_id, response in agent_responses.items():
            agent_name = {
                "university": "University Information Agent",
                "motivator": "Motivator Agent (Emotional Support)"
            }.get(agent_id, agent_id.capitalize() + " Agent")
            
            formatted_responses.append(f"{agent_name} response:\n{response}")
        
        formatted_responses_text = "\n\n".join(formatted_responses)
        
        # Create the aggregation prompt
        llm = get_llm(temperature=0.4)
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""
Original query: {original_query}

Primary intent: {primary_intent or "Not specified"}

Responses to aggregate:

{formatted_responses_text}

Create a unified, coherent response that integrates information from all agent responses.
Focus on ensuring a natural flow of information and a consistent tone.
""")
        ])
        
        # Generate the aggregated response
        chain = prompt | llm | StrOutputParser()
        aggregated_response = chain.invoke({})
        
        logger.info(f"Successfully aggregated responses from {len(agent_responses)} agents")
        return aggregated_response
        
    except Exception as e:
        logger.error(f"Error aggregating responses: {e}")
        # Fallback: return the response from the agent that best matches the primary intent
        # or the first response if no primary intent is specified
        if primary_intent and primary_intent in ["emotional", "motivation", "stress"] and "motivator" in agent_responses:
            return agent_responses["motivator"]
        elif primary_intent and primary_intent in ["information", "academic", "university"] and "university" in agent_responses:
            return agent_responses["university"]
        elif agent_responses:
            return next(iter(agent_responses.values()))
        else:
            return "I'm sorry, but I'm having trouble generating a complete response right now. Could you please try again or rephrase your question?"


def format_agent_contribution(agent_id: str, contribution: str) -> str:
    """
    Format an agent's contribution to highlight the specific contribution.
    
    Args:
        agent_id: Identifier of the contributing agent
        contribution: The agent's contribution text
        
    Returns:
        Formatted contribution
    """
    agent_names = {
        "university": "University Information",
        "motivator": "Motivational Support"
    }
    
    agent_name = agent_names.get(agent_id, agent_id.capitalize())
    
    return f"{agent_name}: {contribution}"


# For local testing
if __name__ == "__main__":
    # Set up environment for testing
    if not os.environ.get("OPENAI_API_KEY"):
        from dotenv import load_dotenv
        load_dotenv()
    
    # Test with sample responses
    test_query = "I'm worried about whether I'll be able to handle the computer science curriculum. What are the requirements and do you have any tips for managing the workload?"
    
    test_responses = {
        "university": "The Computer Science major requires completion of 120 credit hours including core courses in programming, data structures, algorithms, computer organization, and software engineering. Students must maintain a GPA of at least 2.5 in major courses. Specific course requirements include CS101, CS201, CS301, and MATH220. The program typically takes 4 years to complete with a full-time course load.",
        
        "motivator": "It's completely normal to feel concerned about a challenging curriculum like Computer Science. Many successful CS graduates had the same worries when they started! Remember that every student develops at their own pace, and universities have various support resources to help you succeed. For managing the workload, I recommend breaking large projects into smaller tasks, forming study groups with classmates, and maintaining a consistent schedule for coding practice. Also, don't hesitate to use office hours - professors and TAs are there to help you understand difficult concepts."
    }
    
    aggregated = aggregate_responses(test_responses, test_query, "academic anxiety")
    print(f"Original Query: {test_query}\n")
    print(f"Aggregated Response: {aggregated}")