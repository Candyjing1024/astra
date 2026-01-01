"""
Generic Domain Supervisor Agent Template

TEMPLATE FILE: This is a generic template for domain-specific supervisor agents.
Customize this template for your specific business use case.

This module provides a LangGraph supervisor agent that manages and coordinates
queries within your specific domain. The supervisor routes queries to the
appropriate specialist agents and synthesizes responses.

Features:
- Domain-agnostic supervision pattern
- Multi-agent coordination between domain specialist and research agents
- Intelligent query routing and response synthesis
- State management and conversation persistence

CUSTOMIZATION:
1. Replace [YOUR_DOMAIN] with your specific domain (e.g., "portfolio_management", "healthcare")
2. Import your domain-specific agents
3. Update the prompt filepath to your domain prompt
4. Customize the supervisor name and configuration

Usage:
    from backend.agents.domain_supervisor import domain_supervisor
    
    # Use in your application
    result = domain_supervisor.invoke(
        {"messages": [{"role": "user", "content": "Your domain-specific query"}]},
        config={"thread_id": "conversation_id"}
    )
"""

from backend.agents import prompts
from backend.utils import chat_completion_model, checkpointer, State, logger
# CUSTOMIZE: Import your domain-specific agents
# from backend.agents.domain_agent import domain_agent
# from backend.agents.research_agent import research_agent
from prompty import load_prompty
import importlib.resources as pkg_resources
from langgraph_supervisor import create_supervisor

# PLACEHOLDER AGENTS - Replace with your domain agents
try:
    from backend.agents.react_agents import internet_agent
    available_agents = [internet_agent]
except ImportError:
    logger.warning("No agents available - implement your domain agents")
    available_agents = []

# Load the Domain Supervisor prompt
# CUSTOMIZE: Update the prompt filename for your domain
domain_supervisor_prompt_filepath = pkg_resources.files(prompts).joinpath("domain_supervisor.prompty")
logger.info(f"Domain supervisor prompt file path: {domain_supervisor_prompt_filepath}")

try:
    domain_supervisor_prompt = load_prompty(domain_supervisor_prompt_filepath)
    prompt_body = domain_supervisor_prompt["body"]
except FileNotFoundError:
    logger.warning("Domain supervisor prompt not found - using default prompt")
    # Default generic prompt
    prompt_body = """
    You are a domain supervisor agent responsible for coordinating and managing queries 
    within your specific domain. Route queries to appropriate specialist agents and 
    synthesize their responses to provide comprehensive answers.
    
    CUSTOMIZE: Replace this with your domain-specific prompt.
    """

# Create the Domain Supervisor
# CUSTOMIZE: Update supervisor_name for your domain
domain_supervisor = create_supervisor(
    available_agents,
    model=chat_completion_model,
    prompt=prompt_body,
    add_handoff_back_messages=True,
    output_mode="full_history",
    supervisor_name="domain_supervisor"  # Change to your domain (e.g., "portfolio_supervisor")
)