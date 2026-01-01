"""
Generic Research Agent Template

TEMPLATE FILE: This is a generic template for research and internet search agents.
Customize this template for your specific research needs.

This module provides a research agent that specializes in gathering real-time
information from the internet and external sources to supplement domain knowledge.

Features:
- Internet search capabilities using Bing Search API
- Real-time information retrieval
- Market research and trend analysis
- External data integration
- Fact-checking and validation

CUSTOMIZATION:
1. Update the agent description for your research focus
2. Configure research-specific tools and APIs
3. Customize search parameters and filters
4. Add domain-specific research capabilities

Usage:
    from backend.agents.research_agent import research_agent
    
    # Use for research queries
    result = research_agent.invoke(
        {"messages": [{"role": "user", "content": "Research latest trends in [domain]"}]}
    )
"""

from backend.utils import chat_completion_model, logger
from backend.tools.internet_tool import internet_search  # Customize tool import
from langchain_core.messages import HumanMessage
from langgraph import create_react_agent
from prompty import load_prompty
import importlib.resources as pkg_resources
from backend.agents import prompts

# CUSTOMIZE: Update agent configuration for your research needs
AGENT_NAME = "research_agent"  # Can be specialized (e.g., "market_research_agent")
AGENT_DESCRIPTION = "Specialized agent for real-time research and information gathering"

# Load research agent prompt
# CUSTOMIZE: Update prompt filename for your research focus
try:
    research_agent_prompt_filepath = pkg_resources.files(prompts).joinpath("research_agent.prompty")
    logger.info(f"Research agent prompt file path: {research_agent_prompt_filepath}")
    research_agent_prompt = load_prompty(research_agent_prompt_filepath)
    prompt_template = research_agent_prompt["body"]
except FileNotFoundError:
    logger.warning("Research agent prompt not found - using default prompt")
    # Default generic prompt template
    prompt_template = """
    You are a specialized research agent focused on gathering real-time information
    and conducting comprehensive research to support decision-making.
    
    Your capabilities include:
    - Searching the internet for current information and trends
    - Gathering data from multiple sources
    - Analyzing and synthesizing research findings
    - Providing factual, up-to-date information
    - Identifying relevant resources and references
    
    Research Guidelines:
    1. Use internet search tools to find current information
    2. Verify information from multiple sources when possible
    3. Provide clear citations and sources
    4. Focus on recent, relevant, and credible information
    5. Synthesize findings into actionable insights
    
    CUSTOMIZE: Replace this with your research-specific instructions and focus areas.
    """

# CUSTOMIZE: Configure your research-specific tools
try:
    # Add your research tools here
    research_tools = [internet_search]
except NameError:
    logger.warning("Research tools not available - implement your research-specific tools")
    research_tools = []

# Create the research agent with ReAct pattern
research_agent = create_react_agent(
    model=chat_completion_model,
    tools=research_tools,
    state_modifier=prompt_template,
)

# Agent metadata for identification
research_agent.name = AGENT_NAME
research_agent.description = AGENT_DESCRIPTION

logger.info(f"Initialized {AGENT_NAME} with {len(research_tools)} tools")