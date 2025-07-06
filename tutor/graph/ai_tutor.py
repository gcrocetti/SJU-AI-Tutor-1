from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from tutor.indexing import (
    PINECONE_INDEX_NAME,
    PINECONE_API_KEY,
    PINECONE_NAMESPACE
)
from tutor.university_agent.tools import get_llama_embedding

embedded_query = get_llama_embedding("What does this class cover?")

pc_index = Pinecone(api_key=PINECONE_API_KEY).Index(PINECONE_INDEX_NAME)

vectorstore = PineconeVectorStore(
    index=pc_index,
    text_key="chunk_text",
)

# Perform actual similarity search using this embedding
results = pc_index.query(
    top_k=top_k,
    vector=embedded_query,
    include_metadata=True
)

# Format results
for i, match in enumerate(results["matches"]):
    print(f"\n--- Match #{i+1} ---")
    print(f"Score: {match['score']:.4f}")
    print("Metadata:", match.get("metadata", {}))

pc_index = Pinecone(api_key=PINECONE_API_KEY).Index(PINECONE_INDEX_NAME)
results = pc_index.search(
    namespace=PINECONE_NAMESPACE,
    query={
        "top_k": 10,
        "inputs": {
            'text': query
        }
    }
)

for result in results["result"]["hits"]:
    print(f'Sentence: {result["fields"]["chunk_text"]} Semantic Similarity Score: {result["_score"]}\n')