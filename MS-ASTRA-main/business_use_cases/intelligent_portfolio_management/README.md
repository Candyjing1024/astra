# Intelligent Portfolio Management

An AI-powered portfolio management and investment advisory business use case built on the Microsoft ASTRA framework.

## Overview

This business use case demonstrates how AI agents can provide intelligent portfolio management services including:

- **Portfolio Analysis**: Real-time analysis of portfolio performance and composition
- **Market Research**: AI-powered market intelligence and trend analysis  
- **Investment Recommendations**: Personalized investment suggestions based on risk tolerance
- **Risk Assessment**: Comprehensive risk analysis and mitigation strategies
- **Performance Tracking**: Detailed portfolio performance metrics and reporting

## Architecture

This use case follows the standardized ASTRA business use case structure:

```
intelligent_portfolio_management/
├── backend/                    # Python backend with AI agents
├── frontend/                   # Frontend applications
│   ├── chainlit/              # Chainlit chat interface
│   └── agui/                  # Advanced React GUI
├── services/                   # Shared services
├── modules/                    # Reusable modules
│   └── evaluation/            # Testing and evaluation
├── deploy/                     # Deployment templates
├── .env.example               # Environment configuration
└── README.md                  # This file
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- Azure subscription with access to:
  - Azure OpenAI
  - Azure Key Vault
  - Azure Cosmos DB
  - Azure AI Search

### Backend Setup

1. **Configure Environment**
   ```bash
   cd backend
   cp ../.env.example .env
   # Edit .env with your Azure credentials
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Backend Server**
   ```bash
   python main.py
   ```

### Frontend Setup

#### Chainlit Interface

1. **Navigate to Chainlit Directory**
   ```bash
   cd frontend/chainlit
   ```

2. **Install Chainlit**
   ```bash
   pip install chainlit
   ```

3. **Run Chainlit App**
   ```bash
   chainlit run chainlit_run.py
   ```

#### Advanced GUI (React)

1. **Navigate to AGUI Directory**
   ```bash
   cd frontend/agui
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

## Features

### AI Agents

- **Portfolio Supervisor**: Main orchestrator for portfolio management tasks
- **Market Research Agent**: Analyzes market conditions and trends
- **Portfolio Analyzer Agent**: Evaluates portfolio performance and composition
- **Risk Assessment Agent**: Identifies and quantifies investment risks

### Frontend Applications

- **Chainlit Interface**: Conversational AI interface for natural language portfolio queries
- **Advanced GUI**: Rich dashboard with charts, analytics, and interactive portfolio management

### Services

- **Market Data Service**: Real-time market data integration
- **Portfolio Analytics Service**: Advanced portfolio performance calculations
- **Risk Management Service**: Risk assessment and monitoring

## Usage Examples

### Portfolio Analysis
```
User: "How is my portfolio performing this quarter?"
AI: "Your portfolio has gained 8.5% this quarter, outperforming the S&P 500 by 2.1%. 
     The technology sector allocation (35%) has been the primary driver of returns."
```

### Investment Recommendations
```
User: "I want to diversify my portfolio with bonds. What do you recommend?"
AI: "Based on your risk profile and current allocation, I recommend adding 15-20% 
     in investment-grade corporate bonds. Here are three specific bond funds..."
```

### Risk Assessment
```
User: "What are the main risks in my current portfolio?"
AI: "I've identified three key risks: 1) High concentration in tech stocks (40%), 
     2) Low international diversification (5%), 3) No inflation protection assets."
```

## Development

### Adding New Agents

1. Create agent file in `backend/agents/`
2. Add prompts in `backend/agents/prompts/`
3. Register with supervisor in `backend/agents/portfolio_supervisor.py`

### Adding New Services

1. Create service file in `services/`
2. Add initialization in `services/__init__.py`
3. Import in backend as needed

### Frontend Customization

- **Chainlit**: Modify `frontend/chainlit/chainlit_run.py`
- **React GUI**: Update components in `frontend/agui/src/`

## Deployment

### Azure Deployment

1. **Configure Bicep Parameters**
   ```bash
   cd deploy
   cp parameters/example.bicepparam parameters/production.bicepparam
   # Edit parameters for your environment
   ```

2. **Deploy Infrastructure**
   ```bash
   az deployment group create \
     --resource-group your-rg \
     --template-file main.bicep \
     --parameters @parameters/production.bicepparam
   ```

### Local Development

Use the provided Docker configuration for local development:

```bash
docker-compose up -d
```

## Testing

### Unit Tests
```bash
cd modules/evaluation
python -m pytest tests/
```

### Integration Tests
```bash
python -m pytest backend/tests/
```

### Frontend Tests
```bash
cd frontend/agui
npm test
```

## Configuration

Key configuration options in `.env`:

- `KEY_VAULT_NAME`: Azure Key Vault for secrets
- `AZURE_OPENAI_API_VERSION`: OpenAI API version
- `PORTFOLIO_UPDATE_INTERVAL`: How often to refresh portfolio data
- `RISK_THRESHOLD`: Default risk tolerance threshold

## Contributing

1. Follow the ASTRA development guidelines
2. Use the standardized folder structure
3. Add tests for new features
4. Update documentation

## License

This project is part of Microsoft ASTRA and follows Microsoft's open source guidelines.

## Support

For support and questions:
- Create an issue in the repository
- Consult the ASTRA documentation
- Contact the development team

---

**Last Updated**: September 12, 2025  
**Version**: 1.0.0  
**ASTRA Framework**: Compatible
