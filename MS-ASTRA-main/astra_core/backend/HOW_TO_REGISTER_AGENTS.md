# How to Register Agents in Cosmos DB Token Monitoring

## 📝 Quick Answer

**Agents are automatically "registered" when you track their usage.** There's no separate registration step!

---

## 🎯 Three Ways to Track Agents

### **Method 1: Modify Your Agent Files (Recommended for Consistency)**

Update your agent file to include automatic tracking:

**Before** (`domain_agent.py`):
```python
domain_agent = create_react_agent(
    model=chat_completion_model,
    tools=domain_tools,
    state_modifier=prompt_template,
)

domain_agent.name = AGENT_NAME
domain_agent.description = AGENT_DESCRIPTION
```

**After** (with token tracking wrapper):
```python
from backend.callbacks import TokenTrackingCallbackHandler

# Create the base agent
base_domain_agent = create_react_agent(
    model=chat_completion_model,
    tools=domain_tools,
    state_modifier=prompt_template,
)

# Wrap with tracking functionality
class TrackedDomainAgent:
    def __init__(self, base_agent, agent_name):
        self.base_agent = base_agent
        self.agent_name = agent_name
        self.name = agent_name
        self.description = f"Tracked {agent_name}"
    
    async def ainvoke(self, input_data, config=None, **kwargs):
        """Invoke with automatic token tracking."""
        if config is None:
            config = {}
        
        # Create callback
        callback = TokenTrackingCallbackHandler(
            user_id=config.get("configurable", {}).get("user_id", "unknown"),
            thread_id=config.get("configurable", {}).get("thread_id", "unknown"),
            agent_name=self.agent_name
        )
        
        # Add callback to config
        if "callbacks" not in config:
            config["callbacks"] = []
        config["callbacks"].append(callback)
        
        # Call base agent
        return await self.base_agent.ainvoke(input_data, config, **kwargs)
    
    def invoke(self, input_data, config=None, **kwargs):
        """Sync invoke (if needed)."""
        # Similar implementation for sync calls
        return self.base_agent.invoke(input_data, config, **kwargs)

# Export the tracked agent
domain_agent = TrackedDomainAgent(base_domain_agent, AGENT_NAME)

logger.info(f"Initialized tracked {AGENT_NAME} with {len(domain_tools)} tools")
```

### **Method 2: Add Tracking at Usage Point (Simplest)**

Don't modify agent files - add tracking when you use them:

```python
from backend.agents.domain_agent import domain_agent
from backend.callbacks import attach_token_tracking

# When you use the agent
config = {
    "configurable": {
        "user_id": "user@example.com",
        "thread_id": "conversation-123"
    }
}

# Add tracking
config = attach_token_tracking(config, agent_name="domain_agent")

# Use agent normally - tokens tracked automatically
result = await domain_agent.ainvoke(
    {"messages": [{"role": "user", "content": "query"}]},
    config=config
)
```

### **Method 3: Track in Supervisor (Best for Multi-Agent)**

Track at the supervisor level to capture all agent calls:

```python
from backend.agents.domain_supervisor import domain_supervisor
from backend.callbacks import attach_token_tracking

# Track the entire supervisor (includes all sub-agents)
config = {
    "configurable": {
        "user_id": "user@example.com",
        "thread_id": "conversation-123"
    }
}

# This tracks the supervisor and all its sub-agents
config = attach_token_tracking(config, agent_name="domain_supervisor")

result = await domain_supervisor.ainvoke(
    {"messages": [{"role": "user", "content": "query"}]},
    config=config
)
```

---

## 🔍 **Verify Agent Registration**

After using your agents with tracking, verify they're registered:

### **Python Query**

```python
from backend.services.token_monitoring import token_monitor
from datetime import datetime, timedelta

# Get usage for last 7 days
start_date = datetime.utcnow() - timedelta(days=7)
stats = await token_monitor.get_user_usage("user@example.com", start_date=start_date)

# Check which agents are registered
print("Registered Agents:")
for agent_name, request_count in stats.requests_by_agent.items():
    print(f"  ✓ {agent_name}: {request_count} requests")
```

### **API Query**

```bash
# Get user stats (includes agent breakdown)
curl http://localhost:8000/token-usage/user/user@example.com?days=7
```

**Look for the `requests_by_agent` field:**
```json
{
  "requests_by_agent": {
    "domain_agent": 45,
    "research_agent": 23,
    "bing_search_agent": 12
  }
}
```

---

## 📋 **Complete Integration Example**

Here's a complete example showing how to integrate with the existing ASTRA system:

### **File: `backend/agents/tracked_domain_agent.py`**

```python
"""
Domain Agent with Automatic Token Tracking

This is an enhanced version of domain_agent that automatically tracks
token usage in Cosmos DB for all interactions.
"""

from backend.utils import chat_completion_model, logger
from backend.tools.rag_tool import domain_search_retrieval
from backend.callbacks import TokenTrackingCallbackHandler
from langchain_core.messages import HumanMessage
from langgraph import create_react_agent
from prompty import load_prompty
import importlib.resources as pkg_resources
from backend.agents import prompts
from typing import Any, Dict, Optional

AGENT_NAME = "domain_agent"
AGENT_DESCRIPTION = "Domain analysis agent with token tracking"

# Load prompt
try:
    domain_agent_prompt_filepath = pkg_resources.files(prompts).joinpath("domain_agent.prompty")
    domain_agent_prompt = load_prompty(domain_agent_prompt_filepath)
    prompt_template = domain_agent_prompt["body"]
except FileNotFoundError:
    logger.warning("Using default domain agent prompt")
    prompt_template = "You are a domain-specific AI agent."

# Configure tools
domain_tools = [domain_search_retrieval]

# Create base agent
base_agent = create_react_agent(
    model=chat_completion_model,
    tools=domain_tools,
    state_modifier=prompt_template,
)


class TrackedAgent:
    """Wrapper that adds automatic token tracking to any agent."""
    
    def __init__(self, agent, agent_name: str):
        self.agent = agent
        self.agent_name = agent_name
        self.name = agent_name
        self.description = f"Tracked {agent_name}"
    
    def _add_tracking_callback(self, config: Optional[Dict] = None) -> Dict:
        """Add token tracking callback to config."""
        if config is None:
            config = {}
        
        # Extract user_id and thread_id
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id", "unknown")
        thread_id = configurable.get("thread_id", "unknown")
        
        # Create callback
        callback = TokenTrackingCallbackHandler(
            user_id=user_id,
            thread_id=thread_id,
            agent_name=self.agent_name
        )
        
        # Add to callbacks
        if "callbacks" not in config:
            config["callbacks"] = []
        config["callbacks"].append(callback)
        
        return config
    
    async def ainvoke(self, input_data: Any, config: Optional[Dict] = None, **kwargs) -> Any:
        """Async invoke with automatic token tracking."""
        config = self._add_tracking_callback(config)
        return await self.agent.ainvoke(input_data, config, **kwargs)
    
    def invoke(self, input_data: Any, config: Optional[Dict] = None, **kwargs) -> Any:
        """Sync invoke with automatic token tracking."""
        config = self._add_tracking_callback(config)
        return self.agent.invoke(input_data, config, **kwargs)
    
    async def astream(self, input_data: Any, config: Optional[Dict] = None, **kwargs):
        """Async stream with automatic token tracking."""
        config = self._add_tracking_callback(config)
        async for chunk in self.agent.astream(input_data, config, **kwargs):
            yield chunk
    
    def stream(self, input_data: Any, config: Optional[Dict] = None, **kwargs):
        """Sync stream with automatic token tracking."""
        config = self._add_tracking_callback(config)
        for chunk in self.agent.stream(input_data, config, **kwargs):
            yield chunk


# Export tracked agent
domain_agent = TrackedAgent(base_agent, AGENT_NAME)

logger.info(f"✓ Initialized tracked {AGENT_NAME} with automatic token monitoring")
```

### **Usage:**

```python
from backend.agents.tracked_domain_agent import domain_agent

# Use normally - tracking is automatic!
config = {
    "configurable": {
        "user_id": "user@example.com",
        "thread_id": "conversation-123"
    }
}

result = await domain_agent.ainvoke(
    {"messages": [{"role": "user", "content": "Analyze portfolio"}]},
    config=config
)

# Agent usage is automatically registered in Cosmos DB!
```

---

## 🎯 **Recommended Approach for ASTRA**

For your ASTRA system, I recommend **Method 2** (add tracking at usage point) because:

1. ✅ **Non-invasive**: Doesn't modify existing agent files
2. ✅ **Flexible**: Easy to add/remove tracking
3. ✅ **Centralized**: Track at supervisor level
4. ✅ **Clear**: Explicit about what's being tracked

### **Implementation:**

**In `backend/run.py` (already done)**:

```python
def create_agents(context):
    """Create agents with token tracking."""
    
    user_id = context.get('properties', {}).get('user_id')
    
    agent_config = {
        'configurable': {
            'user_id': user_id
        }
    }
    
    # Add token tracking to the config
    from backend.callbacks import attach_token_tracking
    agent_config = attach_token_tracking(
        agent_config, 
        agent_name="domain_supervisor"  # Track the main supervisor
    )
    
    return [
        SessionAwareLangGraphAgent(
            checkpointer=checkpointer,
            name="domain_agent",
            description="AI assistant with token tracking",
            graph=graph,
            langgraph_config=agent_config,
        )
    ]
```

---

## 📊 **View All Registered Agents**

To see all agents that have been "registered" (i.e., tracked):

```python
from backend.services.token_monitoring import token_monitor
from datetime import datetime, timedelta

# Get all usage records
start_date = datetime.utcnow() - timedelta(days=30)
records = await token_monitor.get_all_usage(start_date=start_date, limit=1000)

# Extract unique agent names
agents = set(record.get("agent_name") for record in records if record.get("agent_name"))

print("Registered Agents:")
for agent in sorted(agents):
    print(f"  ✓ {agent}")
```

**Output:**
```
Registered Agents:
  ✓ bing_search_agent
  ✓ domain_agent
  ✓ domain_supervisor
  ✓ research_agent
```

---

## 🔧 **Agent Naming Best Practices**

1. **Use consistent names** across your codebase
2. **Be descriptive**: `portfolio_agent` better than `agent1`
3. **Match file names**: If file is `domain_agent.py`, use `domain_agent`
4. **Hierarchy**: Use dots for sub-agents: `supervisor.domain.search`

**Example:**
```python
# Main supervisor
config = attach_token_tracking(config, agent_name="supervisor")

# Domain agent under supervisor
config = attach_token_tracking(config, agent_name="supervisor.domain")

# Research agent
config = attach_token_tracking(config, agent_name="supervisor.research")
```

This creates a hierarchy in your analytics:
```
supervisor: 150 requests
  ├─ supervisor.domain: 89 requests
  └─ supervisor.research: 61 requests
```

---

## ✅ **Quick Checklist**

- [ ] Choose tracking method (recommend Method 2)
- [ ] Add `attach_token_tracking()` to your agent calls
- [ ] Use consistent agent names
- [ ] Test with a few calls
- [ ] Verify agents appear in statistics
- [ ] Set up monitoring dashboard (optional)

---

## 🎉 **Summary**

**Agents are "registered" automatically when you use them with token tracking.**

**Simplest way:**
```python
from backend.callbacks import attach_token_tracking

config = attach_token_tracking(config, agent_name="my_agent")
result = await agent.ainvoke(input_data, config)
```

**That's it!** The agent is now tracked in Cosmos DB. 🚀

---

## 📞 **Need Help?**

- **View tracked agents**: `GET /token-usage/all`
- **Check agent stats**: Look for `requests_by_agent` in user stats
- **Test tracking**: Run `python -m backend.examples.token_monitoring_example`





