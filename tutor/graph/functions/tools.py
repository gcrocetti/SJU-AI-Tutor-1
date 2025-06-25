from langchain_core.tools import tool, Tool
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from tutor.config import PINECONE_API_KEY, PINECONE_INDEX_NAME, EMBEDDING_MODEL_NAME
from tutor.graph.config import MAX_DOCS_RETRIEVED

# Tool Definitions
# I will implement these tools as I go through the tutor implementation

search = GoogleSearchAPIWrapper()

google_search_tool = Tool(
    name="google-search",
    func=search.run,
    description="Use this tool to search the web using Google Programmable Search"
)

google_sju_search_tool = Tool(
    name="google-sju-search",
    func=lambda q: search.run(f"site:stjohns.edu {q}"),
    description="Use this tool to search the web using Google Programmable Search"
)

@tool
def retrieve_course_material_tool(query: str) -> str:
    """
    Retrieves relevant course content, lecture notes, study tips, or explanations from the internal knowledge base.
    Use this for any question related to a specific course.
    """
    print(f"\n--- Calling Course Material Tool with query: '{query}' ---")

    embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
    vector_store = PineconeVectorStore(
        pinecone_api_key=PINECONE_API_KEY,
        index_name=PINECONE_INDEX_NAME,
        embedding=embedding_model,
    )

    try:
        # Perform similarity search
        docs = vector_store.similarity_search(query, k=MAX_DOCS_RETRIEVED) # Retrieve top 3 relevant documents
        if not docs:
            return "No relevant course information found in the knowledge base."

        # Format the retrieved content
        retrieved_info = "\n".join([doc.page_content for doc in docs])
        return f"Retrieved course information:\n{retrieved_info}"
    except Exception as e:
        print(f"Error during Pinecone Course Info retrieval: {e}")
        return "An error occurred while retrieving course information. Please try again later or rephrase your query."
