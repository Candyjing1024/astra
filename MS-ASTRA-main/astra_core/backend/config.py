"""
This module serves as the central configuration hub for the agentic framework,
managing all external service connections, credentials, and application settings.

TEMPLATE FILE: This is a generic template for business use case configuration.
Replace placeholder values with your specific domain requirements.

Key Features:
    1. Azure Key Vault Integration: Securely retrieves all sensitive credentials and configuration
    2. Azure OpenAI Configuration: Sets up chat completion models and embedding services
    3. Azure AI Search Setup: Configures search endpoints and credentials for RAG functionality
    4. Cosmos DB Configuration: Manages database connections for conversation persistence
    5. Environment-Based Settings: Uses environment variables with sensible defaults

Security:
All sensitive information (API keys, endpoints, connection strings) is stored in
Azure Key Vault and retrieved using DefaultAzureCredential for secure authentication.
No hardcoded secrets are present in the codebase.

Configuration Areas:
- Azure OpenAI: Chat completion models, embeddings, API versions
- Azure AI Search: Search endpoints, credentials, index configurations
- Cosmos DB: Database connections for checkpointing and conversation storage
- Application Insights: Telemetry and logging configuration
- Key Vault: Centralized secret management

Usage:
This module is imported by other components to access configured services and
credentials. It initializes all necessary Azure service clients and provides
them as module-level variables for easy consumption throughout the application.

CUSTOMIZATION:
1. Update KEY_VAULT_NAME to your Key Vault instance
2. Configure domain-specific index names and search fields
3. Adjust model parameters for your use case requirements
4. Set appropriate database container names
"""

from dotenv import load_dotenv
import os
from azure.keyvault.secrets import SecretClient # type: ignore
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential # type: ignore
from azure.identity import ClientSecretCredential

# Load environment variables
load_dotenv()

# Basic Configuration - UPDATE THESE FOR YOUR DEPLOYMENT
CONFIG = {
    "KEY_VAULT_NAME": os.getenv("KEY_VAULT_NAME", "your-key-vault-name"),
    "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    "EMBEDDING_VECTOR_DIMENSION": os.getenv("EMBEDDING_VECTOR_DIMENSION", "1536")
}

keyVaultName = CONFIG["KEY_VAULT_NAME"]
keyVaultURL = f"https://{keyVaultName}.vault.azure.net"
azureOpenAIVersion = CONFIG["AZURE_OPENAI_API_VERSION"]
embeddingVectorDimension = int(CONFIG["EMBEDDING_VECTOR_DIMENSION"])

# Azure Authentication
credential = DefaultAzureCredential()
client = SecretClient(vault_url=keyVaultURL, credential=credential)

# Azure OpenAI Configuration
azure_openai_endpoint = client.get_secret(name="azure-openai-endpoint").value
azure_openai_api_key = client.get_secret(name="azure-openai-api-key").value
azure_openai_api_version = azureOpenAIVersion

# Embedding Configuration
azure_openai_embedding_deployment = client.get_secret(name="azure-openai-embedding-deployment").value
azure_openai_embedding_model = client.get_secret(name="azure-openai-embedding-model").value
embedding_vector_dimension = embeddingVectorDimension

# Azure AI Search Configuration
search_credential = AzureKeyCredential(client.get_secret(name="azure-search-key").value)
search_endpoint = client.get_secret(name="azure-search-endpoint").value

# Chat Completion Model Configuration - ADJUST FOR YOUR USE CASE
chat_completion_model_name = "gpt-4o"
chat_completion_model_temperature = 0.2
chat_completion_model_max_tokens = 1000

# Cosmos DB Configuration
container_conversations_name = "conversations"
container_checkpoint_name = "checkpoints"
container_checkpoint_writes_name = "checkpoint_writes"
database_name = "agentic-framework"
cosmosdb_endpoint = client.get_secret(name="cosmosdb-endpoint").value
cosmosdb_account_key = client.get_secret(name="cosmosdb-account-key").value
cosmosdb_credential = cosmosdb_account_key

# Application Insights Configuration
app_insight_connection_string = client.get_secret(name="app-insights-connection-string").value

# Bing Search Configuration (for internet search capabilities)
ai_foundry_project_endpoint = client.get_secret(name="ai-foundry-project-endpoint").value
ai_foundry_bing_agent_name = "your-agent-name"

# DOMAIN-SPECIFIC CONFIGURATION - CUSTOMIZE FOR YOUR USE CASE
# Replace these placeholder configurations with your domain-specific settings

# Primary Domain Index Configuration
# Example: For portfolio management, change "domain" to "portfolio_management"
domain_index_name = "index-your-domain"
domain_semantic_configuration_name = "semantic-config"
domain_search_nearest_neighbour = 50  # Adjust based on your knowledge base size
domain_search_field_name = "content_vector"  # Your vector field name
domain_scoring_profile = "default-scoring-profile"

# Secondary Index Configuration (if needed)
# Example: For market research, analytics, etc.
secondary_index_name = "index-your-secondary-domain"
secondary_semantic_configuration_name = "secondary-semantic-config"
secondary_search_nearest_neighbour = 25
secondary_search_field_name = "content_vector"

# TEMPLATE EXAMPLE CONFIGURATIONS - REMOVE OR REPLACE WITH YOUR DOMAIN
# These are examples that should be replaced with your specific use case configurations

# Example 1: Knowledge Base Index
knowledge_base_index_name = "index-knowledge-base"
knowledge_base_semantic_configuration_name = "knowledge-semantic-config"
knowledge_base_search_nearest_neighbour = 30
knowledge_base_search_field_name = "knowledge_vector"

# Example 2: Analytics Index
analytics_index_name = "index-analytics"
analytics_semantic_configuration_name = "analytics-semantic-config"
analytics_search_nearest_neighbour = 20
analytics_search_field_name = "analytics_vector"

# Resource Configuration
resource_id = client.get_secret(name="azure-resource-id").value
