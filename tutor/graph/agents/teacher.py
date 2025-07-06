from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from tutor.graph.functions.helpers import GraphState
from tutor.graph.config import LLM

async def teacher_agent(state: GraphState) -> Dict:
    system_prompt = """You are the Teacher. Your role is to explain concepts and answer subject-specific questions.
    Use `retrieve_course_material_tool` for course content and `google_search_tool` as a backup.
    The student profile is the following: \n"""

    for key in state['student_profile']:
        text = key + ": ''"
        if state['student_profile'][key]:
            text = key + ' : ' + str(state['student_profile'][key])
        system_prompt += text + '\n'

    system_prompt += f"""\n\n
    Task: {state['agent_task_description']}

    After explaining, decide if a quick knowledge check is appropriate to gauge understanding.
    If so, identify the specific `topic_for_kc`. Otherwise, leave it null.
    If appropriate, also set the `current_topic_in_focus` property to the string describing the focus of the conversation.
    Also, provide a brief `updated_progress` note if the student seems to grasp the concept.
    
    At the end of your answer add the following information:
       #academic_progress: <your assessment of the academic progress of the student based on her entire history>#\n
       #knowledge_check": <the topic you think should be the subject of a knowledge check based on her entire history>#
    """

    # Preparing the prompt for the Teacher Agent
    user_query = state['messages'][-1].content
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        *state['messages'],
        ("user", f"{user_query}"),
    ])

    #structured_llm = LLM.bind_tools([retrieve_course_material_tool, google_search_tool]).with_structured_output(TeacherDecision)
    decision = await LLM.ainvoke(prompt.format(user_query=user_query))

    # Update state based on the LLM's structured decision
    topic_in_focus = ""

    try:
        state["student_profile"]["academic_progress"]=decision.content.split('#')[1].split(':')[1]
        topic_in_focus = decision.content.split('#')[2].split(':')[1]
    except IndexError:
        pass

    return {
        "messages": decision,
        "current_topic_in_focus": topic_in_focus,
        "student_profile": state["student_profile"],
    }