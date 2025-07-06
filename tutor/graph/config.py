from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from tutor.graph.functions.tools import retrieve_course_material_tool, google_search_tool, google_sju_search_tool

HISTORY_LENGTH = 10
CHAT_MODEL = "gpt-4o"
TEMPERATURE = 0.5

# Maximum time (in minutes) of inactivity allowed before triggering the motivator
MAX_ELAPSED_TIME=120

# Definition of the llm and tools
TOOLS = [retrieve_course_material_tool, google_search_tool, google_sju_search_tool]
LLM = ChatOpenAI(model=CHAT_MODEL, temperature=TEMPERATURE).bind_tools(TOOLS)

# Dictionaries
EMOTIONAL_KEYWORDS = ["stressed", "anxious", "overwhelmed", "demotivated", "sad", "can't focus", "bad day", "struggling", "unmotivated"]
EMOTIONAL_STATE = ["stressed", "overwhelmed"]
DISTRESS_KEYWORDS = ["suicidal", "ending it all", "kill myself", "hopeless", "want to die"]

# Parameters for agents
MOTIVATOR_CHECK_MINUTES = 5
STATE_DB = "C:/tmp/ciro_state.db"