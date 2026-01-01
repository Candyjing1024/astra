# Import Packages - Following the same pattern as existing indexers

from azure.keyvault.secrets import SecretClient # type: ignore
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential # type: ignore
from azure.search.documents.indexes.models import ( # type: ignore
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SearchIndex,
    SemanticConfiguration,
    SemanticSearch,
    ScoringProfile,
    SemanticPrioritizedFields,
    SemanticField,
    TagScoringFunction,
    TagScoringParameters,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    IndexingParameters,
    IndexingParametersConfiguration
)
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient # type: ignore

import os
from azure.search.documents.indexes import SearchIndexClient # type: ignore
from azure.search.documents.indexes import SearchIndexerClient # type: ignore
from azure.search.documents.indexes.models import ( # type: ignore
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataIdentity
)

# Configuration - Customized for Microsoft ASTRA Roadmap PowerPoint
import os
CONFIG = {
    "KEY_VAULT_NAME": os.getenv("KEY_VAULT_NAME", "kvt-maf-dev"),
    "SOURCE_DATA_TYPE": os.getenv("SOURCE_DATA_TYPE", "pptx"),  # PowerPoint presentation
    "MODULE_NAME": os.getenv("MODULE_NAME", "astra-roadmap"),  # Microsoft ASTRA Roadmap
    "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    "EMBEDDING_VECTOR_DIMENSION": os.getenv("EMBEDDING_VECTOR_DIMENSION", "1536"),
    "BLOB_CONTAINER_NAME": os.getenv("BLOB_CONTAINER_NAME", "presentations")  # For PowerPoint files
}

# Extract configuration variables
keyVaultName = CONFIG["KEY_VAULT_NAME"]
keyVaultURL = f"https://{keyVaultName}.vault.azure.net"
azureOpenAIVersion = CONFIG["AZURE_OPENAI_API_VERSION"]
sourceDataType = CONFIG["SOURCE_DATA_TYPE"]
moduleName = CONFIG["MODULE_NAME"]
embeddingVectorDimension = int(CONFIG["EMBEDDING_VECTOR_DIMENSION"])
blobContainerName = CONFIG["BLOB_CONTAINER_NAME"]

print(f"Creating index for Microsoft ASTRA Roadmap PowerPoint")
print(f"Source data type: {sourceDataType}")
print(f"Container: {blobContainerName}")

# Get credentials and secrets
credential = DefaultAzureCredential(exclude_managed_identity_credential=True)
client = SecretClient(vault_url=keyVaultURL, credential=credential)

# Get required secrets (matching config.py secret names)
azure_openai_endpoint = client.get_secret(name="aisvc-openai-endpoint").value
azure_openai_api_key = client.get_secret(name="aisvc-key").value
azure_openai_embedding_deployment = client.get_secret(name="aoai-embedding-deploymentname").value
azure_openai_embedding_model = client.get_secret(name="aoai-embedding-model").value
search_credential = AzureKeyCredential(client.get_secret(name="aisearch-key").value)
search_endpoint = client.get_secret(name="aisearch-endpoint").value
blob_storage_name = client.get_secret(name="blobstore-account-name").value
# azure_ai_cognitive_services_key = client.get_secret(name="azure-ai-cognitive-services-key").value
# azure_ai_cognitive_services_endpoint = client.get_secret(name="azure-ai-cognitive-services-endpoint").value
resource_id = client.get_secret(name="ds-resource-id").value

# Generate names using simplified pattern for ASTRA Roadmap
index_name = "index-astra-roadmap"  # Simplified name as requested
data_source_connection_name = f"dsoc-{sourceDataType}-{moduleName}"

print(f"Index name: {index_name}")
print(f"Data source connection name: {data_source_connection_name}")

# Data source creation function (reusing existing pattern)
def create_or_update_data_source(indexer_client, data_source_connection_name, blob_container_name, resource_id):
    """
    Creates or updates a data source connection.
    """
    indexer_container = SearchIndexerDataContainer(name=blob_container_name)
    data_source_connection = SearchIndexerDataSourceConnection(
        name=data_source_connection_name,
        type="adlsgen2",
        connection_string=resource_id,
        container=indexer_container
    )
    data_source = indexer_client.create_or_update_data_source_connection(data_source_connection=data_source_connection)
    print(f"Data source '{data_source.name}' created or updated successfully.")
    return data_source

# Initialize clients
indexer_client = SearchIndexerClient(endpoint=search_endpoint, credential=search_credential)
index_client = SearchIndexClient(endpoint=search_endpoint, credential=search_credential)

# Create data source
data_source = create_or_update_data_source(indexer_client, data_source_connection_name, blobContainerName, resource_id)

## Define fields for Microsoft ASTRA Roadmap PowerPoint - Optimized for presentation content
fields = [
    # Core required fields (following existing pattern)
    SearchField(name="chunk_id", type=SearchFieldDataType.String, searchable=True, filterable=False, retrievable=True, sortable=True, key=True, facetable=False, analyzer_name="keyword"),
    SearchField(name="parent_id", type=SearchFieldDataType.String, searchable=False, filterable=True, retrievable=True, sortable=False, key=False, facetable=False),
    SearchField(name="chunk", type=SearchFieldDataType.String, searchable=True, filterable=False, retrievable=True, sortable=False, facetable=False, key=False),
    SearchField(name="title", type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
    SearchField(name="text_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, filterable=False, retrievable=True, sortable=False, facetable=False, key=False, vector_search_dimensions=embeddingVectorDimension, vector_search_profile_name="myHnswProfile"),
    
    # PowerPoint-specific fields for Microsoft ASTRA Roadmap
    SearchField(name="slide_number", type=SearchFieldDataType.Int32, searchable=False, sortable=True, filterable=True, facetable=True),
    SearchField(name="slide_title", type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
    SearchField(name="section", type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),  # E.g., "Overview", "Roadmap", "Architecture"
    SearchField(name="content_type", type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),  # E.g., "title", "bullet_point", "diagram"
    
    # ASTRA-specific fields
    SearchField(name="roadmap_phase", type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),  # E.g., "Phase 1", "Phase 2", "Future"
    SearchField(name="component", type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),  # E.g., "Core", "Modules", "Agents"
    SearchField(name="timeline", type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),  # E.g., "Q1 2025", "Q2 2025"
    SearchField(name="priority", type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),  # E.g., "High", "Medium", "Low"
    SearchField(name="technology", type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),  # E.g., "Azure AI", "LangGraph"
    
    # Metadata fields
    SearchField(name="source_file", type=SearchFieldDataType.String, searchable=False, sortable=False, filterable=True, facetable=True),
    SearchField(name="created_date", type=SearchFieldDataType.DateTimeOffset, searchable=False, sortable=True, filterable=True, facetable=False),
]

# Vector search configuration (reusing existing pattern)
vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(name="myHnsw")
    ],
    profiles=[
        VectorSearchProfile(
            name="myHnswProfile",
            algorithm_configuration_name="myHnsw"
        )
    ]
    # Note: Vectorizer removed to work with AI Foundry endpoint
    # Embeddings will be generated at indexing time using the AI Foundry endpoint
)

# Semantic search configuration for Microsoft ASTRA Roadmap content
semantic_config = SemanticConfiguration(
    name="astra-roadmap-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="slide_title"),
        keywords_fields=[
            SemanticField(field_name="section"),
            SemanticField(field_name="roadmap_phase"),
            SemanticField(field_name="component"),
            SemanticField(field_name="technology"),
            SemanticField(field_name="priority")
        ],
        content_fields=[SemanticField(field_name="chunk")]
    )
)

semantic_search = SemanticSearch(configurations=[semantic_config])

# Scoring profile for ASTRA Roadmap content relevance
# Scoring profile for Microsoft ASTRA Roadmap content (commented out for now)
# scoring_profile = ScoringProfile(
#     name="astra-roadmap-scoring-profile",
#     functions=[
#         TagScoringFunction(
#             field_name="roadmap_phase",
#             boost=2.0,
#             parameters=TagScoringParameters(tags_parameter="roadmap_phase_tags")
#         ),
#         TagScoringFunction(
#             field_name="priority",
#             boost=1.5,
#             parameters=TagScoringParameters(tags_parameter="priority_tags")
#         )
#     ]
# )

# Create the search index
index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search,
    semantic_search=semantic_search
    # scoring_profiles=[scoring_profile]  # Commented out for now
)

def create_search_index():
    """Create the search index"""
    try:
        result = index_client.create_or_update_index(index)
        print(f"✅ Index '{index_name}' created or updated successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating index: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Creating Your Custom Index ===")
    print()
    
    if create_search_index():
        print("✅ Index creation completed!")
        print()
        print("Next steps:")
        print("1. Upload your documents to the blob container")
        print("2. Create an indexer to process the documents")
        print("3. Add your index configuration to config.py")
        print("4. Create a search function in rag_tool.py")
    else:
        print("❌ Index creation failed")

def create_indexer():
    """Create the indexer to process PowerPoint files"""
    print("Creating indexer for Microsoft ASTRA Roadmap PowerPoint")
    
    try:
        # Create Azure AI Search client
        indexer_client = SearchIndexerClient(search_endpoint, search_credential)
        
        # Define indexer name
        indexer_name = f"{index_name}-indexer"
        
        # Configure indexing parameters for PowerPoint
        index_parameters = IndexingParameters(
            configuration=IndexingParametersConfiguration(
                data_to_extract="contentAndMetadata",
                parsing_mode="default",
                query_timeout=None,
                execution_environment="Private"
            )
        )
        
        # Create indexer
        indexer = SearchIndexer(
            name=indexer_name,
            description="Indexer for Microsoft ASTRA Roadmap PowerPoint processing",
            target_index_name=index_name,
            data_source_name=data_source_connection_name,
            parameters=index_parameters
        )
        
        # Create or update indexer
        indexer_result = indexer_client.create_or_update_indexer(indexer)
        
        # Run the indexer
        indexer_client.run_indexer(indexer_name)
        print(f"✅ Indexer '{indexer_name}' created and running!")
        print("📄 Upload your PowerPoint to the 'presentations' container and wait for indexing to complete.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating indexer: {e}")
        return False

# Main execution functions
if __name__ == "__main__":
    print("ASTRA Roadmap Indexer Setup")
    print("=" * 40)
    
    # Create index first
    print("Step 1: Creating search index...")
    create_search_index()
    
    print("\nStep 2: Creating indexer...")
    create_indexer()
    
    print("\n" + "=" * 40)
    print("🎯 NEXT STEPS:")
    print("1. Upload 'Microsoft ASTRA Roadmap.pptx' to your 'presentations' blob container")
    print("2. Wait for indexing to complete (check Azure portal)")
    print("3. Test search with: python -c \"from app.rag_tool import astra_roadmap_search_retrieval; print(astra_roadmap_search_retrieval('roadmap phases'))\"")
    print("=" * 40)
