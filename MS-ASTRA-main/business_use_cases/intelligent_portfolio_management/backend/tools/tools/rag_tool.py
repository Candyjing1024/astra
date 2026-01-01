"""
This module provides Retrieval-Augmented Generation (RAG) functionality by 
integrating with Azure AI Search to retrieve relevant information from 
knowledge bases and indexed documents.

Key Features:
    1. HQ Glossary Search: Searches through Hydro-Quebec's glossary database
       to find definitions, abbreviations, and contextual information.
    2. IT Support Search: Retrieves knowledge base articles and IT support
       documentation from ServiceNow integration.
    3. Vector and Semantic Search: Utilizes both vector embeddings and 
       semantic search capabilities for enhanced relevance.
    4. Configurable Search Parameters: Supports customizable search parameters
       including k-nearest neighbors, field selection, and scoring profiles.

The module connects to Azure AI Search indices and performs hybrid searches
combining traditional text search with vector similarity and semantic ranking
to provide the most relevant results for user queries.

Functions:
- search_retrieval(user_input: str) -> list:
    Searches the HQ Glossary index and returns formatted search results
    including definitions, titles, abbreviations, context, and metadata.
    
- it_support_search_retrieval(user_input: str) -> list:
    Searches the IT Support knowledge base and returns structured results
    including descriptions, responses, context, and workflow information.

Both functions return lists of dictionaries containing the search results
with scoring information and search metadata for further processing by
the agentic framework.
"""
from backend.config import (
    search_endpoint, hq_glossary_index_name, search_credential, 
    hq_glossary_search_nearest_neighbour, hq_glossary_search_field_name, 
    hq_glossary_semantic_configuration_name, it_support_index_name,
    astra_roadmap_index_name, astra_roadmap_semantic_configuration_name,
    astra_roadmap_search_nearest_neighbour, astra_roadmap_search_field_name
)
from backend.utils import logger
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.search.documents.models import (
    QueryType,
    QueryCaptionType,
    QueryAnswerType
)

def search_retrieval(user_input: str) -> list:
    """
    Search and retrieve answers from Azure AI Search.
    Returns:
        list of dictionaries containing search results
    """

    logger.info(f"Search and retrieve answers from Azure AI Search.")
    query = user_input
    search_results = []  # Initialize an empty list to store dictionaries
    logger.info(f"Starting to establishing Connection with Search Index...")

    search_client = SearchClient(endpoint=search_endpoint, 
                                 index_name=hq_glossary_index_name, 
                                 credential=search_credential)
    vector_query = VectorizableTextQuery(text=query,
                                         k_nearest_neighbors=hq_glossary_search_nearest_neighbour,
                                         fields=hq_glossary_search_field_name, exhaustive=True)
    logger.info(f"Successfully established Connection with Search Index...")
    logger.info(f"Executing query...")


    r = search_client.search(  
                                search_text=query,
                                vector_queries=[vector_query],
                                select=["chunk", "title", "abbreviation", "context", "incorrectTerms","domain", "englishResponse", "sources", "synonym", "uuid"],   
                                query_type=QueryType.SEMANTIC,
                                semantic_configuration_name=hq_glossary_semantic_configuration_name, # default
                                query_caption=QueryCaptionType.EXTRACTIVE,
                                query_answer=QueryAnswerType.EXTRACTIVE,
                                scoring_profile="my-scoring-profile", # default
                                # scoring_parameters=["tags-VPOM, MAIS"],
                                top=3
                            )
    logger.info(f"Query Executed Successfully...")
    logger.info(f"Building Dictionary for Search results...")
    
    for result in r:
        # Convert the result to a dictionary and append it to the list
        result_dict = {
            "definition": result.get('chunk', ''),
            "title": result.get('title', ''),
            "abbreviation": result.get('abbreviation', ''),
            "context": result.get('title', ''),
            "domain": result.get('domain', ''),
            "sources": result.get('sources', ''),
            "synonym": result.get('synonym', ''),
            "uuid": result.get('uuid', ''),
            "@search.score": result.get('@search.score', 0),
            "@search.reranker_score": result.get('@search.reranker_score', 0),
            "@search.highlights": result.get('@search.highlights', None),
            "@search.captions": result.get('@search.captions', None),
            "@search.document_debug_info": result.get('@search.document_debug_info', None)
        }
        logger.info(f"Content: {result_dict} \n")
        search_results.append(result_dict)  # Append the dictionary to the list

    logger.info(f"Function Successfully completed...")

    return search_results

def it_support_search_retrieval(user_input: str) -> list:
    """
    Search and retrieve answers from Azure AI Search.
    Returns:
        list of dictionaries containing search results
    """

    logger.info(f"Search and retrieve answers from Azure AI Search.")
    query = user_input
    search_results_it = []  # Initialize an empty list to store dictionaries
    logger.info(f"Starting to establishing Connection with Search Index...")
    
    search_client = SearchClient(endpoint=search_endpoint, index_name=it_support_index_name, credential=search_credential)
    vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=5, fields="text_vector", exhaustive=True)
    logger.info(f"Successfully established Connection with Search Index...")

    logger.info(f"Executing query...")


    r = search_client.search(  
    search_text=query,
    vector_queries=[vector_query],
    select=["chunk", "short_description", "u_kb_reponse", "u_kb_contexte", "u_kb_tapes_de_r_alisation","kb_knowledge_base", "kb_category", "workflow_state", "active", "sys_id"],   
    query_type=QueryType.SEMANTIC,
    semantic_configuration_name='my-semantic-config', # default
    query_caption=QueryCaptionType.EXTRACTIVE,
    query_answer=QueryAnswerType.EXTRACTIVE,
    top=2
        )
    logger.info(f" Query Executed Successfully...")
    logger.info(f" Building Dictionary for Search results...")
    
    for result in r:
        # Convert the result to a dictionary and append it to the list
        result_dict = {
            "definition": result.get('chunk', ''),
            "short_description": result.get('short_description', ''),
            "u_kb_reponse": result.get('u_kb_reponse', ''),
            "u_kb_contexte": result.get('u_kb_contexte', ''),
            "u_kb_tapes_de_r_alisation": result.get('u_kb_tapes_de_r_alisation', ''),
            "kb_knowledge_base": result.get('kb_knowledge_base', ''),
            "kb_category": result.get('kb_category', ''),
            "workflow_state": result.get('workflow_state', ''),
            "active": result.get('active', ''),
            "sys_id": result.get('sys_id', ''),
            "@search.score": result.get('@search.score', 0),
            "@search.reranker_score": result.get('@search.reranker_score', 0),
            "@search.highlights": result.get('@search.highlights', None),
            "@search.captions": result.get('@search.captions', None),
            "@search.document_debug_info": result.get('@search.document_debug_info', None)
        }
        logger.info(f"Content: {result_dict} \n")
        search_results_it.append(result_dict)  # Append the dictionary to the list

    logger.info(f" Function Successfully completed...")

    return search_results_it


def astra_roadmap_search_retrieval(user_input: str, top_results: int = 3) -> list:
    """
    Search and retrieve answers from Microsoft ASTRA Roadmap PowerPoint index.
    
    This function searches through the Microsoft ASTRA Roadmap presentation content
    including slides about roadmap phases, components, timeline, and priorities.
    
    Args:
        user_input (str): The search query
        top_results (int): Number of results to return (default: 3)
    
    Returns:
        list of dictionaries containing search results with ASTRA roadmap content
    """

    logger.info(f"Search and retrieve answers from Microsoft ASTRA Roadmap PowerPoint index.")
    query = user_input
    search_results = []  # Initialize an empty list to store dictionaries
    logger.info(f"Starting to establish connection with ASTRA Roadmap search index...")

    try:
        search_client = SearchClient(endpoint=search_endpoint, 
                                   index_name=astra_roadmap_index_name, 
                                   credential=search_credential)
        
        logger.info(f"Successfully established connection with ASTRA Roadmap search index...")
        logger.info(f"Executing basic text search query...")

        # Use basic text search instead of vector/semantic search
        r = search_client.search(  
            search_text=query,
            select=[
                "chunk_id", "chunk", "title", "slide_number", "slide_title", 
                "section", "content_type", "roadmap_phase", "component", 
                "timeline", "priority", "technology", "source_file"
            ],
            top=top_results
        )
        
        logger.info(f"Query executed successfully...")
        logger.info(f"Building dictionary for ASTRA Roadmap search results...")
        
        for result in r:
            # Convert the result to a dictionary optimized for ASTRA Roadmap content
            # Handle chunk field which comes as a list
            chunk_content = result.get('chunk', '')
            if isinstance(chunk_content, list):
                chunk_content = ' '.join(str(item) for item in chunk_content if item)
            elif chunk_content is None:
                chunk_content = ''
            else:
                chunk_content = str(chunk_content)
                
            result_dict = {
                # Core content fields
                "content": chunk_content,  # Main content field (processed)
                "title": result.get('title', ''),
                "slide_title": result.get('slide_title', ''),
                "chunk_id": result.get('chunk_id', ''),
                
                # PowerPoint structure fields
                "slide_number": result.get('slide_number', 0),
                "section": result.get('section', ''),
                "content_type": result.get('content_type', ''),
                
                # ASTRA Roadmap specific fields
                "roadmap_phase": result.get('roadmap_phase', ''),
                "component": result.get('component', ''),
                "timeline": result.get('timeline', ''),
                "priority": result.get('priority', ''),
                "technology": result.get('technology', ''),
                "source_file": result.get('source_file', ''),
                
                # Search metadata
                "@search.score": result.get('@search.score', 0),
                "@search.reranker_score": result.get('@search.reranker_score', 0),
                "@search.highlights": result.get('@search.highlights', None),
                "@search.captions": result.get('@search.captions', None),
                "@search.document_debug_info": result.get('@search.document_debug_info', None)
            }
            logger.info(f"ASTRA Roadmap Content: {result_dict} \n")
            search_results.append(result_dict)  # Append the dictionary to the list

        logger.info(f"ASTRA Roadmap search function completed successfully...")
        return search_results

    except Exception as e:
        logger.error(f"Error in ASTRA Roadmap search retrieval: {str(e)}")
        return []
    