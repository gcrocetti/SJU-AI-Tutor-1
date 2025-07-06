import datetime
from langchain_core.messages import HumanMessage
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


class CiroTutor:
    _app = None

    def __init__(self, thread_id: str):
        self.thread_id = thread_id

    @classmethod
    async def init_graph(cls):
        """Initializes the LangGraph once for all users (if not already built)."""
        if cls._app is not None:
            return  # Already built

        async def route_agent(state: GraphState) -> str:
            next_agent = state.get("next_agent")
            if not next_agent:
                raise ValueError("Missing 'next_agent' in state.")
            if next_agent == "END":
                return "end_node"
            return next_agent

        async def route_back_to_caller(state: GraphState) -> str:
            return state["next_agent"]

        conn = await aiosqlite.connect(STATE_DB)
        saver = AsyncSqliteSaver(conn)

        workflow = StateGraph(GraphState)
        workflow.add_node("orchestrator", orchestrator_agent)
        workflow.add_node("clarify", clarify_agent)
        workflow.add_node("academic_coach", academic_coach_agent)
        workflow.add_node("teacher", teacher_agent)
        workflow.add_node("motivator", motivator_agent)
        workflow.add_node("university", university_agent)
        workflow.add_node("end_node", end_node)
        workflow.add_node("tools", ToolNode(TOOLS))

        workflow.add_edge(START, "orchestrator")
        workflow.add_conditional_edges("orchestrator", route_agent)

        for node in ["clarify", "academic_coach", "teacher", "motivator", "university"]:
            workflow.add_edge(node, "end_node")
            workflow.add_conditional_edges(
                node,
                tools_condition,
                path_map={"tools": "tools", "__end__": "end_node"}
            )

        workflow.add_conditional_edges("tools", route_back_to_caller)

        cls._app = workflow.compile(checkpointer=saver)

    async def process_message(self, user_input: str) -> str:
        """Processes a single message for this thread/user in a web environment."""
        config = {"configurable": {"thread_id": self.thread_id}}

        # 1. Load existing state (or initialize new one)
        current_state = await self._app.aget_state(config)
        current_state = current_state[0]  # aget_state returns a list

        if not current_state:
            print(f"Initializing new state for {self.thread_id}")
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

        # 2. Save (or update) the initial state
        await self._app.aupdate_state(config, current_state)

        # 3. Process new message
        inputs = {"new_message": HumanMessage(content=user_input)}
        final_state = None
        try:
            async for event in self._app.astream_events(inputs, config=config, version="v1", stream_mode="values"):
                if event.get("event") == "on_chain_end":
                    final_state = event["data"]["output"]
        except Exception as e:
            return f"An error occurred: {str(e)}"

        # 4. Extract and return the response
        # Safely extract the last message from the message list
        messages = final_state.get("messages", [])
        if messages and hasattr(messages[-1], "content"):
            return messages[-1].content
        else:
            return "No response generated."

    async def run_session(self):
        """Runs a local, console-based test loop for this tutor instance."""
        print("\nWelcome to your intelligent tutor! Type 'quit' to exit.\n")
        config = {"configurable": {"thread_id": self.thread_id}}

        # Step 1: Load or initialize state
        current_state = await self._app.aget_state(config)
        current_state = current_state[0]

        if not current_state:
            print("🆕 No previous state found. Initializing a new student profile...")
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

        # Save initialized or restored state
        await self._app.aupdate_state(config, current_state)

        # Step 2: Loop for interaction
        while True:
            user_input = input("\nStudent: ")
            if user_input.lower() == 'quit':
                print("\nTutor: Goodbye! Come back soon.\n")
                break

            # Step 3: Prepare input and process through the graph
            inputs = {"new_message": HumanMessage(content=user_input)}
            final_state = None
            partial_response = ""

            try:
                async for event in self._app.astream_events(inputs, config=config, version="v1", stream_mode="values"):
                    event_type = event.get("event")

                    if event_type == "on_node_start":
                        print(f"\nEntering node: {event['name']}")

                    elif event_type == "on_chat_model_stream":
                        token = event["data"]["chunk"].content
                        print(token, end="", flush=True)
                        partial_response += token

                    elif event_type == "on_chain_end":
                        final_state = event["data"]["output"]

                print()  # spacing

                # Step 4: Display final response if not already streamed
                if final_state:
                    messages = final_state.get("messages", [])
                    if messages and hasattr(messages[-1], "content"):
                        response = messages[-1].content
                        if not partial_response:  # if streaming didn't already show it
                            print(f"Tutor: {response}")
                else:
                    print("⚠️ Tutor: Something went wrong. No response was generated.")

                # Optional: alert for escalation
                if final_state and final_state.get("escalation_flag"):
                    print("\nSYSTEM ALERT: The system detected distress. Human intervention is recommended.")

            except Exception as e:
                print(f"\nAn error occurred: {e}")


async def main():
    # For Demo purposes and local testing
    thread_id = "student_session_demo"

    # Step 1: Compile and cache the graph once
    await CiroTutor.init_graph()

    # Step 2: Create a tutor instance with a test thread ID
    tutor = CiroTutor(thread_id)

    # Step 3: Launch console session
    await tutor.run_session()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())