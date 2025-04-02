"""
Tools for the Teacher Agent.

This module implements specialized tools for:
1. Retrieving educational content from Pinecone vector database
2. Processing educational content for student learning
3. Tracking student knowledge and progress
"""

import os
import sys
import json
import logging
from typing import List, Dict, Any, Optional

# Ensure we can import from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Now import the modules
from pinecone import Pinecone
from agents.common.utils import setup_logging

# Configure logging
logger = logging.getLogger(__name__)
setup_logging()

def initialize_pinecone(index_name: str = "ciro") -> Optional[Any]:
    """
    Initialize the Pinecone client and connect to the specified index.
    
    Args:
        index_name: Name of the Pinecone index to connect to
        
    Returns:
        Pinecone index object or None if initialization failed
    """
    try:
        # The API key is hard-coded for testing
        pc_api_key = "pcsk_4bLxw7_UgJTr4hZhDjozufcqjEZvPnQWGkHyjARYU7T9uVNy18fArhvpXcVVWaphDGpQki"
        
        # Initialize Pinecone
        pc_db = Pinecone(api_key=pc_api_key)
        
        # For testing, we'll create a mock index object since we might not have access to the actual index
        logger.info(f"Would connect to Pinecone index: {index_name}")
        
        # Return a mock index object for testing purposes
        mock_index = {
            "name": index_name,
            "query": lambda **kwargs: {
                "matches": [
                    {
                        "score": 0.95,
                        "metadata": {
                            "text": "This is sample text about the requested topic.",
                            "source": "Sample Textbook",
                            "page": "42",
                            "summary": "Key concept explanation",
                            "keywords": "sample, test, concept",
                            "categories": "programming, computer science"
                        }
                    },
                    {
                        "score": 0.85,
                        "metadata": {
                            "text": "Additional information related to the topic with examples.",
                            "source": "Course Materials",
                            "page": "15",
                            "summary": "Examples and exercises",
                            "keywords": "examples, practice, exercises",
                            "categories": "examples, practice"
                        }
                    }
                ]
            }
        }
        return mock_index
            
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone: {e}")
        return None


def get_openai_embedding(text: str, client=None, model: str = "text-embedding-3-small") -> List[float]:
    """
    Generate embeddings for the query text using OpenAI's embedding model.
    For testing purposes, this returns a mock embedding.
    
    Args:
        text: The text to embed
        client: OpenAI client (optional, will create one if not provided)
        model: Embedding model to use
        
    Returns:
        Vector embedding for the text
    """
    try:
        # For testing, return a mock embedding (1536-dimensional vector)
        # In a real implementation, we would generate actual embeddings
        logger.info(f"Would generate embedding for: {text[:30]}...")
        return [0.1] * 1536  # Mock 1536-dimensional vector
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        # Return a default embedding rather than raising an exception
        return [0.0] * 1536


def pinecone_content_retrieval(query: str, top_k: int = 5, content_type: str = None) -> List[Dict[str, Any]]:
    """
    Retrieve relevant educational content from Pinecone based on the query and optional content type.
    
    Args:
        query: Student question or topic to search for
        top_k: Number of results to return
        content_type: Optional filter for content type (e.g., "syllabus", "lecture", "textbook")
        
    Returns:
        List of content chunks with text and metadata
    """
    try:
        # Initialize Pinecone
        index = initialize_pinecone()
        if not index:
            logger.error("Failed to initialize Pinecone index")
            return []
        
        # In a real implementation, we would generate embeddings for the query
        # and search with proper filters based on content_type
        
        # Query our mock index
        # In production: We'd use the actual Pinecone query with filters
        query_results = index["query"](top_k=top_k)
        
        # Format results
        formatted_results = []
        for match in query_results["matches"]:
            # In this mock implementation, we'll simulate different content types
            metadata = match.get("metadata", {})
            
            # Skip if content_type filter is specified and doesn't match
            if content_type and metadata.get("content_type", "") != content_type:
                continue
                
            # Create a more realistic mock response based on query and content type
            if content_type == "syllabus" or metadata.get("content_type") == "syllabus":
                custom_text = f"Syllabus information about {query}: The course covers this topic in week {3 + (hash(query) % 10)}. Students will learn the fundamental concepts and practical applications."
                source = "Course Syllabus"
                content_type_value = "syllabus"
            elif content_type == "lecture" or metadata.get("content_type") == "lecture":
                custom_text = f"Lecture notes about {query}: This concept is explained through examples and case studies. Key points include theoretical foundations and implementation strategies."
                source = "Lecture Materials"
                content_type_value = "lecture"
            else:
                # Default to textbook content
                custom_text = f"Information about {query}: {metadata.get('text', 'This topic explores the relationship between theory and practice, with emphasis on real-world applications.')}"
                source = metadata.get("source", "Course Textbook")
                content_type_value = metadata.get("content_type", "textbook")
            
            formatted_results.append({
                "text": custom_text,
                "score": match.get("score", 0),
                "metadata": {
                    "source": source,
                    "page": metadata.get("page", str(10 + (hash(query) % 90))),
                    "summary": metadata.get("summary", f"Overview of {query} concepts and applications"),
                    "keywords": metadata.get("keywords", f"{query}, fundamentals, applications"),
                    "categories": metadata.get("categories", "core concepts"),
                    "content_type": content_type_value
                }
            })
        
        logger.info(f"Retrieved {len(formatted_results)} content matches for query: {query[:50]}...")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error retrieving content from Pinecone: {e}")
        return []


def get_document_names(content_type: str = None) -> List[str]:
    """
    Retrieve a list of unique document names from Pinecone metadata.
    
    Args:
        content_type: Optional filter for content type (e.g., "syllabus", "lecture", "textbook")
        
    Returns:
        List of unique document names
    """
    try:
        # Initialize Pinecone
        index = initialize_pinecone()
        if not index:
            logger.error("Failed to initialize Pinecone index")
            return []
        
        # In a real implementation, we would use a metadata query to get unique document names
        # For example: results = index.query(vector=[0]*1536, top_k=100, include_metadata=True)
        # Then extract unique document names from metadata
        
        # Mock implementation for testing
        if content_type == "syllabus":
            return [
                "CS101_Introduction_to_Computer_Science_Syllabus.pdf",
                "MATH250_Linear_Algebra_Syllabus.pdf",
                "PHYS201_Mechanics_Syllabus.pdf",
                "ENG301_Technical_Writing_Syllabus.pdf",
                "BUS220_Business_Ethics_Syllabus.pdf"
            ]
        elif content_type == "lecture":
            return [
                "CS101_Lecture1_Introduction.pdf",
                "CS101_Lecture2_Programming_Basics.pdf",
                "MATH250_Lecture1_Vectors.pdf",
                "PHYS201_Lecture3_Forces.pdf"
            ]
        elif content_type == "textbook":
            return [
                "Introduction_to_Programming_TextBook.pdf",
                "Linear_Algebra_and_Its_Applications.pdf",
                "Physics_for_Scientists_and_Engineers.pdf"
            ]
        else:
            # Return all document types
            return [
                "CS101_Introduction_to_Computer_Science_Syllabus.pdf",
                "MATH250_Linear_Algebra_Syllabus.pdf",
                "PHYS201_Mechanics_Syllabus.pdf",
                "ENG301_Technical_Writing_Syllabus.pdf",
                "BUS220_Business_Ethics_Syllabus.pdf",
                "CS101_Lecture1_Introduction.pdf",
                "CS101_Lecture2_Programming_Basics.pdf",
                "MATH250_Lecture1_Vectors.pdf",
                "PHYS201_Lecture3_Forces.pdf",
                "Introduction_to_Programming_TextBook.pdf",
                "Linear_Algebra_and_Its_Applications.pdf",
                "Physics_for_Scientists_and_Engineers.pdf"
            ]
            
        logger.info(f"Retrieved document names from Pinecone with filter: {content_type}")
        
    except Exception as e:
        logger.error(f"Error retrieving document names from Pinecone: {e}")
        return []


def get_syllabus_topics() -> List[Dict[str, Any]]:
    """
    Retrieve list of topics from course syllabi in the vector database.
    
    Returns:
        List of topics with metadata from syllabi
    """
    try:
        # Get list of syllabus documents from Pinecone
        syllabus_documents = get_document_names(content_type="syllabus")
        
        # In a real implementation, we would:
        # 1. Query each syllabus document for its topics section
        # 2. Extract topics and their descriptions
        # 3. Return structured data with source attribution to specific syllabi
        
        # For now, we'll create a mock response that simulates data from real syllabi
        syllabus_topics = []
        
        # CS101 topics
        if "CS101_Introduction_to_Computer_Science_Syllabus.pdf" in syllabus_documents:
            syllabus_topics.extend([
                {
                    "topic": "Introduction to Programming Concepts",
                    "description": "Basic programming concepts, syntax, and problem-solving approaches",
                    "source": "CS101_Introduction_to_Computer_Science_Syllabus.pdf",
                    "week": "Week 1-2",
                    "content_type": "syllabus",
                    "course": "CS101"
                },
                {
                    "topic": "Data Structures and Algorithms",
                    "description": "Fundamental data structures and basic algorithms for problem solving",
                    "source": "CS101_Introduction_to_Computer_Science_Syllabus.pdf",
                    "week": "Week 3-5",
                    "content_type": "syllabus",
                    "course": "CS101"
                },
                {
                    "topic": "Object-Oriented Programming",
                    "description": "Principles of OOP including classes, objects, inheritance, and polymorphism",
                    "source": "CS101_Introduction_to_Computer_Science_Syllabus.pdf",
                    "week": "Week 6-8",
                    "content_type": "syllabus",
                    "course": "CS101"
                }
            ])
        
        # MATH250 topics
        if "MATH250_Linear_Algebra_Syllabus.pdf" in syllabus_documents:
            syllabus_topics.extend([
                {
                    "topic": "Vector Spaces",
                    "description": "Definitions and properties of vector spaces with applications",
                    "source": "MATH250_Linear_Algebra_Syllabus.pdf",
                    "week": "Week 1-3",
                    "content_type": "syllabus",
                    "course": "MATH250"
                },
                {
                    "topic": "Linear Transformations",
                    "description": "Theory and applications of linear transformations between vector spaces",
                    "source": "MATH250_Linear_Algebra_Syllabus.pdf",
                    "week": "Week 4-6",
                    "content_type": "syllabus",
                    "course": "MATH250"
                },
                {
                    "topic": "Eigenvalues and Eigenvectors",
                    "description": "Calculation and application of eigenvalues and eigenvectors",
                    "source": "MATH250_Linear_Algebra_Syllabus.pdf",
                    "week": "Week 7-9",
                    "content_type": "syllabus",
                    "course": "MATH250"
                }
            ])
        
        # Add more syllabi topics as needed
        # This would come from actual Pinecone entries in a real implementation
        
        logger.info(f"Retrieved {len(syllabus_topics)} topics from course syllabi")
        return syllabus_topics
        
    except Exception as e:
        logger.error(f"Error retrieving syllabus topics: {e}")
        return []


def get_syllabus_document_content(syllabus_name: str) -> Dict[str, Any]:
    """
    Retrieve the full content of a specific syllabus document.
    
    Args:
        syllabus_name: Name of the syllabus document to retrieve
        
    Returns:
        Dictionary containing the document content and metadata
    """
    try:
        # In a real implementation, we would query Pinecone for the specific document
        # and return its full content
        
        # Mock implementation for testing
        if "CS101" in syllabus_name:
            return {
                "title": "Introduction to Computer Science",
                "course_code": "CS101",
                "instructor": "Dr. Jane Smith",
                "semester": "Fall 2023",
                "topics": [
                    {
                        "name": "Introduction to Programming Concepts",
                        "description": "Basic programming concepts, syntax, and problem-solving approaches",
                        "weeks": "1-2",
                        "readings": ["Introduction_to_Programming_TextBook.pdf, Ch. 1-2"]
                    },
                    {
                        "name": "Data Structures and Algorithms",
                        "description": "Fundamental data structures and basic algorithms for problem solving",
                        "weeks": "3-5",
                        "readings": ["Introduction_to_Programming_TextBook.pdf, Ch. 3-4"]
                    },
                    {
                        "name": "Object-Oriented Programming",
                        "description": "Principles of OOP including classes, objects, inheritance, and polymorphism",
                        "weeks": "6-8",
                        "readings": ["Introduction_to_Programming_TextBook.pdf, Ch. 5-7"]
                    }
                ],
                "text": "This course introduces students to the fundamentals of computer science and programming...",
                "source": syllabus_name,
                "content_type": "syllabus"
            }
        elif "MATH250" in syllabus_name:
            return {
                "title": "Linear Algebra",
                "course_code": "MATH250",
                "instructor": "Dr. Robert Johnson",
                "semester": "Spring 2024",
                "topics": [
                    {
                        "name": "Vector Spaces",
                        "description": "Definitions and properties of vector spaces with applications",
                        "weeks": "1-3",
                        "readings": ["Linear_Algebra_and_Its_Applications.pdf, Ch. 1-2"]
                    },
                    {
                        "name": "Linear Transformations",
                        "description": "Theory and applications of linear transformations between vector spaces",
                        "weeks": "4-6",
                        "readings": ["Linear_Algebra_and_Its_Applications.pdf, Ch. 3-4"]
                    },
                    {
                        "name": "Eigenvalues and Eigenvectors",
                        "description": "Calculation and application of eigenvalues and eigenvectors",
                        "weeks": "7-9",
                        "readings": ["Linear_Algebra_and_Its_Applications.pdf, Ch. 5-6"]
                    }
                ],
                "text": "This course provides a comprehensive introduction to linear algebra concepts...",
                "source": syllabus_name,
                "content_type": "syllabus"
            }
        else:
            return {
                "title": "Unknown Course",
                "course_code": "Unknown",
                "text": "Syllabus content not found",
                "source": syllabus_name,
                "content_type": "syllabus"
            }
            
    except Exception as e:
        logger.error(f"Error retrieving syllabus document: {e}")
        return {
            "error": str(e),
            "source": syllabus_name,
            "content_type": "syllabus"
        }


def get_topic_content(topic: str) -> List[Dict[str, Any]]:
    """
    Retrieve detailed content about a specific topic from the vector database.
    
    Args:
        topic: Specific topic to search for
        
    Returns:
        List of content chunks related to the topic
    """
    try:
        # Reuse the pinecone_content_retrieval function with a higher result count
        # to get comprehensive information about the topic
        results = pinecone_content_retrieval(topic, top_k=10)
        
        # In a real implementation, we would further process these results
        # to extract the most relevant information
        
        logger.info(f"Retrieved {len(results)} content items about topic: {topic}")
        return results
        
    except Exception as e:
        logger.error(f"Error retrieving topic content: {e}")
        return []


def analyze_content_relevance(query: str, content_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze the relevance of retrieved content to the student's query.
    
    Args:
        query: Original student query
        content_results: Retrieved content chunks from Pinecone
        
    Returns:
        Filtered and ranked content with relevance scores
    """
    try:
        # If no results, return empty list
        if not content_results:
            return []
        
        # For now, just return the sorted results based on score
        # This can be enhanced with more sophisticated relevance analysis
        sorted_results = sorted(content_results, key=lambda x: x.get("score", 0), reverse=True)
        
        return sorted_results
        
    except Exception as e:
        logger.error(f"Error analyzing content relevance: {e}")
        return content_results


def get_supplemental_materials(categories: List[str]) -> List[Dict[str, Any]]:
    """
    Get supplemental learning materials based on categories.
    
    Args:
        categories: List of subject categories or topics
        
    Returns:
        List of supplemental materials metadata
    """
    # This is a placeholder function that could be expanded to retrieve actual supplemental materials
    # For now, it returns mock data
    supplemental_materials = [
        {
            "type": "PDF",
            "title": "Course Syllabus",
            "description": "Complete course syllabus with schedule and assignments",
            "location": "Course Home > Syllabus"
        },
        {
            "type": "Rubric",
            "title": "Assignment Evaluation Criteria",
            "description": "Detailed grading rubric for course assignments",
            "location": "Assignments > Resources"
        },
        {
            "type": "Study Guide",
            "title": "Exam Study Guide",
            "description": "Comprehensive study guide for upcoming exams",
            "location": "Course Home > Resources > Study Guides"
        }
    ]
    
    # Filter by categories (in a real implementation)
    # For now, return all materials
    return supplemental_materials


def generate_probing_questions(topic: str, difficulty_level: str = "intermediate") -> List[str]:
    """
    Generate probing questions for a specific topic to encourage deeper thinking.
    
    Args:
        topic: The subject topic to generate questions about
        difficulty_level: Level of question difficulty (beginner, intermediate, advanced)
        
    Returns:
        List of probing questions
    """
    # This is a placeholder function that could be integrated with LLM generation
    # For now, it returns generic questions
    
    beginner_questions = [
        f"What is your current understanding of {topic}?",
        f"Can you explain the basic concept of {topic} in your own words?",
        f"What examples of {topic} have you encountered in your coursework?",
        f"How would you describe {topic} to someone who's never heard of it before?"
    ]
    
    intermediate_questions = [
        f"How does {topic} relate to other concepts you've learned in this course?",
        f"What are some practical applications of {topic} in real-world scenarios?",
        f"What challenges or difficulties have you encountered when working with {topic}?",
        f"How might {topic} be approached differently in various contexts?"
    ]
    
    advanced_questions = [
        f"How would you evaluate different approaches to {topic}?",
        f"What are the theoretical foundations underlying {topic}?",
        f"How might {topic} evolve or change in the future?",
        f"What critiques or limitations exist regarding current understanding of {topic}?"
    ]
    
    if difficulty_level == "beginner":
        return beginner_questions
    elif difficulty_level == "advanced":
        return advanced_questions
    else:  # intermediate is default
        return intermediate_questions