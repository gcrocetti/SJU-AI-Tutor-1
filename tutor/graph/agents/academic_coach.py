from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from tutor.graph.config import LLM
from tutor.graph.functions.helpers import GraphState


async def academic_coach_agent(state: GraphState) -> Dict:
    system_prompt = f"""You are the Academic Coach. Your goal is to help the student with study strategies, time management, and goal setting.
    Use the `retrieve_course_material_tool` for general study advice or the `google_search_tool` for advanced study advice.\n\n
    The student profile is the following: \n"""

    for key in state['student_profile']:
        text = key + ": ''"
        if state['student_profile'][key]:
            text = key + ' : ' + str(state['student_profile'][key])
        system_prompt += text + '\n'

    system_prompt += f"""\n\n
    TASK: {state['agent_task_description']}\n\n
    Provide an actionable and encouraging response. If the user sets a new academic goal, mention it at the end of your 
    response with the string #academic_goal:<value># with value the new academic goal that you and the student have identified."""

    # Preparing the prompt for the Motivator Agent
    user_query = state['new_message'].content
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        *state['messages'],
        ("user", f"{user_query}"),
    ])

    decision = await LLM.ainvoke(prompt.format())
    try:
        state["student_profile"]["academic_goals"] = decision.content.split('#')[1].split(':')[1]
    except IndexError:
        pass

    return {"messages": decision}