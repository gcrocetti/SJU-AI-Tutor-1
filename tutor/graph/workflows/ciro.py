from datetime import datetime, timezone
from langchain_core.messages import HumanMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from tutor.common.summarizer import ConversationSummarizer
from tutor.graph.config import STATE_DB, LLM, TOOLS
from tutor.graph.agents.responder import responder_agent
from tutor.graph.agents.academic_coach import academic_coach_agent
from tutor.graph.agents.summarization_agent import summarize_agent
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

    def __init__(self, email: str):
        summarizer_config = {"max_turns": 20} #<TODO: Maybe we can pass the config as a parameter>
        self.summarizer = ConversationSummarizer(**summarizer_config)
        self.thread_id = email
        self.email = email

    @classmethod
    async def init_graph(cls):
        """Initializes the LangGraph once for all users (if not already built)."""
        if cls._app is not None:
            return  # Already built

        async def route_agent(state: GraphState) -> str:
            next_agent = state.get("next_agent")
            if not next_agent or next_agent not in ["academic_coach", "teacher", "motivator", "university", "clarify",
                                                    "END"]:
                print(f"Invalid or missing next_agent: {next_agent}. Defaulting to END.")
                return "END"

            return next_agent

        async def route_back_to_caller(state: GraphState) -> str:
            return "end_node"

        conn = await aiosqlite.connect(STATE_DB)
        saver = AsyncSqliteSaver(conn)

        workflow = StateGraph(GraphState)
        workflow.add_node("summarizer", summarize_agent)
        workflow.add_node("orchestrator", orchestrator_agent)
        workflow.add_node("clarify", clarify_agent)
        workflow.add_node("academic_coach", academic_coach_agent)
        workflow.add_node("teacher", teacher_agent)
        workflow.add_node("motivator", motivator_agent)
        workflow.add_node("university", university_agent)
        workflow.add_node("responder", responder_agent)
        workflow.add_node("tools", ToolNode(TOOLS))

        workflow.add_edge(START, "summarizer")
        workflow.add_edge("summarizer", "orchestrator")

        workflow.add_conditional_edges("orchestrator", route_agent)

        for node in ["clarify", "academic_coach", "teacher", "motivator", "university"]:
            #workflow.add_edge(node, "end_node")
            workflow.add_conditional_edges(node, tools_condition, path_map={"tools": "tools", "__end__": "responder"})

        workflow.add_edge("tools", "responder")
        workflow.add_edge("responder", END)

        cls._app = workflow.compile(checkpointer=saver)

    async def process_message(self, user_input: str) -> str:
        """Processes a single message for this thread/user in a web environment."""
        config = {"configurable": {"thread_id": self.thread_id}}

        # 1. Load existing state (or initialize new one)
        current_state = await self._app.checkpointer.aget(config)

        if not current_state:
            print(f"Initializing new state for {self.thread_id}")
            current_state = {
                "student_profile": {
                    "email": self.email,
                    "academic_goals": ["Pass LST 1000X EDGE and declare my major."],
                    "academic_progress": [],
                    "knowledge_checker": [],
                    "emotional_state": [],
                    "last_check_in_time": datetime.now().isoformat(),
                },
                "messages": [],
                "routing_history": [],
                "current_depth": 0,
                "max_routing_depth": 10,
            }

        # Save initialized or restored state
        #s = await self._app.aupdate_state(config, current_state)

        # 2. Process new message and invoke the workflow
        inputs = {**current_state, "new_message": HumanMessage(content=user_input)}


        try:
            # Using invoke instead of streaming for simpler handling
            final_state = await self._app.ainvoke(inputs, config=config)

            # 3. Save (or update) the new state
#            try:
#                await self._app.aupdate_state(config, current_state)
#            except Exception as e:
#                print(f"Error updating state: {e}")

            # Extract response from final state and return the response
            if final_state and "messages" in final_state:
                # Save current state checkpointer
#                checkpoint = {"ts": datetime.now(timezone.utc).isoformat(), "id": self.thread_id}
#                await self._app.checkpointer.aput(config, checkpoint, metadata={}, new_versions={key: "1" for key in final_state})

                messages = final_state["messages"]
                if messages and hasattr(messages[-1], "content"):
                    return messages[-1].content

            return "No response generated."

        except Exception as e:
            print(f"Error during graph execution: {e}")
            return f"An error occurred: {str(e)}"

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