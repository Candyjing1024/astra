# Token Monitoring System - File Structure

## 📁 Complete File Tree

```
astra_core/
│
├── 📄 TOKEN_MONITORING_IMPLEMENTATION_SUMMARY.md    ⭐ START HERE
├── 📄 TOKEN_MONITORING_README.md                    (Complete guide)
├── 📄 QUICK_START_TOKEN_MONITORING.md               (Quick reference)
│
└── backend/
    │
    ├── services/
    │   ├── token_monitoring.py                      🔥 CORE SERVICE
    │   └── TOKENMONITORING_USAGE.md                 (Detailed docs)
    │
    ├── callbacks/
    │   ├── __init__.py
    │   └── token_tracking_callback.py               🔥 LANGCHAIN CALLBACK
    │
    ├── examples/
    │   ├── __init__.py
    │   └── token_monitoring_example.py              🔥 PRACTICAL EXAMPLES
    │
    └── run.py                                        🔥 API ENDPOINTS (modified)
```

## 📋 File Descriptions

### 🎯 Start Here
**`TOKEN_MONITORING_IMPLEMENTATION_SUMMARY.md`** ⭐  
Complete overview of the entire implementation. Read this first!

### 🔥 Core Implementation Files

#### 1. `backend/services/token_monitoring.py` (550 lines)
**The main service for token tracking**

**Contains:**
- `TokenMonitoringService` class
- `TokenUsageRecord` model
- `TokenUsageStats` model
- `MODEL_PRICING` dictionary
- Cost calculation logic
- Cosmos DB integration
- Analytics methods

**Key Functions:**
```python
token_monitor.track_usage()         # Track API call
token_monitor.get_user_usage()      # Get user stats
token_monitor.get_thread_usage()    # Get thread stats
token_monitor.get_usage_by_model()  # Model breakdown
token_monitor.get_all_usage()       # Raw records
```

#### 2. `backend/callbacks/token_tracking_callback.py` (200 lines)
**LangChain callback handler for automatic tracking**

**Contains:**
- `TokenTrackingCallbackHandler` class
- `create_token_tracking_callback()` function
- `attach_token_tracking()` helper function

**Key Usage:**
```python
config = attach_token_tracking(config, agent_name="my_agent")
```

#### 3. `backend/run.py` (180 lines added)
**REST API endpoints for querying token usage**

**Added Endpoints:**
- `GET /token-usage/user/{user_id}`
- `GET /token-usage/thread/{thread_id}`
- `GET /token-usage/all`
- `GET /token-usage/by-model`

**Added Models:**
- `TokenUsageResponse`
- `TokenUsageRecordResponse`

#### 4. `backend/examples/token_monitoring_example.py` (450 lines)
**Practical, runnable examples**

**Contains 8 Examples:**
1. Basic manual tracking
2. Automatic callback tracking
3. Query user statistics
4. Budget monitoring
5. Cost analysis by model
6. Cost trend visualization
7. Retrieve raw records
8. Cost optimization recommendations

**Run it:**
```bash
python -m backend.examples.token_monitoring_example
```

### 📚 Documentation Files

#### 1. `TOKEN_MONITORING_IMPLEMENTATION_SUMMARY.md` ⭐
**Complete implementation overview**
- What was built
- How to use it
- File descriptions
- Quick start
- Examples

#### 2. `TOKEN_MONITORING_README.md`
**Comprehensive guide**
- Architecture overview
- Quick start
- API documentation
- Data models
- Use cases
- Configuration
- Benefits

#### 3. `QUICK_START_TOKEN_MONITORING.md`
**5-minute quick reference**
- Instant setup
- Common queries
- API endpoints
- Examples
- Production checklist

#### 4. `backend/services/TOKENMONITORING_USAGE.md`
**Detailed usage documentation**
- Architecture diagrams
- API reference
- Integration examples
- Best practices
- Troubleshooting
- Advanced features

### 🔧 Supporting Files

#### `backend/callbacks/__init__.py`
Package initialization for callbacks

**Exports:**
```python
from .token_tracking_callback import (
    TokenTrackingCallbackHandler,
    create_token_tracking_callback,
    attach_token_tracking
)
```

#### `backend/examples/__init__.py`
Package initialization for examples

---

## 🎯 How to Navigate

### If you want to...

**Get started quickly:**
1. Read: `QUICK_START_TOKEN_MONITORING.md`
2. Use: `attach_token_tracking()`

**Understand the full system:**
1. Read: `TOKEN_MONITORING_IMPLEMENTATION_SUMMARY.md`
2. Read: `TOKEN_MONITORING_README.md`

**See working examples:**
1. Run: `python -m backend.examples.token_monitoring_example`
2. Read: `backend/examples/token_monitoring_example.py`

**Learn the API:**
1. Read: `backend/services/TOKENMONITORING_USAGE.md`
2. Visit: `http://localhost:8000/docs`

**Modify the implementation:**
1. Edit: `backend/services/token_monitoring.py` (service)
2. Edit: `backend/callbacks/token_tracking_callback.py` (callback)
3. Edit: `backend/run.py` (API endpoints)

**Update pricing:**
1. Edit `MODEL_PRICING` in `backend/services/token_monitoring.py`

---

## 📊 File Statistics

| File | Lines | Type | Purpose |
|------|-------|------|---------|
| `token_monitoring.py` | 550 | Python | Core service |
| `token_tracking_callback.py` | 200 | Python | LangChain callback |
| `run.py` | +180 | Python | API endpoints |
| `token_monitoring_example.py` | 450 | Python | Examples |
| `TOKENMONITORING_USAGE.md` | 400 | Docs | Usage guide |
| `TOKEN_MONITORING_README.md` | 500 | Docs | Complete guide |
| `QUICK_START_TOKEN_MONITORING.md` | 300 | Docs | Quick reference |
| `TOKEN_MONITORING_IMPLEMENTATION_SUMMARY.md` | 400 | Docs | Overview |
| **TOTAL** | **~2,980** | - | - |

---

## 🚀 Quick Start Commands

### 1. Use Token Tracking
```python
from backend.callbacks import attach_token_tracking

config = attach_token_tracking(config, agent_name="my_agent")
result = await agent.ainvoke(input_data, config)
```

### 2. Query Usage (Python)
```python
from backend.services.token_monitoring import token_monitor

stats = await token_monitor.get_user_usage("user@example.com")
print(f"Cost: ${stats.total_cost:.2f}")
```

### 3. Query Usage (API)
```bash
curl http://localhost:8000/token-usage/user/user@example.com?days=30
```

### 4. Run Examples
```bash
python -m backend.examples.token_monitoring_example
```

### 5. View API Docs
```bash
# Start server, then visit:
http://localhost:8000/docs
```

---

## 🎓 Learning Path

### Beginner Path
1. Read `QUICK_START_TOKEN_MONITORING.md`
2. Copy-paste the quick start code
3. Run `token_monitoring_example.py`
4. Query your usage via API

### Intermediate Path
1. Read `TOKEN_MONITORING_README.md`
2. Understand the architecture
3. Integrate into your agents
4. Set up budget monitoring

### Advanced Path
1. Read `TOKENMONITORING_USAGE.md`
2. Customize `token_monitoring.py`
3. Build cost dashboards
4. Implement optimization strategies

---

## 💡 Key Features Per File

### `token_monitoring.py`
- ✅ Track token usage
- ✅ Calculate costs
- ✅ Store in Cosmos DB
- ✅ Query statistics
- ✅ Analyze trends

### `token_tracking_callback.py`
- ✅ LangChain integration
- ✅ Automatic capture
- ✅ Error-safe
- ✅ Non-blocking

### `run.py` (API endpoints)
- ✅ User statistics
- ✅ Thread statistics
- ✅ All records
- ✅ Model breakdown

### `token_monitoring_example.py`
- ✅ Manual tracking demo
- ✅ Callback tracking demo
- ✅ Budget monitoring
- ✅ Cost analysis
- ✅ Optimization tips

---

## 🔗 File Dependencies

```
token_monitoring.py
    ↓
    ├─→ Cosmos DB
    └─→ config.py

token_tracking_callback.py
    ↓
    ├─→ token_monitoring.py
    └─→ LangChain callbacks

run.py
    ↓
    ├─→ token_monitoring.py
    └─→ FastAPI

token_monitoring_example.py
    ↓
    ├─→ token_monitoring.py
    ├─→ token_tracking_callback.py
    └─→ utils.py
```

---

## 📞 Quick Reference

### Import Statements
```python
# For automatic tracking
from backend.callbacks import attach_token_tracking

# For manual tracking
from backend.services.token_monitoring import token_monitor

# For callback handler
from backend.callbacks import TokenTrackingCallbackHandler
```

### Essential Functions
```python
# Track usage
await token_monitor.track_usage(user_id, thread_id, model, input_tokens, output_tokens)

# Get stats
stats = await token_monitor.get_user_usage(user_id, days=30)

# Attach to config
config = attach_token_tracking(config, agent_name="my_agent")
```

### API Endpoints
```bash
GET /token-usage/user/{user_id}?days=30
GET /token-usage/thread/{thread_id}
GET /token-usage/all?days=7&limit=100
GET /token-usage/by-model?days=30
```

---

## ✅ Implementation Checklist

- [x] Core service implemented
- [x] Callback handler implemented
- [x] API endpoints added
- [x] Examples created
- [x] Documentation written
- [x] Quick start guide created
- [x] No linting errors
- [x] Production ready

---

## 🎉 You're All Set!

Everything is implemented and documented. Start with:

```python
config = attach_token_tracking(config, agent_name="my_agent")
```

For questions, check:
- `TOKEN_MONITORING_IMPLEMENTATION_SUMMARY.md` (overview)
- `QUICK_START_TOKEN_MONITORING.md` (quick reference)
- `TOKEN_MONITORING_README.md` (complete guide)
- `TOKENMONITORING_USAGE.md` (detailed docs)

**Happy tracking! 🚀**





