"""
Generic RAG (Retrieval-Augmented Generation) Tool Template

This template provides generic search and retrieval functions for Azure AI Search.
Customize the functions below for your specific domain and knowledge base.

CUSTOMIZATION GUIDE:
1. Update index names in config.py for your domain
2. Modify search fields and metadata based on your document schema
3. Customize the search results formatting for your use case
4. Implement domain-specific search logic as needed

Authors: Microsoft ASTRA Team
License: MIT
"""

import logging
from typing import List, Dict, Any, Optional
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery, QueryType, QueryCaptionType, QueryAnswerType
from app.config import (
    search_endpoint,
    search_credential,
    domain_index_name,
    domain_semantic_configuration_name,
    domain_search_field_name,
    domain_search_nearest_neighbour
)

# Configure logging
logger = logging.getLogger(__name__)


def domain_search_retrieval(user_input: str, top_results: int = 3) -> List[Dict[str, Any]]:
    """
    Generic domain search and retrieval function.
    
    CUSTOMIZE THIS FUNCTION for your specific domain and knowledge base.
    This template shows the basic pattern for Azure AI Search integration.
    
    Args:
        user_input (str): The user's search query
        top_results (int): Number of results to return (default: 3)
        
    Returns:
        List[Dict[str, Any]]: List of search results with metadata
    """
    search_results = []
    logger.info(f"Starting domain search retrieval for query: {user_input}")
    
    try:
        # Initialize Azure AI Search client
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=domain_index_name,
            credential=search_credential
        )
        
        # CUSTOMIZE: Configure vector query based on your embedding field
        vector_query = VectorizableTextQuery(
            text=user_input,
            k_nearest_neighbors=domain_search_nearest_neighbour,
            fields=domain_search_field_name,
            exhaustive=True
        )
        
        logger.info(f"Executing search query...")
        
        # CUSTOMIZE: Modify select fields based on your document schema
        results = search_client.search(
            search_text=user_input,
            vector_queries=[vector_query],
            select=[
                "content",      # CUSTOMIZE: Main content field name
                "title",        # CUSTOMIZE: Document title field
                "category",     # CUSTOMIZE: Category/domain field
                "source",       # CUSTOMIZE: Source document field
                "metadata"      # CUSTOMIZE: Additional metadata fields
            ],
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name=domain_semantic_configuration_name,
            query_caption=QueryCaptionType.EXTRACTIVE,
            query_answer=QueryAnswerType.EXTRACTIVE,
            top=top_results
        )
        
        logger.info(f"Processing search results...")
        
        for result in results:
            # CUSTOMIZE: Format result data based on your needs
            result_dict = {
                # Core content fields - CUSTOMIZE field names
                "content": result.get('content', ''),
                "title": result.get('title', ''),
                "category": result.get('category', ''),
                "source": result.get('source', ''),
                "metadata": result.get('metadata', {}),
                
                # Search quality metrics
                "search_score": result.get('@search.score', 0),
                "reranker_score": result.get('@search.reranker_score', 0),
                "highlights": result.get('@search.highlights', None),
                "captions": result.get('@search.captions', None)
            }
            
            logger.info(f"Retrieved result: {result_dict['title']}")
            search_results.append(result_dict)
        
        logger.info(f"Domain search completed successfully. Retrieved {len(search_results)} results")
        return search_results
        
    except Exception as e:
        logger.error(f"Error in domain search retrieval: {str(e)}")
        return []


def secondary_search_retrieval(user_input: str, search_type: str = "general") -> List[Dict[str, Any]]:
    """
    Generic secondary search function for additional knowledge sources.
    
    CUSTOMIZE THIS FUNCTION if you have multiple knowledge bases or search indices.
    
    Args:
        user_input (str): The user's search query
        search_type (str): Type of search to perform ("general", "specific", etc.)
        
    Returns:
        List[Dict[str, Any]]: List of search results from secondary sources
    """
    search_results = []
    logger.info(f"Starting secondary search retrieval: {search_type}")
    
    try:
        # CUSTOMIZE: Implement secondary search logic here
        # Example: Different index, different search parameters, etc.
        
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=domain_index_name,  # CUSTOMIZE: Use different index if needed
            credential=search_credential
        )
        
        # Simple text search for secondary results
        results = search_client.search(
            search_text=user_input,
            select=["content", "title", "category", "source"],
            top=2  # Fewer results for secondary search
        )
        
        for result in results:
            result_dict = {
                "content": result.get('content', ''),
                "title": result.get('title', ''),
                "category": result.get('category', ''),
                "source": result.get('source', ''),
                "search_type": search_type,
                "search_score": result.get('@search.score', 0)
            }
            search_results.append(result_dict)
        
        logger.info(f"Secondary search completed. Retrieved {len(search_results)} results")
        return search_results
        
    except Exception as e:
        logger.error(f"Error in secondary search: {str(e)}")
        return []


def search_by_category(user_input: str, category: str, top_results: int = 2) -> List[Dict[str, Any]]:
    """
    Search within a specific category or domain.
    
    CUSTOMIZE THIS FUNCTION to implement category-specific search logic.
    
    Args:
        user_input (str): The user's search query
        category (str): Specific category to search within
        top_results (int): Number of results to return
        
    Returns:
        List[Dict[str, Any]]: Filtered search results for the category
    """
    search_results = []
    logger.info(f"Starting category search: {category}")
    
    try:
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=domain_index_name,
            credential=search_credential
        )
        
        # CUSTOMIZE: Add category filter to your search
        filter_expression = f"category eq '{category}'"  # CUSTOMIZE: Adjust filter field name
        
        results = search_client.search(
            search_text=user_input,
            filter=filter_expression,
            select=["content", "title", "category", "source"],
            top=top_results
        )
        
        for result in results:
            formatted_result = {
                "content": result.get('content', ''),
                "title": result.get('title', ''),
                "category": result.get('category', ''),
                "source": result.get('source', ''),
                "search_context": {
                    "category_filter": category,
                    "score": result["@search.score"],
                    "document_id": result.get("id", "")
                }
            }
            search_results.append(formatted_result)

        logger.info(f"Category search ({category}) retrieved {len(search_results)} results")
        return search_results

    except Exception as e:
        logger.error(f"Error in category search: {str(e)}")
        return []


# Export the main search function for agent use
# CUSTOMIZE: Update the function name to match your domain
__all__ = [
    "domain_search_retrieval",
    "secondary_search_retrieval", 
    "search_by_category"
]

# NOTE: Template file - all customer-specific functions have been removed
# To customize for your domain, implement specific search functions following
# the pattern of domain_search_retrieval() above