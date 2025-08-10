from datetime import datetime
from typing import Dict
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from tutor.graph.functions.helpers import GraphState, KCDecision
from tutor.graph.config import LLM

async def knowledge_check_agent(state: GraphState) -> Dict:
    """Asks questions or evaluates answers for a specific topic."""
    print("\n--- KNOWLEDGE CHECK ---")

    # Read the current state to understand what is happening
    topic = state['agent_task_description']
    kc_state = state.get("knowledge_checker", {"step": 0, "question": "", "answer": "", "hint": "", "grade": 0, "feedback": ""})
    step = kc_state["step"]
    system_message = "You are the `knowledge_check` Agent that works with the `teacher` agent to ensure students understand the topic under study or revision.\n"
    # Determine if we are asking a question or evaluating an answer
    last_message = state['messages'][-1]
    user_prompt = ""
    if step == 0:
        # It is time for the knowledge_check agent to ask the question
        system_message += f"You are starting a knowledge check. Ask the student a concise question to test their understanding. \
        To help you formulate the question, here is the question asked by the student: `{last_message.content}`\n\n"

        user_prompt = f"""Check the knowledge of the student regarding {topic}.\n\n
        You are starting a knowledge check. Ask the student a concise question to test their understanding. \n
        To help you formulate the question, here is the question asked by the student: `{last_message.content}` which was answered by the teacher. \n\n
        TASK: Generate a single question as a knowledge check. Be very empathetic toward this student.\n\n
        OUTPUT:
        Generate a JSON object with the following fields:
        - `question`: the question you generated in this activity
        - `hint`: any hint you want to provide to the student for this question.
        """
    else:
        system_message += f"Consider the answer provided by the student to your question which you must evaluate, provide feedback, and decide if it satisfies the knowledge check."
        user_prompt = f"""You asked to the student the following question: `{kc_state["question"]}` and the user provided the following answer: `{kc_state["answer"]}`\n\n
        TASK: Evaluate the answer from the student.
        
        OUTPUT:
        Generate a JSON object with the following fields: 
        - `question`: "{kc_state["question"]}"
        - `answer`: "{kc_state["answer"]}"
        - `hint`: any hint you want to provide to the student for this question if you perceive a certain struggle in answer this question.
        - `grade`: a letter from A, A-, B+, B, B-, C+, C, C-` reflecting the quality of the answer. Do not go below C-.
        - `feedback`: your feedback to the student.
        """


    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("user", user_prompt),
    ])

    structured_llm = LLM.with_structured_output(KCDecision)
    decision = await structured_llm.ainvoke(prompt.format())


    if decision.grade:
        print("KNOWLEDGE CHECK session is over.")

        # Build the record for this knowledge check
        kc_record = {
            "timestamp": datetime.now(),
            "topic": topic,
            "knowledge_checker": decision
        }
        if not state["knowledge_checker"]["history"]:
            state["knowledge_checker"]["history"] = []

        state["knowledge_checker"]["history"].append(kc_record)

        # Update the overall academic progress
        # <TO DO: keep an history of the academic progress including the overall average>
        if decision.grade in ['A', 'B+', 'B', 'B-']:
            state['student_profile']['academic_progress'][topic] = 'Understood'
        else:
            state['student_profile']['academic_progress'][topic] = 'Needs Review'

        return {
            "knowledge_checker": {
                "step": step+1,
                "question": decision.question,
                "answer": decision.answer,
                "hint": decision.hint,
                "grade": decision.grade,
                "feedback": decision.feedback,
                "history": state["knowledge_checker"]["history"]
            },
            "next_agent": "END",
            "student_profile": state["student_profile"],
        }
    else:  # Start the knowledge check
        print('KNOWLEDGE CHECK: ' + decision.question)
        return {
            "knowledge_checker": {
                "step": step,
                "question": decision.question,
                "answer": decision.answer,
                "hint": decision.hint,
                "grade": decision.grade,
                "feedback": decision.feedback,
                "history": state["knowledge_checker"]["history"]
            },
            "next_agent": "orchestrator"
        }