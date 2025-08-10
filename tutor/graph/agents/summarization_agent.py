from typing import Dict
from tutor.common.summarizer import ConversationSummarizer
from tutor.graph.config import LLM, MAX_TURNS
from tutor.graph.functions.helpers import GraphState



async def summarize_agent(state: GraphState) -> Dict:
    """
    If necessary, summarize the conversation when state exceeds limits (e.g., token count or message count).
    """
    try:
        summarizer = ConversationSummarizer(MAX_TURNS)
        if await summarizer.should_summarize(state):
            summary = await summarizer.create_summary(state, LLM)
            state = summarizer.compress_conversation(state.copy(), summary)


    except Exception as e:
        print(f"Summarization failed: {e}")

    # Update state after summarization
    state["next_agent"] = "orchestrator"
    return state
