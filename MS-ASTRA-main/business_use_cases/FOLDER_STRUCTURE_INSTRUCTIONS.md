# Microsoft ASTRA Business Use Cases - Implementation Guide

## 🎯 Overview
This document defines the standardized folder structure and implementation guidelines for all business use cases within the Microsoft ASTRA framework. It provides proven architectural patterns and best practices for rapid development of production-ready AI-powered applications.

## 🏗️ Standard Folder Structure

Each business use case must follow this structure:

```
business_use_cases/
└── [use_case_name]/
    ├── backend/                              # Complete ASTRA backend infrastructure
    │   ├── __init__.py
    │   ├── main.py                          # FastAPI application with CopilotKit integration
    │   ├── config.py                        # Use-case specific configurations
    │   ├── utils.py                         # Utility functions and helpers
    │   ├── run.py                           # FastAPI server runner
    │   ├── chainlit_run.py                  # Chainlit application runner
    │   ├── agents/                          # AI agents and orchestration
    │   │   ├── __init__.py
    │   │   ├── [domain]_agent.py            # Primary domain-specific agent
    │   │   ├── research_agent.py            # Internet search and research agent
    │   │   ├── supervisor.py                # Multi-agent supervisor
    │   │   └── prompts/                     # Agent prompt templates
    │   │       ├── __init__.py
    │   │       ├── [domain]_agent.prompty   # Domain analysis prompts
    │   │       ├── research_agent.prompty   # Research prompts
    │   │       └── supervisor.prompty       # Orchestration prompts
    │   ├── tools/                           # Agent tools and capabilities
    │   │   ├── __init__.py
    │   │   ├── internet_tool.py             # Internet search functionality
    │   │   ├── rag_tool.py                  # Domain-specific knowledge retrieval
    │   │   └── [custom_tools].py            # Use-case specific tools
    │   └── services/                        # Backend services and integrations
    │       ├── __init__.py
    │       ├── ai_search_indexer.py         # Azure AI Search indexer
    │       └── [additional_services].py     # Other service integrations
    ├── frontend/                            # Modern React-based interface
    │   ├── client/                          # React application
    │   │   ├── package.json                 # Dependencies (CopilotKit, MUI, Tailwind)
    │   │   ├── index.html
    │   │   ├── vite.config.js
    │   │   ├── src/
    │   │   │   ├── routes/                  # Application routing
    │   │   │   │   ├── __root.tsx           # Root layout
    │   │   │   │   ├── index.tsx            # Welcome/landing page
    │   │   │   │   ├── chat.tsx             # AI chat interface
    │   │   │   │   ├── dashboard.tsx        # Data dashboard
    │   │   │   │   └── insights.tsx         # Analytics page
    │   │   │   ├── pages/                   # Page implementations
    │   │   │   ├── components/              # Reusable UI components
    │   │   │   ├── hooks/                   # Custom React hooks
    │   │   │   ├── utils/                   # Frontend utilities
    │   │   │   └── main.tsx                 # Application entry point
    │   │   └── public/                      # Static assets
    │   └── copilot-runtime-service/         # CopilotKit integration
    │       ├── server.ts                    # Runtime service
    │       └── package.json
    ├── tests/                               # Testing framework
    │   ├── test_units.py                    # Unit tests
    │   ├── test_integration.py              # Integration tests
    │   ├── test_e2e.py                      # End-to-end tests
    │   └── validate.py                      # System validation
    ├── deploy/                              # Deployment configuration
    │   ├── main.bicep
    │   ├── parameters/
    │   └── modules/
    ├── README.md                            # Use case documentation
    ├── .env.example                         # Environment template
    └── __init__.py
```

## 🧠 Multi-Agent Architecture

Each business use case should implement this proven pattern:

### Agent Structure
```
Domain Supervisor
├── Domain Analysis Agent (RAG + Knowledge Base)
└── Research Agent (Internet Search + Real-time Data)
```

### Agent Responsibilities
- **Supervisor**: Orchestrates workflows, manages conversation flow, routes queries
- **Domain Agent**: Specialized analysis using domain knowledge and RAG retrieval
- **Research Agent**: Real-time information gathering via internet search and external APIs
- **Pattern**: All agents use ReAct pattern with tool integration
- **State**: Conversation persistence via Cosmos DB checkpointing

## 🎨 Technology Stack

### Backend
- **Framework**: FastAPI with Microsoft ASTRA integration
- **Agents**: LangGraph with create_react_agent pattern
- **AI**: Azure OpenAI for reasoning and generation
- **Search**: Azure AI Search for domain knowledge retrieval
- **Storage**: Cosmos DB for conversation state
- **Integration**: CopilotKit for frontend communication

### Frontend
- **Framework**: React 19 with TanStack Router
- **UI**: Material-UI + Tailwind CSS
- **AI Integration**: CopilotKit for conversational interface
- **Build**: Vite + TypeScript
- **Styling**: Responsive design with modern components

### Infrastructure
- **Cloud**: Microsoft Azure services
- **Deployment**: Bicep templates for infrastructure as code
- **Monitoring**: Application Insights for observability
- **Security**: Azure AD authentication and RBAC

## 🛠️ Implementation Process

### Phase 1: Backend Setup
1. **Foundation**: Copy complete backend from `astra_core/backend`
2. **Agents**: Implement domain supervisor + domain agent + research agent
3. **Tools**: Configure RAG retrieval and internet search tools  
4. **Prompts**: Develop domain-specific prompts for each agent
5. **Configuration**: Set up Azure AI Search index and environment variables

### Phase 2: Frontend Development  
1. **Initialize**: Create React app with Vite + TypeScript + TanStack Router
2. **UI Framework**: Install and configure Material-UI + Tailwind CSS
3. **CopilotKit**: Set up AI integration with runtime service
4. **Pages**: Implement welcome, chat, dashboard, and insights pages
5. **Integration**: Connect frontend to backend agents via CopilotKit

### Phase 3: Testing & Deployment
1. **Testing**: Unit, integration, and end-to-end test implementation
2. **Validation**: System validation and performance testing
3. **Deployment**: Configure Azure infrastructure with Bicep templates
4. **Documentation**: Complete implementation and user documentation

## 📝 Key Configuration

### Environment Variables
```bash
# Azure Services
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
AZURE_SEARCH_SERVICE_ENDPOINT=your_search_endpoint
AZURE_SEARCH_INDEX_KEY=your_search_key
AZURE_COSMOSDB_CONNECTION_STRING=your_cosmos_connection

# Domain Specific
DOMAIN_INDEX_NAME=index-your-use-case
DOMAIN_AGENT_ID=your_agent_id

# CopilotKit
COPILOTKIT_RUNTIME_URL=http://localhost:4000
```

### Import Path Structure
```python
# Correct import paths after flattened structure
from backend.agents.domain_agent import DomainAgent
from backend.tools.rag_tool import search_knowledge_base
from backend.tools.internet_tool import search_internet
from backend.utils import helper_functions
from backend.config import get_settings
```

## 🔄 Migration Guidelines

### From Legacy Structure
1. **Flatten Backend**: Remove intermediate `app/` folder
   - Move `backend/app/agents/` → `backend/agents/`
   - Move `backend/app/agents/tools/` → `backend/tools/`
   - Move `backend/app/utils.py` → `backend/utils.py`

2. **Update Imports**: Change all import statements
   - `from backend.app.tools` → `from backend.tools`
   - `from backend.app.agents` → `from backend.agents`

3. **Agent Simplification**: Remove legacy agents, keep only:
   - Domain-specific supervisor
   - Primary domain agent  
   - Research/internet agent

## 🧪 Testing Framework

### Required Tests
- **Unit Tests**: Individual component validation
- **Integration Tests**: Multi-agent workflow testing
- **End-to-End Tests**: Complete user journey validation
- **Performance Tests**: Load and response time testing

### Validation Checklist
- ✅ Folder structure matches standard
- ✅ All agents functional and responsive
- ✅ Frontend-backend integration working
- ✅ CopilotKit conversation flow operational
- ✅ Dashboard displays domain data correctly
- ✅ Environment configuration complete

## 📚 Reference Implementation

The `intelligent_portfolio_management/` use case serves as the reference implementation demonstrating:
- Multi-agent architecture with supervisor pattern
- Modern React frontend with CopilotKit integration  
- Complete backend with flattened structure
- Comprehensive testing and validation framework

## 🎯 Benefits

- **Consistency**: Standardized structure across all use cases
- **Rapid Development**: Proven patterns reduce development time
- **Scalability**: Easy to extend and modify for new requirements
- **Maintainability**: Clear separation of concerns and documentation
- **Production Ready**: Built-in security, performance, and monitoring

---

**Version**: 4.0 - Streamlined and generic implementation guide  
**Last Updated**: September 15, 2025

---

*Standardized blueprint for building production-ready AI-powered business applications within the Microsoft ASTRA framework.*