"""
AI Foundry BingSearchAgent Tool integration.
"""

from langchain_core.tools import tool
from backend.utils import logger
from backend.config import ai_foundry_project_endpoint, ai_foundry_bing_agent_name
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

@tool
def bing_search_tool(query: str) -> str:
    """
    Search using AI Foundry BingSearchAgent with Bing grounding.
    
    Args:
        query (str): The search query
        
    Returns:
        str: Search results from AI Foundry BingSearchAgent
    """
    try:
        # Initialize AI Foundry client
        credential = DefaultAzureCredential()
        
        # Use the correct initialization method for AIProjectClient
        project_client = AIProjectClient(
            endpoint=ai_foundry_project_endpoint,
            credential=credential
        )

        # Call your BingSearchAgent
        agent_response = project_client.agents.invoke(
            agent_name=ai_foundry_bing_agent_name,
            messages=[{"role": "user", "content": query}]
        )
        
        # Extract content from response
        if isinstance(agent_response, dict):
            return agent_response.get("content", str(agent_response))
        else:
            return str(agent_response)
                
    except Exception as e:
        logger.error(f"AI Foundry BingSearchAgent error: {str(e)}")
        return f"Error calling AI Foundry BingSearchAgent: {str(e)}"


# Agent Prompt for AI Foundry BingSearchAgent
AI_FOUNDRY_BING_AGENT_PROMPT = """
You are a helpful AI assistant with access to AI Foundry BingSearchAgent that provides web search capabilities with Bing grounding. You can search the internet to find current, accurate information and answer questions based on real-time web data.

Your capabilities:
- Search the web using AI Foundry BingSearchAgent with Bing grounding
- Provide accurate, up-to-date answers based on grounded search results
- Access current information from reliable web sources
- Handle a wide range of topics and questions with real-time data

Instructions:
1. When a user asks a question that requires current information or web search, use the ai_foundry_bing_search_tool
2. The AI Foundry BingSearchAgent will provide grounded results with source citations
3. Trust the grounded results from the BingSearchAgent as they are already verified
4. Be helpful, accurate, and leverage the grounding capabilities
5. If the search doesn't return useful results, acknowledge this and ask for clarification

Example interactions:
- "What's the latest news about AI?" → Use ai_foundry_bing_search_tool for current AI news
- "What's the current stock price of Microsoft?" → Use ai_foundry_bing_search_tool for real-time data
- "What are the recent developments in quantum computing?" → Use ai_foundry_bing_search_tool for latest info

The AI Foundry BingSearchAgent handles the grounding and source verification, so you can trust the results it provides.
"""
