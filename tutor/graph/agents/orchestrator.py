import datetime
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from tutor.graph.functions.helpers import GraphState, OrchestratorDecision
from tutor.graph.config import LLM, EMOTIONAL_KEYWORDS, MAX_ELAPSED_TIME


async def orchestrator_agent(state: GraphState) -> Dict:
    """
    Central router. Analyzes the user's query and routes to the appropriate agent.
    This is the only agent that decides the *next* agent.
    """
    print("\n--- ORCHESTRATOR ---")

    # Extract question from user and add it to the history.
    # Remember we are in an asynchronous environment using streaming, so we need to recreate the whole history
    user_msg = state["new_message"].content
    messages = state.get("messages", []).copy()
    messages.append(state["new_message"])

    # Add cycle detection
    routing_history = state.get("routing_history", [])
    current_depth = state.get("current_depth", 0)
    max_depth = state.get("max_routing_depth")

    # <TO DO - HANDLE LONG CONVERSATIONS max_depth > 500?>
    #if current_depth >= max_depth:
    #    print("Max routing depth reached. Ending conversation.")
    #    return {
    #        "messages": messages,
    #        "next_agent": "END",
    #        "agent_task_description": "Maximum conversation depth reached.",
    #    }

    # Proactive check-in logic
    student_profile = state["student_profile"]
    last_check_in = student_profile.get("last_check_in_time")

    if isinstance(last_check_in, str):
        last_check_in = datetime.datetime.strptime(last_check_in, "%Y-%m-%dT%H:%M:%S.%f")

    if last_check_in and (datetime.datetime.now() - last_check_in > datetime.timedelta(minutes=MAX_ELAPSED_TIME)):
        print("Proactive check-in triggered.")
        return {
            "next_agent": "motivator",
            "agent_task_description": "Proactively check in with the student. Ask them how they are feeling and if there is anything on their mind.",
        }

    # Use LLM to decide the route
    system_prompt = f"""You are the central Orchestrator of an AI Tutor. Your job is to analyze the latest user query 
    and the conversation history to determine the student's intent. Then, route them to the correct specialist agent.

    Available Agents:
    - ciro: For general conversations, introductions, and casual interactions with the student.
    - academic_coach: For study strategies, time management, goal setting, academic planning, and learning techniques.
    - teacher: For explaining concepts, homework help, specific subject questions, and academic content.
    - motivator: For emotional support, stress management, anxiety, lack of motivation, and mental wellness.
    - university: For university-specific information including:
      * Academic deadlines, policies, and procedures
      * Career services, job/internship opportunities, and career guidance
      * Campus resources, facilities, and services
      * Administrative matters and student support services
      * Resume building, interview preparation, and professional development
      * Graduate school preparation and career planning
    - clarify: If the user's query is ambiguous or you need more information to route properly.

    The student profile is the following: \n"""

    for key in state['student_profile']:
        text = key + ": ''"
        if state['student_profile'][key]:
            text = key + ' : ' + str(state['student_profile'][key])
        system_prompt += text + '\n'

    system_prompt += f"""\n\n

    Analyze the user message and decide the best agent to handle it.
    Provide a clear task for that agent. Prioritize the 'motivator' if you detect any emotional distress.
    If the student is introducing herself, introduce yourself as the 'CIRO' and route the request to the 'clarify' agent.
    Finally, if the student is answering a question, simply end the current conversation.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        *state['messages'],
        ("user", user_msg),
    ])

    structured_llm = LLM.with_structured_output(OrchestratorDecision)

    try:
        decision = await structured_llm.ainvoke(prompt.format(user_query=user_msg))
        print(f"Orchestrator Decision: Route to {decision.next_agent}. Task: {decision.task_description}")

        # Update routing tracking
        routing_history.append(decision.next_agent)

        return {
            "messages": messages,
            "next_agent": decision.next_agent,
            "agent_task_description": decision.task_description,
            "routing_history": routing_history,
            "current_depth": current_depth + 1,
        }
    except Exception as e:
        print(f"Orchestrator failed: {e}. Defaulting to teacher.")
        return {
            "messages": messages,
            "next_agent": "teacher",
            "agent_task_description": user_msg,  # Pass the original query
            "routing_history": routing_history,
            "current_depth": current_depth + 1,
        }