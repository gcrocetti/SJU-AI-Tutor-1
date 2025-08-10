import datetime
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from tutor.graph.functions.helpers import GraphState
from tutor.graph.config import LLM_NO_TOOLS


async def responder_agent(state: GraphState) -> Dict:
    # The system conversational component
    user_query = state['new_message'].content

    system_prompt = f"""You are CIRO, the conversational agent that receives the history of conversation with a student,
    her/his most recent question and the answer provided by other agents or the data retrieved from a tool.
    Your role is to consider the most recent question with the associated answer and provide a kind, empathetic, and 
    personal conversation with students. Remember their name, and if they did not provide it, ask them.
    
    These students comes with knowledge gaps and from underserved communities, so be particular kind.\n\n
    
    The student profile is the following: \n"""

    for key in state['student_profile']:
        text = key + ": ''"
        if state['student_profile'][key]:
            text = key + ' : ' + str(state['student_profile'][key])
        system_prompt += text + '\n'

    system_prompt += f"""\n\n
    Provide the answer to their question and engage the student with a supportive, empathetic conversation.\n\n
    {state['agent_task_description']}
    
    """

    # Preparing the prompt for the Motivator Agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        *state['messages'],
        ("user", f"{user_query}"),
    ])
    response = await LLM_NO_TOOLS.ainvoke(prompt.format(user_query=user_query))

    return {"messages": response}