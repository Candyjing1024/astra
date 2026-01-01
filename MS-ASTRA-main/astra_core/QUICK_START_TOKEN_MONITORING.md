# Token Monitoring - Quick Start Guide

## ⚡ 5-Minute Setup

### 1. The system is already integrated! Just use it:

```python
from backend.callbacks import attach_token_tracking

# Your existing agent code
config = {
    "configurable": {
        "user_id": "user@example.com",
        "thread_id": "conversation-123"
    }
}

# Add this ONE line
config = attach_token_tracking(config, agent_name="my_agent")

# Continue as normal - tokens tracked automatically!
result = await agent.ainvoke({"messages": messages}, config=config)
```

### 2. Query usage via API:

```bash
# Get user usage (last 30 days)
curl http://localhost:8000/token-usage/user/user@example.com?days=30

# Get all recent usage
curl http://localhost:8000/token-usage/all?days=7&limit=100

# Get usage by model
curl http://localhost:8000/token-usage/by-model?days=30

# Get conversation usage
curl http://localhost:8000/token-usage/thread/conversation-123
```

### 3. Query from Python:

```python
from backend.services.token_monitoring import token_monitor

# Get user statistics
stats = await token_monitor.get_user_usage("user@example.com", days=30)

print(f"Total Requests: {stats.total_requests}")
print(f"Total Tokens: {stats.total_tokens:,}")
print(f"Total Cost: ${stats.total_cost:.2f}")

# By model
for model, cost in stats.cost_by_model.items():
    print(f"{model}: ${cost:.2f}")

# By agent
for agent, requests in stats.requests_by_agent.items():
    print(f"{agent}: {requests} requests")
```

## 📊 What Gets Tracked?

Every OpenAI API call captures:
- ✅ Input/output tokens
- ✅ Cost (calculated automatically)
- ✅ User ID
- ✅ Conversation thread
- ✅ Model used
- ✅ Agent name
- ✅ Timestamp
- ✅ Operation type

## 💾 Where's the Data?

- **Container**: `token_usage` (created automatically)
- **Database**: Your existing Cosmos DB
- **Partition Key**: `user_id`

## 🎯 Common Use Cases

### Budget Check
```python
from backend.services.token_monitoring import token_monitor
from datetime import datetime

# Check monthly spend
start_of_month = datetime.utcnow().replace(day=1)
stats = await token_monitor.get_user_usage("user@example.com", start_date=start_of_month)

if stats.total_cost > 10.00:  # $10 budget
    print(f"⚠️  Over budget! ${stats.total_cost:.2f}")
```

### Cost by Agent
```python
stats = await token_monitor.get_user_usage("user@example.com")
for agent, requests in stats.requests_by_agent.items():
    print(f"{agent}: {requests} requests")
```

### Daily Trend
```python
stats = await token_monitor.get_user_usage("user@example.com")
for day in stats.cost_trend:
    print(f"{day['date']}: ${day['cost']:.2f}")
```

## 🧪 Test It

Run the example script:

```bash
python -m backend.examples.token_monitoring_example
```

This demonstrates:
- Manual tracking
- Automatic callback tracking
- Querying statistics
- Budget monitoring
- Cost analysis
- Optimization suggestions

## 🔧 Update Pricing

Edit `backend/services/token_monitoring.py`:

```python
MODEL_PRICING = {
    "gpt-4o": {
        "input": 2.50,   # $/1M tokens
        "output": 10.00
    },
    "your-model": {
        "input": 1.00,
        "output": 3.00
    }
}
```

## 📋 API Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `GET /token-usage/user/{user_id}` | User stats | `?days=30` |
| `GET /token-usage/thread/{thread_id}` | Thread stats | - |
| `GET /token-usage/all` | All records | `?days=7&limit=100` |
| `GET /token-usage/by-model` | By model | `?days=30` |

## 🎓 Examples

### Example 1: Basic Integration
```python
from backend.callbacks import TokenTrackingCallbackHandler

callback = TokenTrackingCallbackHandler(
    user_id="user@example.com",
    thread_id="conv-123",
    agent_name="my_agent"
)

result = await chat_model.ainvoke(
    messages,
    config={"callbacks": [callback]}
)
```

### Example 2: Helper Function
```python
from backend.callbacks import attach_token_tracking

def track_my_agent(config):
    return attach_token_tracking(config, agent_name="my_agent")

# Use it
config = track_my_agent(config)
result = await agent.ainvoke(input_data, config)
```

### Example 3: Manual Tracking
```python
from backend.services.token_monitoring import token_monitor

# After API call
await token_monitor.track_usage(
    user_id="user@example.com",
    thread_id="conv-123",
    model="gpt-4o",
    input_tokens=100,
    output_tokens=200,
    agent_name="my_agent"
)
```

## 🚀 Production Checklist

- [ ] Update model pricing in `token_monitoring.py`
- [ ] Add token tracking to all agent calls
- [ ] Set up budget monitoring alerts
- [ ] Create dashboard for cost visualization
- [ ] Schedule regular cost reports
- [ ] Implement rate limiting if needed
- [ ] Set up cost alerts in Application Insights

## 📚 Documentation

- **Full Guide**: `backend/services/TOKENMONITORING_USAGE.md`
- **Complete README**: `TOKEN_MONITORING_README.md`
- **Examples**: `backend/examples/token_monitoring_example.py`
- **API Docs**: `http://localhost:8000/docs`

## ⚙️ Architecture

```
┌──────────────┐
│ Agent Call   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ TokenTrackingCallback    │ ← Captures tokens automatically
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ TokenMonitoringService   │ ← Calculates cost & stores
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Cosmos DB (token_usage)  │ ← Persistent storage
└──────────────────────────┘
       │
       ▼
┌──────────────────────────┐
│ REST API Endpoints       │ ← Query & analyze
└──────────────────────────┘
```

## 💡 Pro Tips

1. **Always use callbacks** - Easiest integration
2. **Check costs regularly** - Set up daily/weekly checks
3. **Use cost-appropriate models** - gpt-4o-mini for simple tasks
4. **Monitor trends** - Identify unusual patterns
5. **Set budgets** - Implement checks before expensive operations

## 🎉 That's It!

You're now tracking tokens! Start with:

```python
config = attach_token_tracking(config, agent_name="my_agent")
```

Check usage:

```bash
curl http://localhost:8000/token-usage/user/user@example.com
```

Done! 🚀





