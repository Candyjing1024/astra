"""
Standalone Microsoft ASTRA Roadmap Agent

This module provides a standalone LangGraph agent specialized for answering questions
about the Microsoft ASTRA (Agentic AI System for Transformation, Reasoning & Autonomy)
platform, its roadmap, architecture, and transformation strategy.

Features:
- Specialized RAG search for ASTRA roadmap documentation
- ReAct pattern implementation with reasoning and action capabilities
- State management with conversation persistence
- Pre-model summarization hooks for context management

Usage:
    from backend.app.agents.astra_standalone_agent import astra_roadmap_agent
    
    # Use in your application
    result = astra_roadmap_agent.invoke(
        {"messages": [{"role": "user", "content": "What is Microsoft ASTRA?"}]},
        config={"thread_id": "conversation_id"}
    )
"""

from langgraph.prebuilt import create_react_agent
from prompty import load_prompty
from backend.tools.bing_search_tool import bing_search_tool
from backend.agents import prompts
from backend.utils import chat_completion_model, summarization_node, State, logger
import importlib.resources as pkg_resources

# Load the Bing Search Agent prompt
bing_search_agent_prompt_filepath = pkg_resources.files(prompts).joinpath("bing_search_agent.prompty")
logger.info(f"Bing search agent prompt file path: {bing_search_agent_prompt_filepath}")
bing_search_agent_prompt = load_prompty(bing_search_agent_prompt_filepath)

# Create the standalone Bing Search Agent
bing_search_agent = create_react_agent(
    model=chat_completion_model,
    tools=[bing_search_tool],
    pre_model_hook=summarization_node,
    state_schema=State,
    checkpointer=True,
    name="bing_search_agent",
    prompt=bing_search_agent_prompt["body"]
)