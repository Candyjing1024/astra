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
    from backend.agents.astra_standalone_supervisor import astra_domain_supervisor
    
    # Use in your application
    result = astra_domain_supervisor.invoke(
        {"messages": [{"role": "user", "content": "Tell me about ASTRA's architecture"}]},
        config={"thread_id": "conversation_id"}
    )
"""

from backend.agents import prompts
from backend.utils import chat_completion_model, checkpointer, State, logger
from backend.agents.astra_roadmap_agent import astra_roadmap_agent
from backend.agents.react_agents import internet_agent
from prompty import load_prompty
import importlib.resources as pkg_resources
from langgraph_supervisor import create_supervisor

# Load the ASTRA Domain Supervisor prompt
astra_domain_supervisor_prompt_filepath = pkg_resources.files(prompts).joinpath("astra_domain_supervisor.prompty")
logger.info(f"ASTRA domain supervisor prompt file path: {astra_domain_supervisor_prompt_filepath}")
astra_domain_supervisor_prompt = load_prompty(astra_domain_supervisor_prompt_filepath)

# Create the ASTRA Domain Supervisor
astra_domain_supervisor = create_supervisor(
    [astra_roadmap_agent],
    model=chat_completion_model,
    prompt=astra_domain_supervisor_prompt["body"],
    add_handoff_back_messages=True,
    output_mode="full_history",
    supervisor_name="astra_domain_supervisor"
)
