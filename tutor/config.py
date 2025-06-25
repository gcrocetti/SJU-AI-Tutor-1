import os

# Pinecone configuration
PINECONE_INDEX_NAME = "ciro"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_NAMESPACE = 'LST'
UPSERT_BATCH_SIZE = 100

# GOOGLE API KEYS
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# LLMs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Embeddings and document process configuration
EMBEDDING_MODEL_NAME = "text-embedding-3-small"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 100

# New logging level config: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOGGING_LEVEL = "DEBUG"  # Change to "INFO" or "ERROR" in production