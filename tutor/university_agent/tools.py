"""
Tools for the University Information Agent.

This module implements various tools used by the agent, primarily for:
1. Retrieving information from Google Custom Search
2. Processing and formatting search results

Updated for LangChain 0.3+ compatibility
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import requests
from urllib.parse import urlencode
from langchain.embeddings.base import Embeddings
from pinecone import Pinecone

class PineconeLlamaEmbedder(Embeddings):
    # Class used to embed queries using lLama embeddings.
    def __init__(self, pc_index: Pinecone):
        self.pc_index = pc_index

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.get_llama_embedding(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.get_llama_embedding(text)

    def get_llama_embedding(self, text: str) -> list[float]:
        # Gets the embedding of the text using the server-side embedding features ('integrated embedding' of Pinecone)
        res = self.pc_index.query(
            top_k=1,  # We don’t care about results
            vector=None,
            query=text,  # ✅ This triggers embedding
            include_values=True,
            include_metadata=False,
            namespace=None
        )

        return res["matches"][0]["values"]  # This is the embedding of your query


# Set up logging
logger = logging.getLogger(__name__)

def google_search_query(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Performs a Google Custom Search to retrieve information relevant to a query.
    
    Args:
        query: The search query string
        num_results: Number of results to retrieve (max 10)
        
    Returns:
        List of search result dictionaries with title, link, and snippet
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")
    
    if not api_key or not cse_id:
        logger.error("Google API key or CSE ID not found in environment variables")
        raise ValueError("Google API key or CSE ID not configured")
    
    # Limit to maximum of 10 results (Google CSE constraint)
    num_results = min(num_results, 10)
    
    # Construct query parameters
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query,
        'num': num_results
    }
    
    # Create the URL
    url = f"https://www.googleapis.com/customsearch/v1?{urlencode(params)}"
    
    try:
        # Make the request
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse response
        search_results = response.json()
        
        # Extract relevant information
        formatted_results = []
        if 'items' in search_results:
            for item in search_results['items']:
                result = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                }
                formatted_results.append(result)
        
        logger.info(f"Retrieved {len(formatted_results)} search results")
        return formatted_results
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making Google search request: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing Google search response: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Google search: {e}")
        raise