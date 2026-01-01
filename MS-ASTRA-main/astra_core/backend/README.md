# ASTRA Core Backend

**Generic Multi-Agent AI Backend Template**

This is the backend component of ASTRA Core, providing a FastAPI-based web server with LangGraph multi-agent orchestration and CopilotKit integration.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Azure subscription
- Azure OpenAI access
- Azure AI Search instance

### Installation

```bash
# Clone and navigate to backend
cd astra_core/backend

# Install dependencies
pip install -r requirements.txt

# Configure environment (see Configuration section)
# Edit config.py with your Azure resource details

# Start the server
python run.py
```

The server will start at `http://localhost:8000`

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## 🏗️ Architecture

### Multi-Agent System
- **Domain Supervisor**: Orchestrates agent routing and coordination
- **Domain Agent**: Handles domain-specific analysis and tasks  
- **Research Agent**: Performs internet research and information gathering

### Key Components
- **FastAPI Server** (`run.py`): RESTful API with CopilotKit integration
- **Agent Framework** (`agents/`): LangGraph-based multi-agent system
- **RAG Tools** (`tools/`): Retrieval-Augmented Generation capabilities
- **Services** (`services/`): AI Search indexing and data processing
- **Configuration** (`config.py`): Centralized configuration management

## 📁 Directory Structure

```
backend/
├── agents/                 # Agent implementations
│   ├── prompts/           # Agent prompt templates
│   ├── domain_supervisor.py
│   ├── domain_agent.py
│   ├── research_agent.py
│   └── supervisor_agents.py
├── tools/                 # Agent tools and utilities
│   ├── rag_tool.py       # RAG implementation
│   └── internet_tool.py  # Web search capabilities
├── services/              # External service integrations
│   └── ai_search_indexer.py
├── app/                   # Core application modules
│   ├── config.py         # Configuration management
│   ├── main.py           # Chainlit application (alternative)
│   └── utils.py          # Shared utilities
├── config.py             # Main configuration file
├── run.py               # FastAPI server entry point
└── requirements.txt     # Python dependencies
```

## ⚙️ Configuration

### 1. Azure Resources Setup

You need these Azure resources:
- Azure OpenAI service
- Azure AI Search service
- Azure Key Vault
- Azure Cosmos DB (optional, for conversation persistence)

### 2. Update Configuration

Edit `config.py` with your resource details:

```python
# Azure Key Vault
key_vault_name = "your-keyvault-name"

# Azure OpenAI
openai_service_name = "your-openai-service"
openai_model_name = "gpt-4o"

# Azure AI Search  
search_service_name = "your-search-service"
domain_index_name = "your-domain-index"

# Domain Configuration
domain_name = "Your Domain Name"
```

### 3. Environment Variables

Set up your `.env` file or Azure Key Vault:

```env
AZURE_OPENAI_ENDPOINT=https://your-service.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-search-key
```

## 🤖 Agent Customization

### Creating Domain-Specific Agents

1. **Copy Template Agent**:
```bash
cp agents/domain_agent.py agents/your_domain_agent.py
```

2. **Update Agent Configuration**:
```python
# In your_domain_agent.py
agent_name = "your_domain_expert"
agent_description = "Expert in your specific domain"
agent_capabilities = ["capability1", "capability2"]
```

3. **Update Prompts**:
```bash
cp agents/prompts/domain_agent.prompty agents/prompts/your_domain_agent.prompty
```

4. **Register Agent**:
```python
# In supervisor_agents.py
from .your_domain_agent import your_domain_agent
agents = [your_domain_agent, research_agent]
```

### Agent Development Best Practices

1. **Single Responsibility**: Each agent should have a clear, focused purpose
2. **Stateless Design**: Agents should not maintain state between calls
3. **Error Handling**: Implement robust error handling and fallbacks
4. **Testing**: Write unit tests for agent functionality
5. **Documentation**: Document agent capabilities and usage

## 🔍 RAG Implementation

### Setting Up Your Knowledge Base

1. **Prepare Documents**:
```python
documents = [
    {
        "id": "doc1", 
        "title": "Document Title",
        "content": "Document content...",
        "metadata": {"category": "type1"}
    }
]
```

2. **Create Search Index**:
```python
from services.ai_search_indexer import DomainIndexer

indexer = DomainIndexer()
indexer.create_index()
indexer.upload_documents(documents)
```

3. **Configure RAG Tool**:
```python
# In tools/rag_tool.py
@tool
def domain_search_retrieval(query: str) -> str:
    """Search your domain-specific knowledge base."""
    # Customize search logic for your domain
```

## 🌐 API Endpoints

### Core Endpoints

- `POST /query`: Process user queries through the agent system
- `GET /conversations`: List conversation threads
- `POST /conversations`: Create new conversation
- `GET /conversations/{id}`: Get conversation details
- `DELETE /conversations/{id}`: Delete conversation

### CopilotKit Integration

- `/copilotkit`: CopilotKit endpoint for frontend integration

### Health and Monitoring

- `GET /health`: Health check endpoint
- `GET /metrics`: Application metrics

## 🔧 Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
python run.py --reload

# Run tests
pytest

# Code formatting
black .
isort .
```

### Adding New Tools

1. **Create Tool Function**:
```python
# In tools/your_tool.py
from langchain.tools import tool

@tool
def your_custom_tool(input_param: str) -> str:
    """Description of what your tool does."""
    # Implementation here
    return result
```

2. **Register with Agent**:
```python
# In agents/your_agent.py
from tools.your_tool import your_custom_tool

agent = create_react_agent(
    model=chat_completion_model,
    tools=[existing_tools, your_custom_tool],
    # ... other config
)
```

### Database Integration

For conversation persistence:

```python
# Configure Cosmos DB checkpointer
from utils import checkpointer

# Agents automatically use the checkpointer
graph = agent.compile(checkpointer=checkpointer)
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=backend
```

### Integration Tests

```bash
# Test API endpoints
pytest tests/test_api.py

# Test agent workflows
pytest tests/test_workflows.py
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:8000
```

## 📊 Monitoring and Logging

### Application Insights Integration

```python
# Configure in config.py
application_insights_connection_string = "your-connection-string"
```

### Custom Logging

```python
from utils import logger

logger.info("Custom log message")
logger.error("Error occurred", extra={"context": data})
```

### Performance Monitoring

- Request/response times tracked automatically
- Agent execution times logged
- Database query performance monitored
- Memory and CPU usage tracked

## 🔐 Security

### Authentication and Authorization

```python
# Add authentication middleware
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Authentication logic
    pass
```

### Secret Management

- Use Azure Key Vault for production secrets
- Never commit secrets to version control
- Rotate secrets regularly

### Input Validation

```python
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    input: str
    
    @validator('input')
    def validate_input(cls, v):
        if len(v) > 1000:
            raise ValueError('Input too long')
        return v
```

## 🚀 Deployment

### Local Development
```bash
python run.py
```

### Docker Deployment
```bash
docker build -t astra-backend .
docker run -p 8000:8000 astra-backend
```

### Azure App Service
```bash
az webapp deploy --resource-group rg --name app-name --src-path .
```

## 🔧 Troubleshooting

### Common Issues

1. **Azure Key Vault Access**:
   - Verify managed identity is configured
   - Check Key Vault access policies
   - Ensure correct Key Vault name in config

2. **OpenAI API Errors**:
   - Verify API key and endpoint
   - Check model deployment status
   - Monitor rate limits and quotas

3. **Search Index Issues**:
   - Verify search service connection
   - Check index schema and data
   - Monitor search service capacity

### Debug Mode

```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python run.py
```

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Test agent endpoint
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"input": "test query"}'
```

## 📚 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure OpenAI Documentation](https://docs.microsoft.com/azure/cognitive-services/openai/)
- [CopilotKit Documentation](https://docs.copilotkit.ai/)

## 🤝 Contributing

1. Follow the template structure
2. Maintain generic, reusable patterns
3. Add comprehensive documentation
4. Include unit tests for new features
5. Update this README for significant changes