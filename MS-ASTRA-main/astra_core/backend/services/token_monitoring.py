"""
Token Monitoring Service for ASTRA Core

This service tracks token usage and costs for all OpenAI API calls and stores
the data in Cosmos DB for analytics and cost management.

Features:
- Real-time token tracking for input/output tokens
- Cost calculation based on model pricing
- Per-user, per-session, and per-agent tracking
- Historical analytics and reporting
- Budget alerts and usage limits

Usage:
    from backend.services.token_monitoring import token_monitor, track_tokens
    
    # Track tokens for an API call
    await token_monitor.track_usage(
        user_id="user@example.com",
        thread_id="conversation-123",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=200,
        agent_name="domain_agent"
    )
    
    # Get usage statistics
    stats = await token_monitor.get_user_usage("user@example.com")
"""

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import uuid
from backend.config import cosmosdb_endpoint, cosmosdb_credential, database_name
from backend.utils import logger

# Model pricing per 1M tokens (update these based on current Azure OpenAI pricing)
MODEL_PRICING = {
    "gpt-4o": {
        "input": 2.50,   # $2.50 per 1M input tokens
        "output": 10.00  # $10.00 per 1M output tokens
    },
    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60
    },
    "gpt-4-turbo": {
        "input": 10.00,
        "output": 30.00
    },
    "gpt-4": {
        "input": 30.00,
        "output": 60.00
    },
    "gpt-35-turbo": {
        "input": 0.50,
        "output": 1.50
    },
    "text-embedding-ada-002": {
        "input": 0.10,
        "output": 0.00
    },
    "text-embedding-3-small": {
        "input": 0.02,
        "output": 0.00
    },
    "text-embedding-3-large": {
        "input": 0.13,
        "output": 0.00
    }
}

class TokenUsageRecord(BaseModel):
    """Model for a single token usage record."""
    id: str
    user_id: str
    thread_id: str
    timestamp: datetime
    model: str
    agent_name: Optional[str] = None
    operation_type: str  # "chat", "embedding", "tool_call", etc.
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    request_metadata: Optional[Dict[str, Any]] = None


class TokenUsageStats(BaseModel):
    """Aggregated token usage statistics."""
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost: float
    cost_by_model: Dict[str, float]
    tokens_by_model: Dict[str, int]
    requests_by_agent: Dict[str, int]
    cost_trend: List[Dict[str, Any]]  # Daily cost breakdown


class TokenMonitoringService:
    """Service for tracking and analyzing token usage."""
    
    def __init__(self):
        """Initialize the token monitoring service."""
        self.client: Optional[CosmosClient] = None
        self.db = None
        self.container = None
        self.container_name = "token_usage"
        self._initialized = False
        
    async def initialize(self):
        """Initialize Cosmos DB connection and ensure container exists."""
        if self._initialized:
            return
            
        try:
            self.client = CosmosClient(url=cosmosdb_endpoint, credential=cosmosdb_credential)
            self.db = self.client.get_database_client(database_name)
            
            # Create token usage container if it doesn't exist
            await self.db.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path="/user_id")
            )
            
            self.container = self.db.get_container_client(self.container_name)
            self._initialized = True
            logger.info("Token monitoring service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing token monitoring service: {e}")
            raise
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> tuple[float, float, float]:
        """
        Calculate the cost for a given number of tokens.
        
        Args:
            model: Model name (e.g., "gpt-4o")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Tuple of (input_cost, output_cost, total_cost)
        """
        # Get pricing for the model, default to gpt-4o if not found
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o"])
        
        # Calculate costs (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        return input_cost, output_cost, total_cost
    
    async def track_usage(
        self,
        user_id: str,
        thread_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        agent_name: Optional[str] = None,
        operation_type: str = "chat",
        request_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Track token usage for a single API call.
        
        Args:
            user_id: User identifier
            thread_id: Conversation thread ID
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            agent_name: Name of the agent that made the call
            operation_type: Type of operation (chat, embedding, etc.)
            request_metadata: Additional metadata about the request
            
        Returns:
            Record ID
        """
        await self.initialize()
        
        try:
            # Calculate costs
            input_cost, output_cost, total_cost = self.calculate_cost(
                model, input_tokens, output_tokens
            )
            
            # Create usage record
            record_id = str(uuid.uuid4())
            record = {
                "id": record_id,
                "user_id": user_id,
                "thread_id": thread_id,
                "timestamp": datetime.utcnow().isoformat(),
                "model": model,
                "agent_name": agent_name,
                "operation_type": operation_type,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "input_cost": round(input_cost, 6),
                "output_cost": round(output_cost, 6),
                "total_cost": round(total_cost, 6),
                "request_metadata": request_metadata or {}
            }
            
            # Save to Cosmos DB
            await self.container.create_item(body=record)
            
            logger.info(
                f"Tracked token usage: user={user_id}, tokens={input_tokens + output_tokens}, "
                f"cost=${total_cost:.6f}, model={model}"
            )
            
            return record_id
            
        except Exception as e:
            logger.error(f"Error tracking token usage: {e}")
            # Don't raise - we don't want monitoring to break the application
            return ""
    
    async def get_user_usage(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> TokenUsageStats:
        """
        Get aggregated token usage statistics for a user.
        
        Args:
            user_id: User identifier
            start_date: Start date for the query (default: 30 days ago)
            end_date: End date for the query (default: now)
            
        Returns:
            TokenUsageStats with aggregated statistics
        """
        await self.initialize()
        
        try:
            # Default to last 30 days
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Query all records for the user in the date range
            query = """
                SELECT * FROM c 
                WHERE c.user_id = @user_id 
                AND c.timestamp >= @start_date 
                AND c.timestamp <= @end_date
                ORDER BY c.timestamp DESC
            """
            
            parameters = [
                {"name": "@user_id", "value": user_id},
                {"name": "@start_date", "value": start_date.isoformat()},
                {"name": "@end_date", "value": end_date.isoformat()}
            ]
            
            records = []
            async for item in self.container.query_items(
                query=query,
                parameters=parameters
            ):
                records.append(item)
            
            # Aggregate statistics
            stats = self._aggregate_stats(records)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user usage: {e}")
            # Return empty stats on error
            return TokenUsageStats(
                total_requests=0,
                total_input_tokens=0,
                total_output_tokens=0,
                total_tokens=0,
                total_cost=0.0,
                cost_by_model={},
                tokens_by_model={},
                requests_by_agent={},
                cost_trend=[]
            )
    
    async def get_thread_usage(self, thread_id: str) -> TokenUsageStats:
        """
        Get aggregated token usage statistics for a conversation thread.
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            TokenUsageStats with aggregated statistics
        """
        await self.initialize()
        
        try:
            query = """
                SELECT * FROM c 
                WHERE c.thread_id = @thread_id
                ORDER BY c.timestamp DESC
            """
            
            parameters = [{"name": "@thread_id", "value": thread_id}]
            
            records = []
            async for item in self.container.query_items(
                query=query,
                parameters=parameters
            ):
                records.append(item)
            
            return self._aggregate_stats(records)
            
        except Exception as e:
            logger.error(f"Error getting thread usage: {e}")
            return TokenUsageStats(
                total_requests=0,
                total_input_tokens=0,
                total_output_tokens=0,
                total_tokens=0,
                total_cost=0.0,
                cost_by_model={},
                tokens_by_model={},
                requests_by_agent={},
                cost_trend=[]
            )
    
    async def get_all_usage(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get raw token usage records for all users.
        
        Args:
            start_date: Start date for the query
            end_date: End date for the query
            limit: Maximum number of records to return
            
        Returns:
            List of token usage records
        """
        await self.initialize()
        
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()
            
            query = f"""
                SELECT * FROM c 
                WHERE c.timestamp >= @start_date 
                AND c.timestamp <= @end_date
                ORDER BY c.timestamp DESC
                OFFSET 0 LIMIT {limit}
            """
            
            parameters = [
                {"name": "@start_date", "value": start_date.isoformat()},
                {"name": "@end_date", "value": end_date.isoformat()}
            ]
            
            records = []
            async for item in self.container.query_items(
                query=query,
                parameters=parameters
            ):
                records.append(item)
            
            return records
            
        except Exception as e:
            logger.error(f"Error getting all usage: {e}")
            return []
    
    async def get_usage_by_model(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, TokenUsageStats]:
        """
        Get usage statistics broken down by model.
        
        Args:
            start_date: Start date for the query
            end_date: End date for the query
            
        Returns:
            Dictionary mapping model names to their usage stats
        """
        await self.initialize()
        
        try:
            records = await self.get_all_usage(start_date, end_date, limit=10000)
            
            # Group records by model
            records_by_model = {}
            for record in records:
                model = record.get("model", "unknown")
                if model not in records_by_model:
                    records_by_model[model] = []
                records_by_model[model].append(record)
            
            # Aggregate stats for each model
            stats_by_model = {}
            for model, model_records in records_by_model.items():
                stats_by_model[model] = self._aggregate_stats(model_records)
            
            return stats_by_model
            
        except Exception as e:
            logger.error(f"Error getting usage by model: {e}")
            return {}
    
    def _aggregate_stats(self, records: List[Dict[str, Any]]) -> TokenUsageStats:
        """
        Aggregate token usage records into statistics.
        
        Args:
            records: List of token usage records
            
        Returns:
            TokenUsageStats with aggregated data
        """
        if not records:
            return TokenUsageStats(
                total_requests=0,
                total_input_tokens=0,
                total_output_tokens=0,
                total_tokens=0,
                total_cost=0.0,
                cost_by_model={},
                tokens_by_model={},
                requests_by_agent={},
                cost_trend=[]
            )
        
        total_input_tokens = sum(r.get("input_tokens", 0) for r in records)
        total_output_tokens = sum(r.get("output_tokens", 0) for r in records)
        total_cost = sum(r.get("total_cost", 0.0) for r in records)
        
        # Group by model
        cost_by_model = {}
        tokens_by_model = {}
        for record in records:
            model = record.get("model", "unknown")
            cost_by_model[model] = cost_by_model.get(model, 0.0) + record.get("total_cost", 0.0)
            tokens_by_model[model] = tokens_by_model.get(model, 0) + record.get("total_tokens", 0)
        
        # Group by agent
        requests_by_agent = {}
        for record in records:
            agent = record.get("agent_name", "unknown")
            requests_by_agent[agent] = requests_by_agent.get(agent, 0) + 1
        
        # Calculate daily cost trend
        cost_by_date = {}
        for record in records:
            timestamp = record.get("timestamp", "")
            if timestamp:
                date = timestamp.split("T")[0]  # Get just the date part
                cost_by_date[date] = cost_by_date.get(date, 0.0) + record.get("total_cost", 0.0)
        
        cost_trend = [
            {"date": date, "cost": round(cost, 6)}
            for date, cost in sorted(cost_by_date.items())
        ]
        
        return TokenUsageStats(
            total_requests=len(records),
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_tokens=total_input_tokens + total_output_tokens,
            total_cost=round(total_cost, 6),
            cost_by_model={k: round(v, 6) for k, v in cost_by_model.items()},
            tokens_by_model=tokens_by_model,
            requests_by_agent=requests_by_agent,
            cost_trend=cost_trend
        )
    
    async def close(self):
        """Close the Cosmos DB client."""
        if self.client:
            await self.client.close()


# Global token monitoring service instance
token_monitor = TokenMonitoringService()


# Decorator for tracking token usage in functions
def track_tokens(operation_type: str = "chat", agent_name: Optional[str] = None):
    """
    Decorator to automatically track token usage for functions that call OpenAI.
    
    Usage:
        @track_tokens(operation_type="chat", agent_name="domain_agent")
        async def my_agent_function(user_id, thread_id, messages):
            result = await chat_model.ainvoke(messages)
            return result
    
    Note: The decorated function must return an object with usage_metadata or
    response_metadata containing token counts.
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Extract token usage from result
            if hasattr(result, "usage_metadata"):
                usage = result.usage_metadata
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                
                # Try to extract user_id and thread_id from kwargs or args
                user_id = kwargs.get("user_id", "unknown")
                thread_id = kwargs.get("thread_id", "unknown")
                model = kwargs.get("model", "gpt-4o")
                
                # Track the usage
                await token_monitor.track_usage(
                    user_id=user_id,
                    thread_id=thread_id,
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    agent_name=agent_name,
                    operation_type=operation_type
                )
            
            return result
        
        def sync_wrapper(*args, **kwargs):
            import asyncio
            result = func(*args, **kwargs)
            
            # Similar logic for sync functions
            if hasattr(result, "usage_metadata"):
                usage = result.usage_metadata
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                
                user_id = kwargs.get("user_id", "unknown")
                thread_id = kwargs.get("thread_id", "unknown")
                model = kwargs.get("model", "gpt-4o")
                
                # Track asynchronously
                asyncio.create_task(
                    token_monitor.track_usage(
                        user_id=user_id,
                        thread_id=thread_id,
                        model=model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        agent_name=agent_name,
                        operation_type=operation_type
                    )
                )
            
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator



