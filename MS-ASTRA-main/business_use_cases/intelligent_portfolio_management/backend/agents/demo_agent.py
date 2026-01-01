import os
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from copilotkit import CopilotKitState
from backend.utils import chat_completion_model, summarization_node, State, logger

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
# azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://openai-hq-demo.openai.azure.com/")
# model_name = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")
# api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")

# model = AzureChatOpenAI(
#     model=model_name,
#     api_key=api_key,
#     api_version=api_version,
#     azure_endpoint=azure_endpoint,
#     temperature=0.2
# )

# class AgentState(CopilotKitState):
#     remaining_steps: int

# Define Tools
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def web_search(query: str) -> str:
    """Search the web for information."""
    return (
        "Here are the headcounts for each of the FAANG companies in 2024:\n"
        "1. **Facebook (Meta)**: 67,317 employees.\n"
        "2. **Apple**: 164,000 employees.\n"
        "3. **Amazon**: 1,551,000 employees.\n"
        "4. **Netflix**: 14,000 employees.\n"
        "5. **Google (Alphabet)**: 181,269 employees."
    )

# Create Agents
math_agent = create_react_agent(
    model=chat_completion_model,
    tools=[add, multiply],
    pre_model_hook=summarization_node,
    state_schema=State,
    checkpointer=True,
    name="math_expert",
    prompt="You are a math expert. Always use one tool at a time."
)

research_agent = create_react_agent(
    model=chat_completion_model,
    tools=[web_search],
    pre_model_hook=summarization_node,
    state_schema=State,
    checkpointer=True,
    name="research_expert",
    prompt="You are a world-class researcher with access to web search. Do not do any math."
)

# Create Supervisor with default state
demo_supervisor = create_supervisor(
    [research_agent, math_agent],
    model=chat_completion_model,
    prompt=(
        "You are a team supervisor managing a research expert and a math expert. "
        "For current events, use research_agent. "
        "For math problems, use math_agent."
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
    supervisor_name="demo_supervisor"
)

# Compile the Workflow
# app = workflow.compile()

# Function to Invoke Workflow
# def process_query(user_input: str):
#     result = app.invoke({
#         "messages": [{"role": "user", "content": user_input}]
#     })
#     return result["messages"]  # Returning messages for processing


# Create in-memory checkpointer and compile with it
# memory = InMemorySaver()