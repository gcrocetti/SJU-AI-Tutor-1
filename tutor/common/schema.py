"""
Common schema definitions for the tutor.

This module defines shared data models and schemas used across multiple tutor,
ensuring consistent data structure and validation.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Message in a conversation."""
    role: str = Field(..., description="The role of the sender (user or assistant)")
    content: str = Field(..., description="The content of the message")
    
    class Config:
        schema_extra = {
            "example": {
                "role": "user",
                "content": "What are the admission requirements for the CS program?"
            }
        }


class Conversation(BaseModel):
    """A conversation with message history."""
    session_id: str = Field(..., description="Unique identifier for the conversation session")
    messages: List[Message] = Field(default_factory=list, description="Messages in the conversation")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "abc123",
                "messages": [
                    {"role": "user", "content": "What majors do you offer?"},
                    {"role": "assistant", "content": "We offer many majors including Computer Science, Biology, etc."}
                ]
            }
        }


class SearchResult(BaseModel):
    """A search result from information retrieval."""
    title: str = Field(..., description="Title of the search result")
    link: str = Field(..., description="URL of the search result")
    snippet: str = Field(..., description="Text snippet from the search result")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Computer Science Department",
                "link": "https://university.edu/cs",
                "snippet": "The Computer Science department offers undergraduate and graduate programs..."
            }
        }


class QueryRequest(BaseModel):
    """Request to process a query through an agent."""
    query: str = Field(..., description="The user's query")
    session_id: str = Field(..., description="Session identifier for conversation context")
    message_history: Optional[List[Dict[str, Any]]] = Field(default=None, description="Previous messages in this conversation")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What are the requirements for the Computer Science major?",
                "session_id": "session-123",
                "message_history": [
                    {"role": "user", "content": "Hello, I have questions about your programs."},
                    {"role": "assistant", "content": "Hi there! I'd be happy to help. What would you like to know?"}
                ]
            }
        }


class QueryResponse(BaseModel):
    """Response from processing a query through an agent."""
    response: str = Field(..., description="The agent's response to the query")
    message_history: List[Dict[str, Any]] = Field(..., description="Updated message history including the new query and response")
    error: Optional[str] = Field(None, description="Error message if processing failed")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "The Computer Science major requires completion of 120 credits including core courses...",
                "message_history": [
                    {"role": "user", "content": "What are the requirements for the Computer Science major?"},
                    {"role": "assistant", "content": "The Computer Science major requires completion of 120 credits..."}
                ],
                "error": None
            }
        }


class Tool(BaseModel):
    """Definition of a tool that can be used by an agent."""
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    parameters: Dict[str, Any] = Field(..., description="Parameters the tool accepts")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "google_search",
                "description": "Search for information using Google Custom Search",
                "parameters": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                }
            }
        }


class ToolCallResult(BaseModel):
    """Result from calling a tool."""
    tool_name: str = Field(..., description="Name of the tool that was called")
    success: bool = Field(..., description="Whether the tool call succeeded")
    result: Optional[Any] = Field(None, description="Result from the tool call if successful")
    error: Optional[str] = Field(None, description="Error message if the tool call failed")
    
    class Config:
        schema_extra = {
            "example": {
                "tool_name": "google_search",
                "success": True,
                "result": [{"title": "CS Program", "link": "https://example.com", "snippet": "Program details..."}],
                "error": None
            }
        }


class AgentState(BaseModel):
    """State maintained by an agent during processing."""
    messages: List[Dict[str, Any]] = Field(..., description="Conversation message history")
    session_id: str = Field(..., description="Session identifier")
    query: str = Field(..., description="Current user query")
    needs_search: bool = Field(False, description="Whether information retrieval is needed")
    search_results: List[Dict[str, str]] = Field(default_factory=list, description="Search results if retrieved")
    final_response: Optional[str] = Field(None, description="Final response to the user")
    error: Optional[str] = Field(None, description="Error message if processing failed")
    
    class Config:
        schema_extra = {
            "example": {
                "messages": [{"role": "user", "content": "What are admission requirements?"}],
                "session_id": "sess-123",
                "query": "What are admission requirements?",
                "needs_search": True,
                "search_results": [{"title": "Admissions", "link": "https://example.com", "snippet": "Requirements..."}],
                "final_response": "To be admitted, you need to meet the following requirements...",
                "error": None
            }
        }