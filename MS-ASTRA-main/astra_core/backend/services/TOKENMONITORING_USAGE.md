# Token Monitoring System - Usage Guide

This guide explains how to use the token monitoring system to track OpenAI API usage and costs in your ASTRA application.

## Overview

The token monitoring system automatically tracks:
- Input and output tokens for every API call
- Cost calculations based on model pricing
- Per-user, per-session, and per-agent statistics
- Historical trends and analytics

All data is stored in Cosmos DB for long-term analysis and reporting.

## Architecture

```
┌─────────────────┐
│  Agent Calls    │
│  OpenAI API     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ TokenTrackingCallback   │
│ (Automatic Capture)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ TokenMonitoringService  │
│ (Calculate & Store)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Cosmos DB             │
│   token_usage container │
└─────────────────────────┘
```

## Quick Start

### 1. Automatic Token Tracking (Recommended)

The easiest way to track tokens is to use the callback handler with your agent calls:

```python
from backend.callbacks import attach_token_tracking

# Your existing agent code
config = {
    "configurable": {
        "user_id": "user@example.com",
        "thread_id": "conversation-123"
    }
}

# Add token tracking
config = attach_token_tracking(config, agent_name="domain_agent")

# Make agent call as usual - tokens will be tracked automatically
result = await agent.ainvoke({"messages": messages}, config=config)
```

### 2. Manual Token Tracking

If you need more control, you can manually track token usage:

```python
from backend.services.token_monitoring import token_monitor

# After making an OpenAI call
response = await chat_model.ainvoke(messages)

# Extract token usage
usage = response.usage_metadata
input_tokens = usage.get("input_tokens", 0)
output_tokens = usage.get("output_tokens", 0)

# Track it
await token_monitor.track_usage(
    user_id="user@example.com",
    thread_id="conversation-123",
    model="gpt-4o",
    input_tokens=input_tokens,
    output_tokens=output_tokens,
    agent_name="domain_agent",
    operation_type="chat"
)
```

## API Endpoints

### Get User Token Usage

Get aggregated statistics for a specific user:

```bash
GET /token-usage/user/{user_id}?days=30
```

**Response:**
```json
{
  "total_requests": 156,
  "total_input_tokens": 45230,
  "total_output_tokens": 28910,
  "total_tokens": 74140,
  "total_cost": 0.892340,
  "cost_by_model": {
    "gpt-4o": 0.780000,
    "gpt-4o-mini": 0.112340
  },
  "tokens_by_model": {
    "gpt-4o": 65000,
    "gpt-4o-mini": 9140
  },
  "requests_by_agent": {
    "domain_agent": 89,
    "research_agent": 67
  },
  "cost_trend": [
    {"date": "2024-01-01", "cost": 0.234500},
    {"date": "2024-01-02", "cost": 0.456789},
    {"date": "2024-01-03", "cost": 0.201051}
  ]
}
```

### Get Thread Token Usage

Get statistics for a specific conversation:

```bash
GET /token-usage/thread/{thread_id}
```

Returns the same format as user usage, but scoped to the conversation.

### Get All Token Usage Records

Get recent usage records across all users:

```bash
GET /token-usage/all?days=7&limit=100
```

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "user@example.com",
    "thread_id": "conversation-123",
    "timestamp": "2024-01-15T10:30:00Z",
    "model": "gpt-4o",
    "agent_name": "domain_agent",
    "operation_type": "chat",
    "input_tokens": 245,
    "output_tokens": 512,
    "total_tokens": 757,
    "total_cost": 0.007820
  }
]
```

### Get Usage by Model

Get statistics broken down by AI model:

```bash
GET /token-usage/by-model?days=30
```

**Response:**
```json
{
  "gpt-4o": {
    "total_requests": 120,
    "total_tokens": 65000,
    "total_cost": 0.780000,
    ...
  },
  "gpt-4o-mini": {
    "total_requests": 36,
    "total_tokens": 9140,
    "total_cost": 0.112340,
    ...
  }
}
```

## Integration Examples

### Example 1: Tracking in Custom Agent

```python
from backend.callbacks import TokenTrackingCallbackHandler

async def my_custom_agent(user_id: str, thread_id: str, query: str):
    """Custom agent with token tracking."""
    
    # Create callback
    callback = TokenTrackingCallbackHandler(
        user_id=user_id,
        thread_id=thread_id,
        agent_name="custom_agent"
    )
    
    # Use callback in agent call
    result = await chat_model.ainvoke(
        [{"role": "user", "content": query}],
        config={"callbacks": [callback]}
    )
    
    return result
```

### Example 2: Budget Monitoring

```python
from backend.services.token_monitoring import token_monitor
from datetime import datetime, timedelta

async def check_user_budget(user_id: str, budget_limit: float = 10.0):
    """Check if user is within budget."""
    
    # Get usage for current month
    start_date = datetime.utcnow().replace(day=1)
    stats = await token_monitor.get_user_usage(user_id, start_date)
    
    if stats.total_cost > budget_limit:
        print(f"⚠️  User {user_id} has exceeded budget!")
        print(f"   Usage: ${stats.total_cost:.2f} / ${budget_limit:.2f}")
        return False
    
    remaining = budget_limit - stats.total_cost
    print(f"✓ Budget OK: ${remaining:.2f} remaining")
    return True
```

### Example 3: Cost Analytics Dashboard

```python
from backend.services.token_monitoring import token_monitor

async def generate_cost_report():
    """Generate a cost analytics report."""
    
    # Get usage by model
    stats_by_model = await token_monitor.get_usage_by_model(days=30)
    
    print("\n📊 Token Usage Report (Last 30 Days)")
    print("=" * 60)
    
    total_cost = 0
    for model, stats in stats_by_model.items():
        print(f"\n{model}:")
        print(f"  Requests: {stats.total_requests:,}")
        print(f"  Tokens: {stats.total_tokens:,}")
        print(f"  Cost: ${stats.total_cost:.2f}")
        total_cost += stats.total_cost
    
    print("\n" + "=" * 60)
    print(f"Total Cost: ${total_cost:.2f}")
```

## Model Pricing Configuration

Pricing is configured in `token_monitoring.py`. Update the `MODEL_PRICING` dictionary to match your Azure OpenAI pricing:

```python
MODEL_PRICING = {
    "gpt-4o": {
        "input": 2.50,   # $2.50 per 1M input tokens
        "output": 10.00  # $10.00 per 1M output tokens
    },
    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60
    },
    # Add your models here
}
```

## Cosmos DB Schema

The token usage data is stored in the `token_usage` container with this schema:

```json
{
  "id": "uuid",
  "user_id": "user@example.com",          // Partition key
  "thread_id": "conversation-123",
  "timestamp": "2024-01-15T10:30:00Z",
  "model": "gpt-4o",
  "agent_name": "domain_agent",
  "operation_type": "chat",
  "input_tokens": 245,
  "output_tokens": 512,
  "total_tokens": 757,
  "input_cost": 0.000613,
  "output_cost": 0.005120,
  "total_cost": 0.005733,
  "request_metadata": {
    "run_id": "...",
    "generations": 1
  }
}
```

## Best Practices

### 1. Always Track Tokens
Add token tracking to all agent calls to ensure complete visibility:

```python
# ✓ Good
config = attach_token_tracking(config, agent_name="my_agent")
result = await agent.ainvoke(input_data, config)

# ✗ Bad - no tracking
result = await agent.ainvoke(input_data, config)
```

### 2. Set Budget Alerts
Implement budget monitoring to prevent cost overruns:

```python
async def rate_limited_agent_call(user_id, *args, **kwargs):
    # Check budget first
    if not await check_user_budget(user_id):
        raise Exception("Budget exceeded")
    
    # Make call
    return await agent.ainvoke(*args, **kwargs)
```

### 3. Regular Monitoring
Set up scheduled jobs to monitor usage:

```python
import asyncio

async def daily_cost_report():
    while True:
        await generate_cost_report()
        await asyncio.sleep(86400)  # Run daily
```

### 4. Model Selection
Use cost data to inform model selection:

```python
async def cost_aware_model_selection(complexity: str):
    """Choose model based on complexity and cost."""
    
    if complexity == "simple":
        return "gpt-4o-mini"  # Lower cost
    else:
        return "gpt-4o"  # Higher capability
```

## Troubleshooting

### Tokens Not Being Tracked

**Issue:** No token data appearing in Cosmos DB

**Solution:**
1. Verify callback is attached: `print(config.get("callbacks"))`
2. Check Cosmos DB connection in logs
3. Ensure `token_usage` container exists
4. Verify model returns `usage_metadata`

### Cost Calculations Incorrect

**Issue:** Costs don't match Azure billing

**Solution:**
1. Update `MODEL_PRICING` with current Azure OpenAI pricing
2. Check model name matches exactly
3. Verify token counts from API responses

### Performance Impact

**Issue:** Tracking adds latency

**Solution:**
1. Token tracking is async and non-blocking
2. Failures in tracking don't affect agent execution
3. Batch writes are used for efficiency

## Advanced Features

### Custom Metadata

Add custom metadata to track additional information:

```python
await token_monitor.track_usage(
    user_id=user_id,
    thread_id=thread_id,
    model="gpt-4o",
    input_tokens=100,
    output_tokens=200,
    request_metadata={
        "feature": "document_analysis",
        "document_type": "pdf",
        "page_count": 10
    }
)
```

### Export Data

Export token usage data for external analysis:

```python
async def export_usage_data(start_date, end_date):
    """Export usage data to CSV."""
    import csv
    
    records = await token_monitor.get_all_usage(
        start_date=start_date,
        end_date=end_date,
        limit=10000
    )
    
    with open("token_usage_export.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
```

## Support

For questions or issues:
1. Check logs in Azure Application Insights
2. Review Cosmos DB query performance
3. Verify Azure OpenAI response metadata
4. Contact your ASTRA administrator

## License

This token monitoring system is part of the ASTRA Core framework.



