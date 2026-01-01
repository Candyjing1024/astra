# Microsoft ASTRA: End-to-End Implementation Guide

**Version**: 4.0 - Unified Guide
**Last Updated**: September 15, 2025

---

## 1. Introduction: What is ASTRA Core?

ASTRA Core is a reusable, enterprise-grade template for building domain-specific AI applications using sophisticated multi-agent systems. It provides a complete, production-ready foundation that can be customized for any business use case, enabling rapid development and deployment of AI-powered solutions on Microsoft Azure.

This template includes:
- **Backend**: A robust FastAPI server with LangGraph for multi-agent orchestration.
- **Frontend**: A modern React application with CopilotKit for a rich, conversational user experience, and an alternative Chainlit interface.
- **Infrastructure**: Azure Bicep templates for repeatable, secure, and scalable infrastructure as code.
- **Documentation**: This comprehensive guide for customization, deployment, and maintenance.

## 2. Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker Desktop
- Azure CLI
- An Azure subscription with access to Azure OpenAI, AI Search, and other required services.

### Local Development Setup

1.  **Clone the Repository**:
    ```bash
    git clone <your-astra-core-repo>
    cd astra_core
    ```

2.  **Configure Environment**:
    - Create a `.env` file in the `astra_core/backend` directory.
    - Populate it with your Azure service credentials as outlined in the "Environment Variables" section below.

3.  **Install Dependencies**:
    ```bash
    # Backend
    cd backend
    pip install -r requirements.txt

    # Frontend (React App)
    cd ../frontend/agui
    npm install

    # CopilotKit Runtime Service  
    cd copilot-runtime-service
    npm install
    ```

4.  **Run the Application**:
    ```bash
    # Start Backend Server (from astra_core/backend)
    python run.py

    # Start Frontend Development Server (from astra_core/frontend/agui)
    npm run dev

    # Start CopilotKit Runtime (from astra_core/frontend/agui/copilot-runtime-service)
    cd copilot-runtime-service
    npm run dev
    ```

5.  **Access the Application**:
    - **React App**: `http://localhost:3001`
    - **API Docs**: `http://localhost:8000/docs`

## 3. ASTRA Architecture

### 3.1. Multi-Agent System

ASTRA implements a proven multi-agent pattern for robust and scalable AI solutions:

```
Domain Supervisor
├── Domain Analysis Agent (RAG + Knowledge Base)
└── Research Agent (Internet Search + Real-time Data)
```

-   **Domain Supervisor**: The central orchestrator that manages conversation flow, routes user queries to the appropriate specialist agent, and synthesizes responses.
-   **Domain Agent**: The core expert responsible for in-depth analysis using a private knowledge base via Retrieval-Augmented Generation (RAG).
-   **Research Agent**: Gathers real-time information from the internet or external APIs to supplement the domain agent's knowledge.

### 3.2. Technology Stack

-   **Backend**: FastAPI, LangGraph, Azure OpenAI, Azure AI Search
-   **Frontend**: React 19, TypeScript, TanStack Router, CopilotKit, Material-UI, Tailwind CSS
-   **Infrastructure**: Azure Bicep
-   **Database**: Azure Cosmos DB (for conversation persistence)
-   **Security**: Azure Key Vault and Managed Identities

### 3.3. Standard Folder Structure

All ASTRA use cases must adhere to this standardized structure for consistency and maintainability.

```
astra_core/
├── backend/
│   ├── agents/          # Generic agent templates and prompts
│   ├── tools/           # RAG and internet search tools
│   ├── services/        # AI Search indexing and other services
│   ├── config.py        # Central configuration for the backend
│   └── run.py           # FastAPI server entry point
├── frontend/
│   ├── agui/            # Main React application with CopilotKit integration
│   │   └── copilot-runtime-service/  # CopilotKit backend service
│   └── chainlit/        # Alternative lightweight chat interface
├── deploy/              # Azure deployment templates (Bicep)
├── tests/               # Unit, integration, and E2E tests
├── .env.example         # Template for environment variables
├── CUSTOMIZATION.md     # Detailed customization guide
├── DEPLOYMENT.md        # Detailed deployment guide
└── README.md            # Project overview
```

## 4. Building a New Use Case: A Step-by-Step Guide

This section walks through the process of transforming the ASTRA Core template into a specialized AI application for your domain.

### Step 1: Domain Definition and Planning

Before writing any code, clearly define your use case.

-   **Domain Name**: e.g., "Financial Portfolio Management"
-   **Core Capabilities**: e.g., Portfolio analysis, market research, risk assessment.
-   **Knowledge Sources**: e.g., Financial reports, market data APIs, research papers.
-   **User Personas**: e.g., Portfolio managers, financial analysts.

### Step 2: Backend Configuration

1.  **Update `backend/config.py`**: Replace placeholder values with your domain-specific names.
    ```python
    # FROM (template):
    domain_index_name = "your-domain-index"
    domain_name = "your-domain"

    # TO (your domain):
    domain_index_name = "portfolio-analysis-index"
    domain_name = "Portfolio Management"
    ```

2.  **Set Environment Variables**: Create a `.env` file in `astra_core/backend` and populate it with your Azure credentials. For production, these should be stored in Azure Key Vault.
    ```env
    AZURE_OPENAI_ENDPOINT=https://your-service.openai.azure.com/
    AZURE_OPENAI_API_KEY=your-api-key
    AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
    AZURE_SEARCH_API_KEY=your-search-key
    COSMOS_DB_ENDPOINT=your-cosmos-endpoint # Optional
    ```

### Step 3: Agent Customization

1.  **Create Domain-Specific Agents**: Copy the generic agent templates to create your own.
    ```bash
    # In astra_core/backend/agents/
    cp domain_agent.py portfolio_agent.py
    cp prompts/domain_agent.prompty prompts/portfolio_agent.prompty
    ```

2.  **Customize Agent Logic**: In `portfolio_agent.py`, update the agent's name, description, and capabilities.
    ```python
    name="portfolio_expert"
    description="Expert in portfolio analysis and investment recommendations"
    ```

3.  **Update Domain Supervisor**: In `domain_supervisor.py`, import and include your new agents in the orchestration graph.
    ```python
    # FROM:
    from .domain_agent import domain_agent
    agents = [domain_agent, research_agent]

    # TO:
    from .portfolio_agent import portfolio_agent
    agents = [portfolio_agent, research_agent]
    ```

### Step 4: Prompt Engineering

Modify the `.prompty` files to give your agents their unique personality and expertise.

-   **Supervisor Prompt (`prompts/domain_supervisor.prompty`)**: Update the supervisor's description and routing logic to reflect your domain.
-   **Domain Agent Prompt (`prompts/portfolio_agent.prompty`)**: Define the agent's persona, expertise, and constraints. This is where you turn a generic agent into a specialist.

### Step 5: RAG and Knowledge Base Setup

1.  **Customize RAG Tool (`backend/tools/rag_tool.py`)**:
    - Point the `domain_search_retrieval` function to your `domain_index_name` from `config.py`.
    - Customize the search fields and logic based on your data schema.

2.  **Set Up AI Search Indexer (`backend/services/ai_search_indexer.py`)**:
    - Define the schema for your Azure AI Search index, including domain-specific fields.
    - Use the provided scripts to upload your documents to the search index.

### Step 6: Frontend Customization

1.  **Branding and Content (`frontend/agui/src/`)**:
    - Update `App.tsx` and other components with your application's title and branding.
    - Replace generic dashboard components in `src/pages/DomainDashboard.tsx` with widgets relevant to your domain (e.g., portfolio value, risk indicators).

2.  **Styling (`frontend/agui/src/styles.css`)**:
    - Update the color scheme, fonts, and other styles to match your brand identity.

### Step 7: CopilotKit Integration

1.  **Update CopilotKit Provider (`frontend/agui/src/components/CopilotProvider.tsx`)**:
    - Ensure the `agent` property points to your main supervisor agent (e.g., `domain_supervisor`).

2.  **Customize Chat Interface (`frontend/agui/src/components/DomainChat.tsx`)**:
    - Update the title and placeholder text to guide users on how to interact with your AI assistant.

## 5. Deployment to Azure

### Step 1: Deploy Infrastructure with Bicep

ASTRA Core uses Bicep for repeatable and secure infrastructure deployment.

1.  **Update Parameters**: Edit `deploy/parameters/dev/main.bicepparam` to define your resource names, location, and environment prefix.
    ```bicep
    param prefix = 'portfolio-mgmt'
    param domainName = 'Portfolio Management'
    param searchIndexName = 'portfolio-docs'
    ```

2.  **Deploy**: Run the following Azure CLI commands:
    ```bash
    az login
    az account set --subscription "Your Subscription Name"
    az group create --name "portfolio-mgmt-rg" --location "East US"

    cd deploy
    az deployment group create \
      --resource-group "portfolio-mgmt-rg" \
      --template-file main.bicep \
      --parameters @parameters/dev/main.bicepparam
    ```

### Step 2: Application Deployment

You can deploy the backend and frontend using Azure App Service, Azure Container Apps, or Azure Static Web Apps.

**Example: Deploying Backend to App Service**
```bash
cd backend
# Ensure requirements.txt is up to date
pip freeze > requirements.txt

az webapp deploy \
  --resource-group "portfolio-mgmt-rg" \
  --name "portfolio-mgmt-backend" \
  --src-path . \
  --type zip
```

### Step 3: Security Configuration

-   **Use Azure Key Vault**: Store all secrets (API keys, connection strings) in Azure Key Vault.
-   **Enable Managed Identity**: Assign a managed identity to your App Service or Container App and grant it `get` and `list` permissions on secrets in your Key Vault.
-   **Update App Configuration**: Configure your application to read secrets from Key Vault using the managed identity.

### Step 4: Monitoring and Logging

-   **Application Insights**: The Bicep templates can deploy Application Insights. Configure your application with the connection string to enable end-to-end monitoring, logging, and performance tracking.
-   **Log Analytics**: Set up a Log Analytics workspace to query logs and create alerts for critical events like high error rates or performance degradation.

## 6. Testing and Validation

A comprehensive testing strategy is crucial for a production-ready application.

-   **Backend Testing**: Use `pytest` to run unit and integration tests. Test API endpoints directly.
-   **Frontend Testing**: Use a framework like Jest or Vitest to test React components.
-   **End-to-End Testing**: Simulate full user journeys, from login to interacting with the AI and viewing results on the dashboard.
-   **Load Testing**: Use Azure Load Testing to ensure your application can handle concurrent users.

## 7. Advanced Customization

### Adding a New Tool

1.  **Create the Tool**: In a file under `backend/tools/`, define your function and decorate it with `@tool`.
    ```python
    # backend/tools/portfolio_tools.py
    from langchain_core.tools import tool

    @tool
    def calculate_sharpe_ratio(returns: list[float]) -> float:
        """Calculates the Sharpe ratio for a portfolio."""
        # ... implementation ...
    ```
2.  **Register with an Agent**: In the agent's configuration file, import the tool and add it to the `tools` list.

### Database Integration

1.  **Define Models**: Create your data models using a library like SQLAlchemy.
2.  **Create Database Tools**: Build tools that allow agents to interact with the database (e.g., `get_portfolio_data`, `update_trade_log`).
3.  **Register Tools**: Add the new database tools to the relevant agents.

## 8. Troubleshooting

-   **Key Vault Access Denied**: Ensure the managed identity of your application has the correct access policies on the Key Vault.
-   **OpenAI API Errors**: Verify that the correct model deployment name and API version are configured.
-   **Log Analysis**: Use `az webapp log tail` or Application Insights to inspect real-time application logs for errors.

---

This guide provides a complete blueprint for building, customizing, and deploying a production-grade AI application with Microsoft ASTRA. For further details, refer to the specific documentation files in the repository.