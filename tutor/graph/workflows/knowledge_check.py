import datetime
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from tutor.graph.config import STATE_DB
from tutor.graph.agents.academic_coach import academic_coach_agent
from tutor.graph.agents.clarify import ciro_agent
from tutor.graph.functions.helpers import GraphState, end_node
from tutor.graph.agents.orchestrator import orchestrator_agent
from tutor.graph.agents.teacher import teacher_agent
from tutor.graph.agents.knowledge_checker import knowledge_check_agent
from tutor.graph.agents.motivator import motivator_agent
from tutor.graph.agents.university import university_agent

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite

class KnowledgeCheck:
    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.app = None  # This will be set asynchronously

    @classmethod
    async def create(cls, thread_id: str):
        self = cls(thread_id)
        await self._build_graph()
        print(f"Knowledge Check initialized for thread ID: {thread_id}")
        return self

    async def _build_graph(self):
        conn = await aiosqlite.connect(STATE_DB)
        saver = AsyncSqliteSaver(conn)

        workflow = StateGraph(GraphState)
        workflow.add_node("start", START)
        workflow.add_node("knowledge_check", knowledge_check_agent)
        workflow.add_node("end_node", END)

        workflow.set_entry_point("start")

        workflow.add_edge("start", "knowledge_check")
        workflow.add_edge("knowledge_check", "end_node")

        self.app = workflow.compile(checkpointer=saver)

    async def run_session(self):
        """Runs the interactive knowledge check session loop using async checkpointing."""
        print("\nWelcome to your Knowledge Checker tutor! Type 'quit' to exit.")
        config = {"configurable": {"thread_id": self.thread_id}}

        # Load or initialize state
        existing_state = await self.app.aget_state(config)
        if not existing_state:
            print("No existing state found. Initializing new student profile...")
            initial_profile = {
                "learning_style": "visual",
                "academic_goals": ["Pass Calculus I"],
                "academic_progress": {},
                "emotional_state": "neutral",
                "last_check_in_time": datetime.datetime.now().isoformat(),
            }
            await self.app.aupdate_state(config, {
                "student_profile": initial_profile,
                "tutor_response": []
            })

        while True:
            # Invoke the Knowledge Checker to generate a challenge question

            user_input = input("\nStudent: ")
            if user_input.lower() == 'quit':
                print("Knowledge Checker: Goodbye!")
                break

            inputs = {"messages": [HumanMessage(content=user_input)]}
            final_state = None

            try:
                async for event in self.app.astream_events(inputs, config=config, version="v1", stream_mode='values'):
                    if event["event"] == "on_chain_end":
                        final_state = event["data"]["output"]

                if final_state:
                    final_response = final_state.get("tutor_response", "I'm not sure how to respond to that.")
                    print("\nTutor:", final_response)

                    if final_state.get("escalation_flag"):
                        print("\n!!! URGENT: The system detected severe distress. Human intervention is required. !!!")
                else:
                    print("Tutor: I'm sorry, something went wrong and I couldn't generate a response.")
            except Exception as e:
                print(f"An error occurred during graph execution: {e}")
                print("Tutor: I'm sorry, I encountered an issue. Could you please try again?")


async def main():
    tutor = await CiroTutor.create(thread_id="student_session_demo")
    await tutor.run_session()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())