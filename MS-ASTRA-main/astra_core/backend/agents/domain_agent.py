"""
Generic Domain Agent Template

TEMPLATE FILE: This is a generic template for domain-specific analysis agents.
Customize this template for your specific business use case.

This module provides a domain-specific agent that specializes in analyzing
and responding to queries within your business domain using RAG retrieval
and domain expertise.

Features:
- Domain-specific knowledge retrieval using Azure AI Search
- RAG-powered responses based on your knowledge base
- Integration with domain-specific tools and data sources
- Structured analysis and recommendations

CUSTOMIZATION:
1. Replace [YOUR_DOMAIN] with your specific domain name
2. Update the agent description and prompt
3. Configure your domain-specific tools
4. Customize the knowledge retrieval parameters

Usage:
    from backend.agents.domain_agent import domain_agent
    
    # Use in conversations
    result = domain_agent.invoke(
        {"messages": [{"role": "user", "content": "Domain-specific query"}]}
    )
"""

from backend.utils import chat_completion_model, logger
from backend.tools.rag_tool import domain_search_retrieval  # Customize tool import
from langchain_core.messages import HumanMessage
from langgraph import create_react_agent
from prompty import load_prompty
import importlib.resources as pkg_resources
from backend.agents import prompts

# CUSTOMIZE: Update agent configuration for your domain
AGENT_NAME = "domain_agent"  # Change to your domain (e.g., "portfolio_agent")
AGENT_DESCRIPTION = "Specialized agent for [YOUR_DOMAIN] analysis and recommendations"

# Load domain-specific prompt
# CUSTOMIZE: Update prompt filename for your domain
try:
    domain_agent_prompt_filepath = pkg_resources.files(prompts).joinpath("domain_agent.prompty")
    logger.info(f"Domain agent prompt file path: {domain_agent_prompt_filepath}")
    domain_agent_prompt = load_prompty(domain_agent_prompt_filepath)
    prompt_template = domain_agent_prompt["body"]
except FileNotFoundError:
    logger.warning("Domain agent prompt not found - using default prompt")
    # Default generic prompt template
    prompt_template = """
    You are a specialized AI agent for [YOUR_DOMAIN] analysis and assistance.
    
    Your capabilities include:
    - Analyzing domain-specific data and providing insights
    - Retrieving relevant information from the knowledge base
    - Providing recommendations based on domain expertise
    - Answering questions with accurate, contextual information
    
    Instructions:
    1. Use the available tools to search for relevant information
    2. Provide comprehensive analysis based on retrieved data
    3. Offer specific recommendations when appropriate
    4. Be clear about limitations and assumptions
    
    CUSTOMIZE: Replace this with your domain-specific instructions and capabilities.
    """

# CUSTOMIZE: Configure your domain-specific tools
try:
    # Replace with your domain tools
    domain_tools = [domain_search_retrieval]
except NameError:
    logger.warning("Domain tools not available - implement your domain-specific tools")
    domain_tools = []

# Create the domain agent with ReAct pattern
domain_agent = create_react_agent(
    model=chat_completion_model,
    tools=domain_tools,
    state_modifier=prompt_template,
)

# Agent metadata for identification
domain_agent.name = AGENT_NAME
domain_agent.description = AGENT_DESCRIPTION

logger.info(f"Initialized {AGENT_NAME} with {len(domain_tools)} tools")