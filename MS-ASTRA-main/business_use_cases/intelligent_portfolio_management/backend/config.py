"""
This module serves as the central configuration hub for the agentic framework,
managing all external service connections, credentials, and application settings.

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
"""

from dotenv import load_dotenv
import os
from azure.keyvault.secrets import SecretClient # type: ignore
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential # type: ignore
from azure.identity import ClientSecretCredential



CONFIG = {
    "KEY_VAULT_NAME": os.getenv("KEY_VAULT_NAME", "kvt-maf-dev"),
    "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    "EMBEDDING_VECTOR_DIMENSION": os.getenv("EMBEDDING_VECTOR_DIMENSION", "1536")
    }

keyVaultName = CONFIG["KEY_VAULT_NAME"]
keyVaultURL = f"https://{keyVaultName}.vault.azure.net"
azureOpenAIVersion = CONFIG["AZURE_OPENAI_API_VERSION"]
embeddingVectorDimension = int(CONFIG["EMBEDDING_VECTOR_DIMENSION"])

credential = DefaultAzureCredential()
# credential = DefaultAzureCredential(exclude_managed_identity_credential=True)
client = SecretClient(vault_url=keyVaultURL, credential=credential)

# Open AI
azure_openai_endpoint=client.get_secret(name="aisvc-openai-endpoint").value
azure_openai_api_key=client.get_secret(name="aisvc-key").value
azure_openai_api_version = azureOpenAIVersion
# Embedding
azure_openai_embedding_deployment = client.get_secret(name="aoai-embedding-deploymentname").value
azure_openai_embedding_model =client.get_secret(name="aoai-embedding-model").value
embedding_vector_dimension = embeddingVectorDimension

# AI Search
search_credential =AzureKeyCredential(client.get_secret(name="aisearch-key").value)
search_endpoint =client.get_secret(name="aisearch-endpoint").value

# # Cognitive Services
# azure_ai_cognitive_services_key = client.get_secret(name="azure-ai-cognitive-services-key").value
# azure_ai_cognitive_services_endpoint = client.get_secret(name="azure-ai-cognitive-services-endpoint").value
chat_completion_model_name = "gpt4o"
chat_completion_model_temperature=0.2
chat_completion_model_max_tokens=1000

# Cosmos DB

# Create the checkpoint saver config

# Service principal authentication variables
# cosmosdb_tenant_id=client.get_secret(name="tenant-id").value
# cosmosdb_client_id =client.get_secret(name="cosmos-clientid-hq-iav-dev-cosmosdb").value 
# cosmosdb_client_secret =client.get_secret(name="agentic-cosmos").value

# conn_str =client.get_secret(name="cosmosdb-connstr").value
# cosmos_vector_property_name = "vector"
# cosmosdb_data_container = "terminology"
# cosmosdb_history_container = "chathistory"
container_conversations_name = "conversations"
container_checkpoint_name = "checkpoints"
container_checkpoint_writes_name = "checkpoint_writes"
database_name = "agentic-framework"
cosmosdb_endpoint=client.get_secret(name="cosmosdb-url").value
cosmosdb_account_key = client.get_secret(name="cosmosdb-account-key").value
# Authenticate
# cosmosdb_credential = ClientSecretCredential(cosmosdb_tenant_id, cosmosdb_client_id, cosmosdb_client_secret)
cosmosdb_credential = cosmosdb_account_key

# Json Resource ID
resource_id = client.get_secret(name="ds-resource-id").value

# Application Insight
app_insight_connection_string = client.get_secret(name="app-insight-connection-string").value

bing_search_key = client.get_secret(name="bing-search-key").value

# USe Case Specfic

# HQ Glossary
hq_glossary_index_name = f"index-json-hqglossary"
hq_glossary_data_source_connection_name = f"dsoc-json-hqglossary"
hq_glossary_semantic_configuration_name = "my-semantic-config"  # default
hq_glossary_scoring_profile="my-scoring-profile", # default
hq_glossary_search_nearest_neighbour=50 # default
hq_glossary_search_field_name="text_vector"

# IT Support Terminology
it_support_index_name = "index-json-it-terminology"
it_support_data_source_connection_name = "dsoc-json-it-terminology"
it_support_search_nearest_neighbour=50 # default
it_support_search_field_name="text_vector"

# Microsoft ASTRA Roadmap PowerPoint Index Configuration
astra_roadmap_index_name = "index-astra-roadmap"
astra_roadmap_semantic_configuration_name = "astra-roadmap-semantic-config"
astra_roadmap_search_nearest_neighbour = 50
astra_roadmap_search_field_name = "text_vector"
astra_roadmap_scoring_profile = "astra-roadmap-scoring-profile"

# Bing Resource
# bing_project_id = client.get_secret(name="bing_project_id").value
# bing_connection_name = ""
