from datetime import datetime

from langchain_core.messages import SystemMessage

from tutor.graph.functions.helpers import GraphState
from typing import List, Dict, Any
from langgraph.graph.message import RemoveMessage

class ConversationSummarizer:
    """Handles conversation summarization to manage memory"""

    def __init__(self, max_turns: int = 20, summary_prompt_template: str = None):
        self.max_turns = max_turns
        self.summary_prompt_template = summary_prompt_template or self._default_summary_prompt()

    def _default_summary_prompt(self) -> str:
        return """You are an AI assistant helping to summarize a tutoring conversation. 
        Please create a concise summary of the key learning points, student progress, 
        and important context from this conversation history.

        Focus on:
        - Main topics discussed
        - Student's understanding level and progress
        - Key concepts taught
        - Areas where student struggled
        - Current learning objectives
        - Any important context for continuing the conversation

        Conversation history:
        {conversation_history}

        Summary:"""

    async def should_summarize(self, state: GraphState) -> bool:
        """Determine if conversation should be summarized"""
        return len(state["messages"]) > self.max_turns

    async def create_summary(self, state: GraphState, llm_client) -> str:
        """Create a summary of the conversation history"""
        # Format conversation history
        conversation_text = self._format_conversation(state["messages"])

        # Create summary prompt
        prompt = self.summary_prompt_template.format(
            conversation_history=conversation_text
        )

        # Generate summary using your LLM client
        summary = await self._generate_summary(prompt, llm_client)
        return summary

    def _format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        #Format messages into readable conversation history
        formatted = []

        for msg in messages:
            # Handle LangChain message objects
            if hasattr(msg, 'content') and hasattr(msg, '__class__'):
                role = msg.__class__.__name__.replace('Message', '').lower()
                content = msg.content
                # You can add timestamp if available
                timestamp = getattr(msg, 'timestamp', datetime.now().isoformat())
                formatted.append(f"[{timestamp}] {role}: {content}")
            # Handle dict format (fallback)
            elif isinstance(msg, dict):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                timestamp = msg.get('timestamp', datetime.now().isoformat())
                formatted.append(f"[{timestamp}] {role}: {content}")

        return "\n".join(formatted)

    async def _generate_summary(self, prompt: str, llm_client) -> str:
        from langchain_core.prompts import ChatPromptTemplate

        chat_prompt = ChatPromptTemplate.from_messages([
            ("human", prompt)
        ])

        response = await llm_client.ainvoke(chat_prompt.format())
        return response.content

    def compress_conversation(self, state: GraphState, summary: str) -> GraphState:
        """Replace old messages with summary and keep recent messages"""

        # Keep the last few messages for immediate context and delete all other messages
        updated_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-5]]

        # Create summary message
        summary_message = SystemMessage(content=f"Previous conversation summary: {summary}")

        # Update state with compressed history
        messages = [summary_message] + updated_messages
        state["messages"] = messages

        return state