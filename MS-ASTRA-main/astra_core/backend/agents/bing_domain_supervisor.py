"""
Standalone Microsoft ASTRA Domain Supervisor Agent

This module provides a standalone LangGraph supervisor agent that manages and coordinates
queries related to the Microsoft ASTRA platform. The supervisor routes queries to the
appropriate specialist agents and synthesizes responses.

Features:
- Domain-specific supervision for ASTRA platform queries
- Multi-agent coordination between ASTRA specialist and supplementary agents
- Intelligent query routing and response synthesis
- State management and conversation persistence

Usage:
    from backend.app.agents.astra_standalone_supervisor import astra_domain_supervisor
    
    # Use in your application
    result = astra_domain_supervisor.invoke(
        {"messages": [{"role": "user", "content": "Tell me about ASTRA's architecture"}]},
        config={"thread_id": "conversation_id"}
    )
"""

from backend.agents import prompts
from backend.utils import chat_completion_model, logger
from backend.agents.bing_search_agent import bing_search_agent
from prompty import load_prompty
import importlib.resources as pkg_resources
from langgraph_supervisor import create_supervisor

# Load the Bing Domain Supervisor prompt
bing_domain_supervisor_prompt_filepath = pkg_resources.files(prompts).joinpath("bing_domain_supervisor.prompty")
logger.info(f"Bing domain supervisor prompt file path: {bing_domain_supervisor_prompt_filepath}")
bing_domain_supervisor_prompt = load_prompty(bing_domain_supervisor_prompt_filepath)

# Create the Bing Domain Supervisor
bing_domain_supervisor = create_supervisor(
    [bing_search_agent],
    model=chat_completion_model,
    prompt=bing_domain_supervisor_prompt["body"],
    add_handoff_back_messages=True,
    output_mode="full_history",
    supervisor_name="bing_domain_supervisor"
)
