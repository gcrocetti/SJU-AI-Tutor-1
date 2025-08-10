from typing import Dict
from langchain_core.prompts import ChatPromptTemplate

from tutor.common.userManager import Event, UserManager
from tutor.common.utils import get_tag_value_by_key
from tutor.graph.functions.helpers import GraphState
from tutor.graph.config import LLM, EventType


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
    
    At the end of your answer add the following tags and make sure to use the proper format:
       #academic_progress: <your assessment of the academic progress of the student based on her entire history>#\n
       #knowledge_check": <the topic you think should be the subject of a knowledge check based on her entire history>#
    """

    # Preparing the prompt for the Teacher Agent
    user_query = state['messages'][-1].content
    user_email = state['student_profile']['email']

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        *state['messages'],
        ("user", f"{user_query}"),
    ])

    #structured_llm = LLM.bind_tools([retrieve_course_material_tool, google_search_tool]).with_structured_output(TeacherDecision)
    decision = await LLM.ainvoke(prompt.format(user_query=user_query))
    topic_in_focus = ""
    
    try:
        # Extract the value of #academic_progress# and/or #knowledge_check# and update the state and user history
        academic_progress = get_tag_value_by_key(decision.content, "academic_progress")
        topic_in_focus = get_tag_value_by_key(decision.content, "knowledge_check")

        if academic_progress != "":
            event = Event(user_email,EventType.ACADEMIC.value,academic_progress)
            state["student_profile"]["academic_progress"].append(academic_progress)
            if not UserManager.store_event(event):
                print("Event not stored")

        if topic_in_focus != "":
            event = Event(user_email,EventType.KNOWLEDGE.value,topic_in_focus)
            state["student_profile"]["knowledge_checker"].append(topic_in_focus)
            if not UserManager.store_event(event):
                print("Event not stored")

    except (AttributeError, IndexError):
        # Handle cases where content or the key does not exist
        pass

    return {
        "messages": decision,
        "current_topic_in_focus": topic_in_focus,
        "student_profile": state["student_profile"],
    }