# ASTRA Core Template

**Generic Multi-Agent AI Framework Template**

ASTRA Core is a reusable template for building domain-specific AI applications using multi-agent systems. This template provides a complete foundation that can be customized for any business use case.

## 🚀 Quick Start

1. **Read the Guide**: Start with `deployment_instructions.md` for complete setup instructions
2. **Configure Backend**: Update `backend/config.py` with your Azure resources
3. **Install Dependencies**: Follow the installation steps in the deployment guide
4. **Customize Agents**: Modify agents and prompts for your domain
5. **Deploy**: Use the provided Bicep templates for Azure deployment

## 📁 Structure

```
astra_core/
├── backend/                  # Generic FastAPI backend with LangGraph agents
│   ├── agents/              # Domain supervisor + domain agent + research agent
│   ├── tools/               # RAG search and internet tools
│   ├── services/            # AI Search indexing service
│   └── config.py            # Configuration template
├── frontend/
│   ├── agui/                # React application with CopilotKit
│   └── chainlit/            # Alternative chat interface
├── deploy/                  # Azure Bicep templates
└── deployment_instructions.md  # Complete implementation guide
```

## 🎯 Key Features

- **Generic Template**: No customer-specific code - ready for any domain
- **Multi-Agent Architecture**: Supervisor + specialist + research agent pattern
- **Azure Native**: Full integration with Azure OpenAI, AI Search, Key Vault
- **Modern Frontend**: React with CopilotKit for conversational AI
- **Production Ready**: Complete deployment automation with Bicep

## 📚 Documentation

See `deployment_instructions.md` for the complete guide covering:
- Architecture overview
- Step-by-step customization
- Azure deployment procedures
- Testing and validation

## 🔧 This is a Template

**Important**: This is a template, not a ready-to-use application. You must customize it for your specific domain following the deployment instructions.

---

**Start here**: Open `deployment_instructions.md` to begin building your domain-specific AI application.