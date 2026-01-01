"""
This module defines the Internet Agent for the agentic framework, which is responsible
for performing web searches and retrieving information from external internet sources.

Key Features:
    1. Integration with Bing Grounding Tool for internet searches
    2. ReAct (Reasoning and Acting) agent pattern implementation
    3. Configurable prompts for specialized internet search behaviors
    4. Integration with the chat completion model for natural language processing

The Internet Agent is designed to handle queries that require external web information
and can be integrated into the larger multi-agent supervisor system. Currently, the
implementation is commented out and serves as a template for future development.

Components:
- Agent Creation: Uses LangGraph's create_react_agent to build a reactive agent
- Tool Integration: Connects to internet_bing_grounding_tool for web searches
- Prompt Management: Loads specialized prompts from the prompts directory
- Model Configuration: Uses the configured chat completion model

Future Implementation:
When uncommented, this agent will provide the agentic framework with the ability
to search the internet for real-time information and external knowledge sources.
"""

# from langgraph.prebuilt import create_react_agent
# from prompty import load_prompty
# from agentic_framework.app.agents.tools.internet_tool import internet_bing_grounding_tool
# from agentic_framework.app.agents import prompts
# from agentic_framework.app.utils import chat_completion_model
# import importlib.resources as pkg_resources

 
# internet_agent_prompt_filepath = pkg_resources.files(prompts).joinpath("internet_agent.prompty")
# internet_agent_prompt = load_prompty(internet_agent_prompt_filepath)

# internet_agent = create_react_agent(
#     model=chat_completion_model,
#     tools=[internet_bing_grounding_tool],
#     name="internet_agent",
#     prompt=internet_agent_prompt["body"]
#    )
