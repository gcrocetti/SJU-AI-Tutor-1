import datetime
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from tutor.graph.config import STATE_DB, LLM, TOOLS
from tutor.graph.agents.academic_coach import academic_coach_agent
from tutor.graph.agents.clarify import clarify_agent
from tutor.graph.functions.helpers import GraphState, end_node
from tutor.graph.agents.orchestrator import orchestrator_agent
from tutor.graph.agents.teacher import teacher_agent
from tutor.graph.agents.motivator import motivator_agent
from tutor.graph.agents.university import university_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite

from tutor.graph.functions.tools import retrieve_course_material_tool, google_search_tool, google_sju_search_tool


class CiroTutor:
    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.app = None  # This will be set asynchronously

    @classmethod
    async def create(cls, thread_id: str):
        self = cls(thread_id)
        await self._build_graph()
        print(f"Ciro Tutor initialized for thread ID: {thread_id}")
        return self

    async def _build_graph(self):

        # Route agent function for the Orchestrator
        def route_agent(state: GraphState):
            next_agent = state.get("next_agent")
            print(f"Routing to: {next_agent}")

            if not next_agent:
                raise ValueError("Missing 'next_agent' key in state!")

            if next_agent == "END":
                return "end_node"

            valid_agents = {
                "clarify",
                "academic_coach",
                "teacher",
                "motivator",
                "university",
                "orchestrator"  # in case you're looping back
            }

            if next_agent not in valid_agents:
                raise ValueError(f"Invalid next_agent: {next_agent}")

            return next_agent

        def route_back_to_caller(state: GraphState) -> str:
            return state["next_agent"]  # previously set before tool call

        # Build Graph
        conn = await aiosqlite.connect(STATE_DB)
        saver = AsyncSqliteSaver(conn)

        # Initialize Graph
        workflow = StateGraph(GraphState)

        # Add agent nodes
        workflow.add_node("orchestrator", orchestrator_agent)
        workflow.add_node("clarify", clarify_agent)
        workflow.add_node("academic_coach", academic_coach_agent)
        workflow.add_node("teacher", teacher_agent)
        workflow.add_node("motivator", motivator_agent)
        workflow.add_node("university", university_agent)
        workflow.add_node("end_node", end_node)

        # Add reusable tools node
        workflow.add_node("tools", ToolNode(TOOLS))

        # Entry point
        workflow.add_edge(START, "orchestrator")

        # Primary routing by orchestrator
        workflow.add_conditional_edges("orchestrator", route_agent)

        # Agent-to-end transitions (default after completing their task)
        for node in ["clarify", "academic_coach", "teacher", "motivator", "university"]:
            workflow.add_edge(node, "end_node")

        # Tool routing for each agent that may call tools
        for node in ["clarify", "academic_coach", "teacher", "university", "motivator"]:
            workflow.add_conditional_edges(
                node,
                tools_condition,
                path_map={
                    "tools": "tools",  # If tools_condition returns "tools"
                    "__end__": "end_node"  # If tools_condition returns "no_tool"
                }
            )
            #workflow.add_edge("tools", node)  # Return from tools to the same agent

        workflow.add_conditional_edges("tools", route_back_to_caller)
        self.app = workflow.compile(checkpointer=saver)

        #display(Image( self.app.get_graph().draw_mermaid_png()))


    async def run_session(self):
        """Runs the interactive tutor session loop using async checkpointing."""
        print("\nWelcome to your intelligent tutor! Type 'quit' to exit.")
        config = {"configurable": {"thread_id": self.thread_id}}

        # Load or initialize state
        current_state = await self.app.aget_state(config)
        current_state = current_state[0]
        if not current_state:
            print("No existing state found. Initializing new student profile...")
            current_state = {
                "student_profile": {
                    "learning_style": "visual",
                    "academic_goals": ["Pass LST 1000X EDGE and declare my major."],
                    "academic_progress": {},
                    "emotional_state": ["neutral"],
                    "last_check_in_time": datetime.datetime.now().isoformat(),
                },
                "messages": [],
            }

        await self.app.aupdate_state(config, current_state)

        while True:
            user_input = input("\nStudent: ")
            if user_input.lower() == 'quit':
                print("Tutor: Goodbye!")
                break

            # Retrieve latest chat history or start fresh
            inputs = {"new_message": HumanMessage(content=user_input)}
            final_state = None
            partial_response = ""  # optional, if streaming text

            try:
                async for event in self.app.astream_events(inputs, config=config, version="v1", stream_mode="values"):
                    event_type = event.get("event")

                    # Handle streaming outputs (if model streams tokens)
                    if event_type == "on_chat_model_stream":
                        token = event["data"]["chunk"].content
                        print(token, end="", flush=True)
                        partial_response += token

                    # Optionally show agent transitions
                    elif event_type == "on_node_start":
                        print(f"\n→ Entering node: {event['name']}")

                    # Final state output
                    elif event_type == "on_chain_end":
                        final_state = event["data"]["output"]

                # Fallback if no streaming occurred
                if final_state:
                    print("\n")  # spacing after any streamed output
                    final_response = final_state.get("tutor_response", "I'm not sure how to respond to that.")
                    print("")

                    if final_state.get("escalation_flag"):
                        print("\n!!! URGENT: The system detected severe distress. Human intervention is required. !!!")
                else:
                    print("Tutor: I'm sorry, something went wrong and I couldn't generate a response.")

            except Exception as e:
                print(f"An error occurred during graph execution: {e}")
                print("Tutor: I'm sorry, I encountered an issue. Could you please try again.")


async def main():
    tutor = await CiroTutor.create(thread_id="student_session_demo")
    await tutor.run_session()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())