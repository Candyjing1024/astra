"""
LangChain Callback Handler for Token Tracking

This module provides a callback handler that automatically tracks token usage
from LangChain/LangGraph agent calls and saves the data to Cosmos DB.

Usage:
    from backend.callbacks.token_tracking_callback import TokenTrackingCallbackHandler
    
    # Create callback with user/thread context
    callback = TokenTrackingCallbackHandler(
        user_id="user@example.com",
        thread_id="conversation-123",
        agent_name="domain_agent"
    )
    
    # Pass to agent invocation
    result = await agent.ainvoke(
        {"messages": messages},
        config={"callbacks": [callback]}
    )
"""

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult
from typing import Any, Dict, List, Optional
from backend.services.token_monitoring import token_monitor
from backend.utils import logger
import asyncio


class TokenTrackingCallbackHandler(AsyncCallbackHandler):
    """
    Callback handler that tracks token usage from LangChain calls.
    
    This handler automatically captures token usage from LLM calls and
    saves the data to Cosmos DB via the token monitoring service.
    """
    
    def __init__(
        self,
        user_id: str,
        thread_id: str,
        agent_name: Optional[str] = None,
        operation_type: str = "chat"
    ):
        """
        Initialize the token tracking callback handler.
        
        Args:
            user_id: User identifier for tracking
            thread_id: Conversation thread ID
            agent_name: Name of the agent making the calls
            operation_type: Type of operation (chat, embedding, etc.)
        """
        super().__init__()
        self.user_id = user_id
        self.thread_id = thread_id
        self.agent_name = agent_name
        self.operation_type = operation_type
        self._run_metadata: Dict[str, Dict] = {}
    
    async def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any
    ) -> None:
        """Called when LLM starts running."""
        run_id = kwargs.get("run_id")
        if run_id:
            self._run_metadata[str(run_id)] = {
                "model": serialized.get("kwargs", {}).get("model_name", "unknown"),
                "prompts": prompts
            }
    
    async def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any
    ) -> None:
        """
        Called when LLM ends running.
        
        This is where we extract token usage and track it.
        """
        try:
            run_id = kwargs.get("run_id")
            metadata = self._run_metadata.get(str(run_id), {}) if run_id else {}
            
            # Extract token usage from response
            llm_output = response.llm_output or {}
            token_usage = llm_output.get("token_usage", {})
            
            # Try different keys that various providers use
            input_tokens = (
                token_usage.get("prompt_tokens", 0) or
                token_usage.get("input_tokens", 0) or
                0
            )
            output_tokens = (
                token_usage.get("completion_tokens", 0) or
                token_usage.get("output_tokens", 0) or
                0
            )
            
            # Get model name
            model = (
                metadata.get("model") or
                llm_output.get("model_name") or
                llm_output.get("model") or
                "unknown"
            )
            
            # Only track if we have token data
            if input_tokens > 0 or output_tokens > 0:
                # Track the usage
                await token_monitor.track_usage(
                    user_id=self.user_id,
                    thread_id=self.thread_id,
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    agent_name=self.agent_name,
                    operation_type=self.operation_type,
                    request_metadata={
                        "run_id": str(run_id) if run_id else None,
                        "generations": len(response.generations)
                    }
                )
                
                logger.info(
                    f"Token usage tracked: {input_tokens} input + {output_tokens} output = "
                    f"{input_tokens + output_tokens} total tokens (model: {model})"
                )
            
            # Clean up metadata
            if run_id and str(run_id) in self._run_metadata:
                del self._run_metadata[str(run_id)]
                
        except Exception as e:
            logger.error(f"Error tracking token usage in callback: {e}")
            # Don't raise - we don't want monitoring to break the application
    
    async def on_llm_error(
        self,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """Called when LLM errors."""
        run_id = kwargs.get("run_id")
        if run_id and str(run_id) in self._run_metadata:
            del self._run_metadata[str(run_id)]
    
    async def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Called when chain starts running."""
        pass
    
    async def on_chain_end(
        self,
        outputs: Dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Called when chain ends running."""
        pass
    
    async def on_chain_error(
        self,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """Called when chain errors."""
        pass


def create_token_tracking_callback(
    config: Dict[str, Any],
    agent_name: Optional[str] = None
) -> TokenTrackingCallbackHandler:
    """
    Create a token tracking callback from agent configuration.
    
    Args:
        config: Agent configuration containing user_id and thread_id
        agent_name: Name of the agent
        
    Returns:
        TokenTrackingCallbackHandler instance
    """
    configurable = config.get("configurable", {})
    
    user_id = configurable.get("user_id", "unknown")
    thread_id = configurable.get("thread_id", "unknown")
    
    return TokenTrackingCallbackHandler(
        user_id=user_id,
        thread_id=thread_id,
        agent_name=agent_name
    )


def attach_token_tracking(config: Dict[str, Any], agent_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Attach token tracking callback to agent configuration.
    
    This is a helper function to easily add token tracking to any agent call.
    
    Usage:
        config = attach_token_tracking(config, agent_name="domain_agent")
        result = await agent.ainvoke(input_data, config)
    
    Args:
        config: Agent configuration
        agent_name: Name of the agent
        
    Returns:
        Updated configuration with callback attached
    """
    callback = create_token_tracking_callback(config, agent_name)
    
    # Add callback to config
    if "callbacks" not in config:
        config["callbacks"] = []
    config["callbacks"].append(callback)
    
    return config



