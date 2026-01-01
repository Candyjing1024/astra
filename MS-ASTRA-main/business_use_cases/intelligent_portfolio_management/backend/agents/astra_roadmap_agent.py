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
    from backend.agents.astra_standalone_agent import astra_roadmap_agent
    
    # Use in your application
    result = astra_roadmap_agent.invoke(
        {"messages": [{"role": "user", "content": "What is Microsoft ASTRA?"}]},
        config={"thread_id": "conversation_id"}
    )
"""

from langgraph.prebuilt import create_react_agent
from prompty import load_prompty
from backend.tools.rag_tool import astra_roadmap_search_retrieval
from backend.agents import prompts
from backend.utils import chat_completion_model, summarization_node, State, logger
import importlib.resources as pkg_resources

# Load the ASTRA Roadmap Agent prompt
astra_roadmap_agent_prompt_filepath = pkg_resources.files(prompts).joinpath("astra_roadmap_agent.prompty")
logger.info(f"ASTRA roadmap agent prompt file path: {astra_roadmap_agent_prompt_filepath}")
astra_roadmap_agent_prompt = load_prompty(astra_roadmap_agent_prompt_filepath)

# Create the standalone ASTRA Roadmap Agent
astra_roadmap_agent = create_react_agent(
    model=chat_completion_model,
    tools=[astra_roadmap_search_retrieval],
    pre_model_hook=summarization_node,
    state_schema=State,
    checkpointer=True,
    name="astra_roadmap_expert",
    prompt=astra_roadmap_agent_prompt["body"]
)