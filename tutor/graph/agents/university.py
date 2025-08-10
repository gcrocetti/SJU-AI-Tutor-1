from typing import Dict
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from tutor.graph.functions.helpers import GraphState
from tutor.graph.config import LLM


async def university_agent(state: GraphState) -> Dict:

    # We know we have to perform a search, so let's do it right away instead of asking the LLM to call the tool.
    # It saves execution time and money.
    user_query = state["new_message"].content

    system_prompt = f"""
        You are the University Agent at St. John's University answering any question related to the university from office location to dates, from faculty information to financial opportunities.\n
        You answer questions using the most accurate, up-to-date university info and performing a Google search if necessary.\n
        For any information related to the LST 1000X course, use the knowledge retrieval tool "retrieve_course_material_tool"\n\n
        
        Here is the student profile:
        """
    for key, val in state['student_profile'].items():
        system_prompt += f"{key}: {val}\n"

    # Preparing the prompt for the University Agent
    messages = [
        SystemMessage(content=system_prompt),
        *state["messages"],
        HumanMessage(content=user_query),
    ]

    prompt = ChatPromptTemplate.from_messages(messages)

    #structured_llm = LLM.with_structured_output(AgentResponse)
    decision = await LLM.ainvoke(prompt.format())

    return {"messages": decision}
