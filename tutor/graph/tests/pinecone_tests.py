from pinecone import Pinecone
from tutor.graph.config import PINECONE_API_KEY, PINECONE_INDEX_NAME
# Ensure the Pinecone resources are there

pc = Pinecone()  # or use os.environ
index = pc.Index("ciro")
pc.list_indexes()
