from typing import TypedDict, List, Dict, Optional, Annotated, Callable, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

# Shared State Definition (LangGraph StateGraph State)
class GraphState(TypedDict):
    """
    Represents the shared state for the LangGraph workflow.
    It is append-only, ensuring memory of past interactions.
    """
    new_message: HumanMessage
    messages: Annotated[List[BaseMessage], add_messages] # Automatically appends messages
    student_profile: Dict
    agent_task_description: Optional[str]
    retrieved_content: Optional[List[Dict]]
    current_topic_in_focus: Optional[str]
    knowledge_checker: Optional[Dict] # Element used by the knowledge checker
    escalation_flag: bool
    tutor_response: str
    next_agent: str  # The name of the next agent to route to

# Pydantic models for structured output from LLM agents
class OrchestratorDecision(BaseModel):
    """The Orchestrator's routing decision and plan for the next agent."""
    next_agent: Literal["academic_coach", "teacher", "motivator", "university", "clarify"] = Field(
        description="The name of the agent to route to next."
    )
    task_description: str = Field(
        description="A clear, concise, and reformulated task for the selected agent based on the user's query."
    )
    notes: str = Field(description="A brief explanation for the routing decision.")


class ToolTopic(BaseModel):
    tool_calls: List = Field(description="The list of tool calls identified by the agent.")

async def end_node(state: GraphState) -> Dict:
    """A simple node to add the final response to the chat history before ending."""
    tutor_response = state['messages'][-1].content
    print(" TUTOR: " + tutor_response)

    return state

# Execute tool functions for all the notes that are tool-enabled
def execute_tools(state: ToolTopic):
    tool_calls = state.tool_calls
    results = []
    for t in tool_calls:
        result = tool_calls[t['name']].invoke(t['args'])
        results.append(
            ToolMessage(
                tool_call_id=t['id'],
                name=t['name'],
                content=str(result)
            )
        )

    return {'messages': results}