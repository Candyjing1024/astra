"""
This module implements multiple ReAct (Reasoning and Acting) agents for the agentic framework,
each specialized for different knowledge domains and search capabilities.

Key Features:
    1. HQ Glossary Research Agent: Specialized for searching Hydro-Quebec's glossary database
    2. IT Support ReAct Agent: Handles IT support queries and knowledge base searches
    3. Internet Agent: Performs web searches using Bing Grounding Tool
    4. Intranet Agent: Searches internal Hydro-Quebec websites and resources
    5. ASTRA Roadmap Agent: Specialized for Microsoft ASTRA platform information and roadmap queries
    6. State Management: Implements custom state schema with summarization capabilities
    7. Checkpointing: Enables conversation persistence and resumption

Architecture:
Each agent follows the ReAct pattern, combining reasoning capabilities with specific
action tools. The agents use pre-model hooks for summarization and maintain state
across interactions through the checkpointing system.

Agents:
- research_graph: HQ Glossary expert using RAG search retrieval
- it_support_react_agent: IT support specialist with ServiceNow integration
- internet_agent: External web search capabilities
- intranet_agent: Internal website search (placeholder implementation)
- astra_roadmap_agent: Microsoft ASTRA platform expert using ASTRA Roadmap RAG search

Integration:
These agents are orchestrated by supervisor agents and can be called independently
or as part of a larger multi-agent workflow depending on the user's query domain.
"""

from langgraph.prebuilt import create_react_agent
from prompty import load_prompty
from backend.tools.rag_tool import it_support_search_retrieval, search_retrieval, astra_roadmap_search_retrieval
from backend.tools.internet_tool import internet_bing_grounding_tool
from backend.tools.intranet_tool import intranet_tool
from backend.agents import prompts
from backend.utils import chat_completion_model, summarization_node, State, logger
import importlib.resources as pkg_resources

# Read the file contents
prompt_filepath = pkg_resources.files(prompts).joinpath("hq_glossary_react_agents.prompty")
logger.info(f"react agent prompt file path: {prompt_filepath}")
react_agent_prompt = load_prompty(prompt_filepath)

research_graph = create_react_agent(
    model=chat_completion_model,
    tools=[search_retrieval],
    pre_model_hook=summarization_node,
    state_schema=State,
    checkpointer=True,
    name="search_expert",
   prompt = react_agent_prompt["body"]
)

it_support_react_agent_prompt_filepath = pkg_resources.files(prompts).joinpath("it_support_react_agents.prompty")
logger.info(f"it support react agent prompt file path: {it_support_react_agent_prompt_filepath}")
it_support_react_agent_prompt = load_prompty(it_support_react_agent_prompt_filepath)

it_support_react_agent = create_react_agent(
    model=chat_completion_model,
    tools=[it_support_search_retrieval],
    pre_model_hook=summarization_node,
    state_schema=State,
    checkpointer=True,
    name="it_search_expert",
    prompt=it_support_react_agent_prompt["body"]
)

internet_agent_prompt_filepath = pkg_resources.files(prompts).joinpath("internet_agent.prompty")
logger.info(f"internet agent prompt file path: {internet_agent_prompt_filepath}")
internet_agent_prompt = load_prompty(internet_agent_prompt_filepath)

internet_agent = create_react_agent(
    model=chat_completion_model,
    tools=[internet_bing_grounding_tool],
    name="internet_agent",
    prompt=internet_agent_prompt["body"]
   )

intranet_agent_prompt_filepath = pkg_resources.files(prompts).joinpath("intranet_agent.prompty")
logger.info(f"intranet agent prompt file path: {intranet_agent_prompt_filepath}")
intranet_agent_prompt = load_prompty(intranet_agent_prompt_filepath)
                                     
intranet_agent = create_react_agent(
    model=chat_completion_model,
    tools=[intranet_tool],
    name="intranet_agent",
    prompt=intranet_agent_prompt["body"]
    )

# ASTRA Roadmap Agent - Specialized for Microsoft ASTRA platform queries
astra_roadmap_agent_prompt_filepath = pkg_resources.files(prompts).joinpath("astra_roadmap_agent.prompty")
logger.info(f"ASTRA roadmap agent prompt file path: {astra_roadmap_agent_prompt_filepath}")
astra_roadmap_agent_prompt = load_prompty(astra_roadmap_agent_prompt_filepath)

astra_roadmap_agent = create_react_agent(
    model=chat_completion_model,
    tools=[astra_roadmap_search_retrieval],
    pre_model_hook=summarization_node,
    state_schema=State,
    checkpointer=True,
    name="astra_roadmap_expert",
    prompt=astra_roadmap_agent_prompt["body"]
)
