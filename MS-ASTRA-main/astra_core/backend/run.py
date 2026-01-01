"""
This module implements a FastAPI-based web server that serves the agentic framework
as a RESTful API with CopilotKit integration for enhanced AI assistant capabilities.

TEMPLATE FILE: This is a generic template for business use case API implementation.
Customize the agent imports and configurations for your specific domain.

Key Features:
    1. FastAPI Web Server: Provides REST endpoints for agent interactions
    2. CopilotKit Integration: Enables advanced AI assistant features and UI integration
    3. Conversation Management: Handles conversation persistence using Cosmos DB checkpointing
    4. CORS Support: Configured for cross-origin requests from web frontends
    5. Session Management: Maintains user sessions and conversation threads
    6. Database Operations: Provides endpoints for conversation history and analytics

Architecture:
The server implements a session-aware LangGraph agent system that:
- Routes user queries through the supervisor agent
- Maintains conversation state across interactions
- Provides real-time streaming responses
- Supports multiple concurrent user sessions

API Endpoints:
- /health: Health check endpoint
- /conversations: Manage conversation threads and history
- /database/summary: Retrieve database analytics and summaries
- CopilotKit endpoints: Integrated AI assistant capabilities

CUSTOMIZATION:
1. Import your domain-specific agents in place of placeholder agents
2. Update the agent compilation to use your supervisor agent
3. Customize the agent description and name for your use case
4. Modify the lifespan function to initialize your specific agents

Integration:
This module serves as the main entry point for the agentic framework,
providing a web-based interface for interacting with the multi-agent system
and integrating with external applications through standard REST APIs.
"""

from langchain_core.messages import AIMessage, ToolMessage
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# CUSTOMIZE: Import your domain-specific agents here
# Example imports - replace with your actual agents:
# from backend.agents.domain_supervisor import domain_supervisor
# from backend.agents.domain_agent import domain_agent
# from backend.agents.research_agent import research_agent

# PLACEHOLDER IMPORTS - REPLACE WITH YOUR DOMAIN AGENTS
try:
    from backend.agents.supervisor_agents import top_level_supervisor
except ImportError:
    # Fallback for template - you should implement your own supervisor
    top_level_supervisor = None

from pydantic import BaseModel
import uvicorn
import certifi
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitRemoteEndpoint
from typing import List, Dict, Any, Optional
from backend.utils import checkpointer, SessionAwareLangGraphAgent, logger

# Response Models
class ConversationResponse(BaseModel):
    thread_id: str
    user_id: str
    last_updated: str
    message_count: int
    first_message_preview: Optional[Dict[str, Any]] = None

class CreateConversationRequest(BaseModel):
    user_id: str
    title: Optional[str] = None    

class DatabaseSummaryResponse(BaseModel):
    total_conversations: int
    unique_users: List[str]
    unique_thread_ids: List[str]    

class QueryRequest(BaseModel):
    input: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan handler to set up CosmosDB persistence and CopilotKit integration."""
    # Validate checkpointer is initialized
    if checkpointer is None:
        logger.error("Checkpointer is not initialized")
        raise RuntimeError("Checkpointer not initialized")
    
    # Set up indexes
    await checkpointer.ensure_indexes()
    
    try:
        # CUSTOMIZE: Replace with your domain-specific supervisor agent
        if top_level_supervisor is not None:
            graph = top_level_supervisor.compile(checkpointer=checkpointer)
        else:
            logger.warning("No supervisor agent configured - implement your domain supervisor")
            raise RuntimeError("No supervisor agent configured")
    except Exception as e:
        logger.error(f"Failed to compile graph: {str(e)}")
        raise

    # Use dynamic agents to access CopilotKit properties
    def create_agents(context):
        """
        Dynamic agent factory that has access to CopilotKit properties.
        This is called by CopilotKit for each request and receives context including properties.
        
        CUSTOMIZE: Update the agent name and description for your use case
        """

        # Extract user_id from CopilotKit properties
        user_id = None
        if 'properties' in context and context['properties']:
            user_id = context['properties'].get('user_id')

        # Create agent with user_id in config
        agent_config = {}
        if user_id:
            agent_config = {
                'configurable': {
                    'user_id': user_id
                }
            }

        return [
            SessionAwareLangGraphAgent(
                checkpointer=checkpointer,
                # CUSTOMIZE: Update these for your specific use case
                name="domain_agent",  # Replace with your domain name (e.g., "portfolio_agent", "healthcare_agent")
                description="AI assistant for [YOUR_DOMAIN] with persistent conversation history and domain expertise",  # Update description
                graph=graph,
                langgraph_config=agent_config,
            )
        ]

    sdk = CopilotKitRemoteEndpoint(
        agents=create_agents
    )

    # Add the CopilotKit FastAPI endpoint
    add_fastapi_endpoint(app, sdk, "/copilotkit")

    yield

    # Cleanup on shutdown
    await checkpointer.close()

app_fastapi = FastAPI(lifespan=lifespan)

# Add CORS middleware to the FastAPI application
app_fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# USE USER-BASED THREAD ID for cross-session persistence
# thread_id = f"user_{user_identifier.replace('@', '_').replace('.', '_')}"
# thread_id = "test_user0721@hq.com"
# user_identifier = "test_user0721@hq.com"
# config_user = {"configurable": {"thread_id": thread_id, "user_id": user_identifier}}

 
# @app_fastapi.post("/chat")
# async def chat(request: QueryRequest):
#     logger.info(f"Received user input: {request.input}")

#     result = graph.invoke({
#         "messages": [{"role": "user", "content": request.input}]
#     })
 
#     messages = []
#     for m in result["messages"]:
#         if isinstance(m, AIMessage):
#             messages.append({"type": "ai", "content": m.content})
#             logger.info(f"AI response: {m.content}")
#         elif isinstance(m, ToolMessage):
#             messages.append({"type": "tool", "content": m.content})
#             logger.info(f"Tool response: {m.content}")
 
#     return {"messages": messages}
 
@app_fastapi.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}


@app_fastapi.get("/conversation-by-user/{user_id}", response_model=List[ConversationResponse])
async def get_user_conversations(user_id: str, limit: int = 50):
    """Get the single conversation for a specific user (new model: one conversation per user)."""
    try:
        conversations = await checkpointer.get_conversations_by_user(user_id, limit)

        # With the new model, there should be at most one conversation per user
        if len(conversations) > 1:
            # Clean up duplicates automatically
            await checkpointer.cleanup_old_conversations(user_id)
            logger.info(f"Cleaning up duplicate conversations for the user: {user_id}")
            # Fetch again after cleanup
            conversations = await checkpointer.get_conversations_by_user(user_id, limit)
            logger.info(f"Fetching conversation history for user: {user_id}")

        return [
            ConversationResponse(
                thread_id=conv["thread_id"],
                user_id=conv["user_id"],
                last_updated=conv["last_updated"].isoformat(),
                message_count=conv["message_count"],
                first_message_preview=conv.get("first_message_preview")
            )
            for conv in conversations
        ]
    except Exception as e:
        logger.error(f"Error retrieving conversations: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving conversations: {str(e)}")


@app_fastapi.post("/conversations", response_model=Dict[str, str])
async def create_conversation(request: CreateConversationRequest):
    """Get or create conversation for a user (new model: one conversation per user)."""
    try:
        # Get or create the user's single conversation
        logger.info("Creating new conversation")
        thread_id = await checkpointer.get_or_create_user_conversation(request.user_id)
        return {
            "thread_id": thread_id,
            "user_id": request.user_id,
            "message": "Conversation ready"
        }
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error creating conversation: {str(e)}")


@app_fastapi.delete("/conversations/{thread_id}")
async def delete_conversation_thread(thread_id: str):
    """Delete a conversation thread """
    try:
        # Find and delete the user's conversation (use "id" field, not "thread_id")
        # Note: In CosmosDB, we need to query the conversations container
        logger.info("deleting conversation")
        query = "SELECT * FROM c WHERE c.id = @thread_id"
        parameters = [{"name": "@thread_id", "value": thread_id}]
        items = [item async for item in checkpointer.conversations_container.query_items(
            query=query, parameters=parameters)]

        if not items:
            logger.error("Conversation not found")
            raise HTTPException(
                status_code=404, detail="Conversation not found")

        doc = items[0]
        deleted = await checkpointer.delete_conversation(doc["id"])
        if not deleted:
            logger.error("Conversation not found")
            raise HTTPException(
                status_code=404, detail="Conversation not found")
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting conversation: {str(e)}")


@app_fastapi.get("/session/{user_id}")
async def get_session_info(user_id: str):
    """Get session information for a user (new model: always returns the user's single conversation)."""
    try:
        logger.info(f"Fetching session information for user: {user_id}")
        # Get the user's conversation (no time threshold needed)
        thread_id = await checkpointer.get_or_create_user_conversation(user_id)

        return {
            "user_id": user_id,
            "has_recent_session": True,  # Always true since we maintain one conversation per user
            "thread_id": thread_id,
            "message": "User conversation ready"
        }
    except Exception as e:
        logger.error(f"Error checking session: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error checking session: {str(e)}")


@app_fastapi.get("/conversation-by-id/{thread_id}", response_model=ConversationResponse)
async def get_conversation_by_thread(thread_id: str):
    """Get conversation details by thread ID."""
    try:
        logger.info(f"Getting conversation with thread_id: {thread_id}")
        # Find conversation by thread_id (which is stored as "id" in the document)
        query = "SELECT * FROM c WHERE c.id = @thread_id"
        parameters = [{"name": "@thread_id", "value": thread_id}]
        items = [item async for item in checkpointer.conversations_container.query_items(
            query=query, parameters=parameters)]

        if not items:
            logger.error(f"Conversation with thread_id {thread_id} not found")
            raise HTTPException(
                status_code=404, detail="Conversation not found")

        doc = items[0]

        # Extract message count
        message_count = len(doc.get("messages", []))

        # Get first message preview
        first_message_preview = None
        messages = doc.get("messages", [])
        if messages:
            first_message = messages[0]
            content = first_message.get("content", "")
            preview_content = content[:100] + "..." if len(content) > 100 else content
            first_message_preview = {
                "role": messages[0].get("role", ""),
                "content": preview_content,
                "timestamp": first_message.get("timestamp", "")
            }

        return ConversationResponse(
            thread_id=doc["id"],
            user_id=doc["userId"],
            last_updated=doc["lastUpdated"],  # It's already in ISO format
            message_count=message_count,
            first_message_preview=first_message_preview
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving conversation: {str(e)}")


@app_fastapi.get("/database-summary", response_model=DatabaseSummaryResponse)
async def get_database_summary():
    """Get a summary of the database: total conversations, unique users, and unique thread IDs."""
    try:
        logger.info("Getting database summary")
        # Get the count of all conversations
        total_conversations = await checkpointer.get_total_conversations()

        # Get all unique user IDs and thread IDs
        unique_users = await checkpointer.get_all_unique_user_ids()
        unique_thread_ids = await checkpointer.get_all_unique_thread_ids()

        return DatabaseSummaryResponse(
            total_conversations=total_conversations,
            unique_users=unique_users,
            unique_thread_ids=unique_thread_ids
        )
    except Exception as e:
        logger.error(f"Error retrieving database summary: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving database summary: {str(e)}")


# Token Monitoring Endpoints
from backend.services.token_monitoring import token_monitor

class TokenUsageResponse(BaseModel):
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost: float
    cost_by_model: Dict[str, float]
    tokens_by_model: Dict[str, int]
    requests_by_agent: Dict[str, int]
    cost_trend: List[Dict[str, Any]]

class TokenUsageRecordResponse(BaseModel):
    id: str
    user_id: str
    thread_id: str
    timestamp: str
    model: str
    agent_name: Optional[str]
    operation_type: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    total_cost: float


@app_fastapi.get("/token-usage/user/{user_id}", response_model=TokenUsageResponse)
async def get_user_token_usage(
    user_id: str,
    days: int = 30
):
    """
    Get token usage statistics for a specific user.
    
    Args:
        user_id: User identifier
        days: Number of days to look back (default: 30)
    """
    try:
        logger.info(f"Getting token usage for user: {user_id}")
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        stats = await token_monitor.get_user_usage(user_id, start_date, end_date)
        
        return TokenUsageResponse(
            total_requests=stats.total_requests,
            total_input_tokens=stats.total_input_tokens,
            total_output_tokens=stats.total_output_tokens,
            total_tokens=stats.total_tokens,
            total_cost=stats.total_cost,
            cost_by_model=stats.cost_by_model,
            tokens_by_model=stats.tokens_by_model,
            requests_by_agent=stats.requests_by_agent,
            cost_trend=stats.cost_trend
        )
    except Exception as e:
        logger.error(f"Error retrieving user token usage: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving user token usage: {str(e)}"
        )


@app_fastapi.get("/token-usage/thread/{thread_id}", response_model=TokenUsageResponse)
async def get_thread_token_usage(thread_id: str):
    """
    Get token usage statistics for a specific conversation thread.
    
    Args:
        thread_id: Thread identifier
    """
    try:
        logger.info(f"Getting token usage for thread: {thread_id}")
        stats = await token_monitor.get_thread_usage(thread_id)
        
        return TokenUsageResponse(
            total_requests=stats.total_requests,
            total_input_tokens=stats.total_input_tokens,
            total_output_tokens=stats.total_output_tokens,
            total_tokens=stats.total_tokens,
            total_cost=stats.total_cost,
            cost_by_model=stats.cost_by_model,
            tokens_by_model=stats.tokens_by_model,
            requests_by_agent=stats.requests_by_agent,
            cost_trend=stats.cost_trend
        )
    except Exception as e:
        logger.error(f"Error retrieving thread token usage: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving thread token usage: {str(e)}"
        )


@app_fastapi.get("/token-usage/all", response_model=List[TokenUsageRecordResponse])
async def get_all_token_usage(
    days: int = 7,
    limit: int = 100
):
    """
    Get recent token usage records for all users.
    
    Args:
        days: Number of days to look back (default: 7)
        limit: Maximum number of records to return (default: 100)
    """
    try:
        logger.info("Getting all token usage records")
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        records = await token_monitor.get_all_usage(start_date, end_date, limit)
        
        return [
            TokenUsageRecordResponse(
                id=r["id"],
                user_id=r["user_id"],
                thread_id=r["thread_id"],
                timestamp=r["timestamp"],
                model=r["model"],
                agent_name=r.get("agent_name"),
                operation_type=r["operation_type"],
                input_tokens=r["input_tokens"],
                output_tokens=r["output_tokens"],
                total_tokens=r["total_tokens"],
                total_cost=r["total_cost"]
            )
            for r in records
        ]
    except Exception as e:
        logger.error(f"Error retrieving all token usage: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving all token usage: {str(e)}"
        )


@app_fastapi.get("/token-usage/by-model", response_model=Dict[str, TokenUsageResponse])
async def get_token_usage_by_model(days: int = 30):
    """
    Get token usage statistics broken down by model.
    
    Args:
        days: Number of days to look back (default: 30)
    """
    try:
        logger.info("Getting token usage by model")
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        stats_by_model = await token_monitor.get_usage_by_model(start_date, end_date)
        
        result = {}
        for model, stats in stats_by_model.items():
            result[model] = TokenUsageResponse(
                total_requests=stats.total_requests,
                total_input_tokens=stats.total_input_tokens,
                total_output_tokens=stats.total_output_tokens,
                total_tokens=stats.total_tokens,
                total_cost=stats.total_cost,
                cost_by_model=stats.cost_by_model,
                tokens_by_model=stats.tokens_by_model,
                requests_by_agent=stats.requests_by_agent,
                cost_trend=stats.cost_trend
            )
        
        return result
    except Exception as e:
        logger.error(f"Error retrieving token usage by model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving token usage by model: {str(e)}"
        )


def main():
    print("Starting FastAPI application...")
    os.environ["SSL_CERT_FILE"] = certifi.where()
    uvicorn.run("agentic_framework.run:app_fastapi", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    main()