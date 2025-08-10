import re
import datetime
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from tutor.graph.functions.helpers import GraphState
from tutor.graph.config import DISTRESS_KEYWORDS, EventType
from tutor.graph.config import LLM
from tutor.common.userManager import Event,UserManager
from tutor.common.utils import get_tag_value_by_key


async def motivator_agent(state: GraphState) -> Dict:
    # Critical safety check - this runs BEFORE the LLM for immediate action
    user_query = state['new_message'].content
    user_email = state['student_profile']['email']

    # <TO DO: we can use the emotional state instead of hardcoding a distress signal>
    if any(keyword in user_query.lower() for keyword in DISTRESS_KEYWORDS):
        print("\n!!! SEVERE DISTRESS DETECTED - ESCALATING !!!")
        response = ("It sounds like you are in significant distress. Your safety is the most important thing. "
                    "Please reach out for help immediately. You can call or text 988 in the US and Canada "
                    "to reach the Suicide & Crisis Lifeline. Please talk to someone now.")
        return {"final_response": response, "escalation_flag": True, "next_agent": "END"}

    system_prompt = f"""You are the Motivator agent. Your role is to provide emotional support and encouragement to undergraduate students.
    These students comes with knowledge gaps and from underserved communities that, often, fail to declare their major and go through a remediation process.\n\n
    
    The student profile is the following: \n"""

    for key in state['student_profile']:
        text = key + ": ''"
        if state['student_profile'][key]:
            text = key + ' : ' + str(state['student_profile'][key])
        system_prompt += text + '\n'

    system_prompt += f"""\n\n
    Provide a supportive, empathetic response. Assess the student's emotional state based on their message.
    
    At the end of the output, add a string with the following format #emotional_state: <value># with value is your opinion on the emotional state of the student according to the chat history.
    """

    # Preparing the prompt for the Motivator Agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        *state['messages'],
        ("user", f"{user_query}"),
    ])
    decision = await LLM.ainvoke(prompt.format(user_query=user_query))

    try:
        # Extract the value of #emotional_state:<value>#, update the state and store it to the user history
        emotional_state = get_tag_value_by_key(decision.content, "emotional_state")
        if emotional_state != "":
            motivator_event = Event(user_email,EventType.MOTIVATOR.value,emotional_state)
            state["student_profile"]["emotional_state"].append(emotional_state)
            if not UserManager.store_event(motivator_event):
                print("Event not stored")
    except (AttributeError, IndexError):
        # Handle cases where content or the key does not exist
        pass

    # <TO DO: UPDATING CHECK IN TIME TO AVOID TRIGGERING>
    state["student_profile"]["last_check_in_time"] = datetime.datetime.now()


    return {
        "messages": decision,
        "student_profile": state["student_profile"],
    }