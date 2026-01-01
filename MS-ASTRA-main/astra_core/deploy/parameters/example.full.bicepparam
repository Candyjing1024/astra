using '../main.bicep'

// General parameters
param resourceGroupName = '<Resource Group Name>'
param location = '<Azure Region>'
param environment = '<dev|pre|prod>'
param workload = '<solution workload name (used for resource naming)'

param resourceTags = {
  tagName: '<your tag value>'
}

param functionsAuthClientId =  '<Client ID>'
param functionsAuthTenantId =  '<Tenant ID>'

// Azure Search parameters
param azureSearchSku = '<standard|standard2|standard3...>'
param azureSearchPartitionCount = 1
param azureSearchReplicaCount = 1

// OpenAI Parameters
// Minor Model used for minor operations like chat history management and query extraction
// OpenAI Major Model used for Answer generation and FUQs
param openaiLocation = '<Azure Region for Open AI Resource>'
param openAiEmbeddingModelName = 'text-embedding-3-large'
param openAiEmbeddingModelVersion = '2'
param openAiEmbeddingDeploymentId = 'gaia-embeddings'
param openAiEmbeddingModelCapacity = 100
param openAiMinorModelDeploymentId = 'gaia-chat-35'
param openAiMinorModelName = 'gpt-35-turbo'
param openAiMinorModelVersion = '0125'
param openAiMinorModelCapacity = 60
param openAiMajorModelDeploymentId = 'gaia-gpt4o'
param openAiMajorModelName = 'gpt-4o'
param openAiMajorModelVersion = '2024-05-13'
param openAiMajorModelCapacity = 70

// Custom Named Entity Recognition (if needed)
param cnerProjectName = ''
param cnerDeploymentName = ''

// App Service Plans Tiers
param skillPlansSku = 'B2'
param uiPlanSku = 'B2'

// UI Custom domain parameters
param customDomainUiUrl = ''

