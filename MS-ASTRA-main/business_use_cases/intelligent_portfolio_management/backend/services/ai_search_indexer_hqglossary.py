# Import Packages

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
    TagScoringParameters
)
from azure.search.documents.indexes import SearchIndexClient # type: ignore


# Defining Config Variable to be used
import os
CONFIG = {
    "KEY_VAULT_NAME": os.getenv("KEY_VAULT_NAME", "keyvault"),
    "SOURCE_DATA_TYPE": os.getenv("SOURCE_DATA_TYPE", "json"),
    "MODULE_NAME": os.getenv("MODULE_NAME", "hqglossary"),
    "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    "EMBEDDING_VECTOR_DIMENSION": os.getenv("EMBEDDING_VECTOR_DIMENSION", "1536"),
    "BLOB_CONTAINER_NAME": os.getenv("BLOB_CONTAINER_NAME", "container")
    }


# from config import CONFIG
keyVaultName = CONFIG["KEY_VAULT_NAME"]
keyVaultURL = f"https://{keyVaultName}.vault.azure.net"
azureOpenAIVersion = CONFIG["AZURE_OPENAI_API_VERSION"]
sourceDataType = CONFIG["SOURCE_DATA_TYPE"]
moduleName = CONFIG["MODULE_NAME"]
embeddingVectorDimension = int(CONFIG["EMBEDDING_VECTOR_DIMENSION"])
blobContainerName = CONFIG["BLOB_CONTAINER_NAME"]

# aoai-vector-dimension"

print(f"Keyvault Name: {keyVaultName}")
print(f"Keyvault URL: {keyVaultURL}")
print(f"azureOpenAIVersion Name: {azureOpenAIVersion}")
print(f"Source Data Type: {sourceDataType}")
print(f"Module Name: {moduleName}")
print(f"Embedding Vector Dimension: {embeddingVectorDimension}")
print(f"Blob Container Name: {blobContainerName}")


# credential = DefaultAzureCredential()
credential = DefaultAzureCredential(exclude_managed_identity_credential=True)
client = SecretClient(vault_url=keyVaultURL, credential=credential)

# Reading Secrets
# Open AI
azure_openai_endpoint=client.get_secret(name="aoai-endpoint").value
azure_openai_api_key=client.get_secret(name="aoai-api-key").value
azure_openai_api_version = azureOpenAIVersion
# Embedding
azure_openai_embedding_deployment = client.get_secret(name="aoai-embedding-deploymentname").value
azure_openai_embedding_model =client.get_secret(name="aoai-embedding-model").value
# azure_openai_vector_dimension =client.get_secret(name="aoai-vector-dimension").value
embedding_vector_dimension = embeddingVectorDimension

# AI Search
search_credential =AzureKeyCredential(client.get_secret(name="aisearch-key").value)
search_endpoint =client.get_secret(name="aisearch-endpoint").value
# AI Service
# azure_ai_services_key =client.get_secret(name="azure-ai-services-key").value
# azure_ai_services_endpoint =client.get_secret(name="azure-ai-services-endpoint").value

# Blob Storage
blob_container_name = blobContainerName
blob_storage_name =client.get_secret(name="blobstore-account-name").value
# Cognitive Services
azure_ai_cognitive_services_key = client.get_secret(name="azure-ai-cognitive-services-key").value
azure_ai_cognitive_services_endpoint = client.get_secret(name="azure-ai-cognitive-services-endpoint").value

index_name = f"index-{sourceDataType}-{moduleName}"
data_source_connection_name = f"dsoc-{sourceDataType}-{moduleName}"
resource_id = client.get_secret(name="ds-resource-id").value

print(f"azure_openai_endpoint : {azure_openai_endpoint}")
print(f"azure_openai_api_key : {azure_openai_api_key}")
print(f"azure_openai_api_version : {azure_openai_api_version}")

print(f"azure_openai_embedding_deployment : {azure_openai_embedding_deployment}")
print(f"azure_openai_embedding_model : {azure_openai_embedding_model}")
print(f"embedding_vector_dimension : {embedding_vector_dimension}")

print(f"search_credential : {search_credential}")

print(f"search_endpoint : {search_endpoint}")
print(f"blob_container_name : {blob_container_name}")
print(f"blob_storage_name : {blob_storage_name}")
print(f"azure_ai_cognitive_services_key : {azure_ai_cognitive_services_key}")
print(f"azure_ai_cognitive_services_endpoint : {azure_ai_cognitive_services_endpoint}")

print(f"index_name: {index_name}")
print(f"data_source_connection_name: {data_source_connection_name}")
print(f"resource_id: {resource_id}")

## 1. Define Azure AI Search Datasource Object
from azure.search.documents.indexes import SearchIndexerClient # type: ignore
from azure.search.documents.indexes.models import ( # type: ignore
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataIdentity
)

def create_or_update_data_source(client, data_source_connection_name, blob_container_name, resource_id, endpoint, credential):
    """
    Creates or updates a data source connection for Azure AI Search.

    Parameters:
        indexer_client (SearchIndexerClient): The indexer client instance.
        client (SecretClient): The Azure Key Vault secret client instance.
        data_source_connection_name (str): The name of the data source connection.
        blob_container_name (str): The name of the blob container.
        resource_id (str): The resource ID for the data source connection.
        endpoint (str): The endpoint for the Azure AI Search service.
        credential (AzureKeyCredential): The credential for the Azure AI Search service.

    Returns:
        SearchIndexerDataSourceConnection: The created or updated data source connection object.
    """
    # indexer_client = SearchIndexerClient(endpoint=endpoint, credential=credential)
    indexer_container = SearchIndexerDataContainer(name=blob_container_name)
    data_source_connection = SearchIndexerDataSourceConnection(
        name=data_source_connection_name,
        type="adlsgen2",
        connection_string=resource_id,
        container=indexer_container
    )
    data_source = indexer_client.create_or_update_data_source_connection(data_source_connection=data_source_connection)
    print(f"Data source Object: {data_source.name} created or updated successfully.")
    
    return data_source

#### Create Azure AI Search Datasource Object
# Create Indexs and Indexer Objects
indexer_client = SearchIndexerClient(endpoint=search_endpoint, credential=search_credential)
index_client = SearchIndexClient(endpoint=search_endpoint, credential=search_credential)

# Create a Data Source
data_source = create_or_update_data_source(client, data_source_connection_name, blob_container_name, resource_id, search_endpoint, search_credential)

## 2. Create Azure AI Search Index
fields = [
    SearchField(name="chunk_id", type=SearchFieldDataType.String, searchable=True, filterable=False, retrievable=True, sortable=True, key=True, facetable=False, analyzer_name="keyword"),
    SearchField(name="parent_id", type=SearchFieldDataType.String, searchable=False, filterable=True, retrievable=True, sortable=False, key=False, facetable=False),
     SearchField(name="chunk", type=SearchFieldDataType.String, searchable=True, filterable=False, retrievable=True, sortable=False, facetable=False, key=False),
    SearchField(name="title",type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
    SearchField(name="text_vector",type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, filterable=False, retrievable=True, sortable=False, facetable=False, key=False, vector_search_dimensions=embedding_vector_dimension, vector_search_profile_name="myHnswProfile"),
    SearchField(name="abbreviation",type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
    SearchField(name="definition",type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
    SearchField(name="context",type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
    SearchField(name="incorrectTerms",type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
    SearchField(name="domain",type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
    SearchField(name="englishResponse",type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
    SearchField(name="sources",type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
    SearchField(name="synonym",type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
    SearchField(name="uuid",type=SearchFieldDataType.String, searchable=True, sortable=True, filterable=True, facetable=True),
]

#### 2.3 Define Vector Search, Semantic Search and Scoring Profiles

# Define the vector search configuration and parameters
vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(name="myHsnw")

    ],
    profiles=[
        VectorSearchProfile(
            name="myHnswProfile",
            algorithm_configuration_name="myHsnw",
            vectorizer_name="myOpenAI"
        )
    ]
    ,
    vectorizers=[
        AzureOpenAIVectorizer(
            vectorizer_name="myOpenAI",
            kind="azureOpenAI",
            parameters=AzureOpenAIVectorizerParameters(
                resource_url=azure_openai_endpoint,
                deployment_name=azure_openai_embedding_deployment,
                model_name=azure_openai_embedding_model,
            )
        )
    ]
)
# Configure semantic search on the index
semantic_config = SemanticConfiguration(
    name="my-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="title"),
        content_fields=[SemanticField(field_name="abbreviation"), SemanticField(field_name="title"), SemanticField(field_name="synonym"), SemanticField(field_name="chunk")],
        keywords_fields=[SemanticField(field_name="abbreviation"), SemanticField(field_name="title"), SemanticField(field_name="synonym"), SemanticField(field_name="chunk")],
    )
)
# Create the semantic search config
semantic_search = SemanticSearch(configurations=[semantic_config])
# scoring_profiles = []
scoring_profiles = [
                    ScoringProfile
                    (name="my-scoring-profile",
                     functions=[TagScoringFunction
                                (field_name="abbreviation",
                                 boost=100.0,
                                 parameters=TagScoringParameters(
                                     tags_parameter="tags",
                                     ),
                                ),
                                
                                ]
                    )
                    ]

#### 2.4 Function defitniion to create Search Index
def create_search_index(index_name, fields, vector_search, scoring_profiles, semantic_search, search_endpoint, search_credential):
    """
    Creates or updates a search index in Azure AI Search.

    Parameters:
        index_name (str): The name of the index.
        fields (list): The list of fields for the index.
        vector_search (VectorSearch): The vector search configuration.
        scoring_profiles (list): The scoring profiles for the index.
        semantic_search (SemanticSearch): The semantic search configuration.
        search_endpoint (str): The endpoint for the Azure AI Search service.
        search_credential (AzureKeyCredential): The credential for the Azure AI Search service.

    Returns:
        SearchIndex: The created or updated search index object.
    """
    # index_client = SearchIndexClient(endpoint=search_endpoint, credential=search_credential)
    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search, scoring_profiles=scoring_profiles, semantic_search=semantic_search)
    result = index_client.create_or_update_index(index=index)
    print(f"{result.name} created")
    return result

#### 2.5 Create Search Index
# Example usage:
result = create_search_index(
    index_name=index_name,
    fields=fields,
    vector_search=vector_search,
    scoring_profiles=scoring_profiles,
    semantic_search=semantic_search,
    search_endpoint=search_endpoint,
    search_credential=search_credential
)

# Import required libraries
from azure.search.documents.indexes.models import ( # type: ignore
    SplitSkill,
    AzureOpenAIEmbeddingSkill,
    SearchIndexerSkillset,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,
    AIServicesAccountKey
)

skillset_name = f"{index_name}-skillset"

def create_skillset():
    split_skill = SplitSkill(  
    description="Split skill to chunk documents",  
    text_split_mode="pages",  
    default_language_code="fr",  
    context="/document",
    maximum_page_length=2000,  
    page_overlap_length=500,
    maximum_pages_to_take=0,
    unit = "characters",   
    inputs=[ 
        # InputFieldMappingEntry(name="text", source="/document/fra/prc/trm/text")
        InputFieldMappingEntry(name="text", source="/document/fra/def_ctx_merged")
        # InputFieldMappingEntry(name="text", source="/document/uuid")


            ],  
    outputs=[  
        OutputFieldMappingEntry(name="textItems", target_name="pages")  
    ]  
    )  

    embedding_skill = AzureOpenAIEmbeddingSkill(
        description="Skill to generate embeddings via Azure OpenAI",
        context="/document/pages/*",
        resource_url=azure_openai_endpoint,
        deployment_name=azure_openai_embedding_deployment,
        model_name=azure_openai_embedding_model,
        dimensions=embedding_vector_dimension,
        api_key=azure_openai_api_key,
        inputs=[
            InputFieldMappingEntry(name="text", source="/document/pages/*"), # Chunking the definition
        ],
        outputs=[
            OutputFieldMappingEntry(name="embedding", target_name="text_vector") # Inserting the chunks into text_vector of enriched doc
        ]
    )

    index_projections = SearchIndexerIndexProjection(
        selectors=[
            SearchIndexerIndexProjectionSelector(
                target_index_name=index_name,
                parent_key_field_name="parent_id",
                source_context="/document/pages/*",
                mappings=[
                    InputFieldMappingEntry(name="text_vector", source="/document/pages/*/text_vector"),
                    InputFieldMappingEntry(name="chunk", source="/document/pages/*"),
                    InputFieldMappingEntry(name="title", source="/document/fra/prc/trm/text"), # Multiple
                    InputFieldMappingEntry(name="abbreviation", source="/document/fra/prc/abr/trm/text"),
                    InputFieldMappingEntry(name="definition", source="/document/fra/def"), # Multiple
                    InputFieldMappingEntry(name="context", source="/document/fra/ctx"), # Multiple
                    InputFieldMappingEntry(name="incorrectTerms", source="/document/fra/sous/fau/trm/text"),
                    InputFieldMappingEntry(name="domain", source="/document/cla/dom/text"),
                    InputFieldMappingEntry(name="englishResponse", source="/document/eng/prc/trm/text"),
                    InputFieldMappingEntry(name="sources", source="/document/srcs/src"), # Multiple
                    InputFieldMappingEntry(name="synonym", source="/document/fra/sous/syn/trm/text"),
                    InputFieldMappingEntry(name="uuid", source="/document/uuid"),


                ]
            )
        ],
        parameters=SearchIndexerIndexProjectionsParameters(
            projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS
        )
    )

    skills = [split_skill, embedding_skill]

    return SearchIndexerSkillset(
        name=skillset_name,
        description="Skillset to chunk documents and generating embeddings",
        skills=skills,
        index_projection=index_projections,
        # cognitive_services_account=AIServicesAccountKey(key=azure_ai_cognitive_services_key, subdomain_url=azure_ai_cognitive_services_endpoint)
    )

skillset = create_skillset()

# indexer_client = SearchIndexerClient(endpoint=endpoint, credential=credential)
indexer_client.create_or_update_skillset(skillset)
print(f"Created skillset {skillset.name}")

#### 3.2 Create Indexer
from azure.search.documents.indexes.models import ( # type: ignore
    SearchIndexer,
    IndexingParameters,
    IndexingParametersConfiguration,
    BlobIndexerImageAction
)

# Define indexer name  
indexer_name = f"{index_name}-indexer"

index_parameters = IndexingParameters(
    configuration=IndexingParametersConfiguration(
      data_to_extract="contentAndMetadata", # contentAndMetadata
      parsing_mode="jsonArray", # jsonLines
      document_root="records", #/document
      # fail_on_unprocessable_document=False,
      # fail_on_unsupported_content_type=False,
      # first_line_contains_headers=True,
      query_timeout=None,
      execution_environment="Private"
      # allow_skillset_to_read_file_data=True,

    )
  )

indexer = SearchIndexer(
  name=indexer_name,
  description="Indexer to orchestrate the document indexing and embedding generation",
  skillset_name=skillset_name,
  target_index_name=index_name,
  data_source_name=data_source.name
  ,parameters=index_parameters
)

indexer_result = indexer_client.create_or_update_indexer(indexer)

# Run the indexer to kick off the indexing process
indexer_client.run_indexer(indexer_name)
print(f' {indexer_name} is created and running. If queries return no results, please wait a bit and try again.')

