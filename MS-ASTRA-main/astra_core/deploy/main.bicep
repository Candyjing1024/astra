// General parameters
param resourceGroupName string

param location string
param environment string
param workload string
param resourceTags object = {}


// Azure Search
param azureSearchSku string = 'standard'
param azureSearchPartitionCount int = 1
param azureSearchReplicaCount int = 1

// OpenAI Parameters
param openAiEmbeddingModelName string = 'text-embedding-3-small'
param openAiEmbeddingModelVersion string = '1'
param openAiEmbeddingDeploymentId string = 'text-embedding-3-small'
param openAiEmbeddingModelCapacity int = 120

param openAiMainModelDeploymentId string = 'gpt4o'
param openAiMainModelName string = 'gpt-4o'
param openAiMainModelVersion string = '2024-11-20'
param openAiMainModelCapacity int = 50

// // App Service Plans Parameters
param uiPlanSku string = 'B3'
param aspLocation string = 'westus'


var resourceSuffix = '${workload}-${environment}'
var resourceSuffixNoSpecialChars = replace(resourceSuffix, '-', '')

// Monitoring

module log 'br/public:avm/res/operational-insights/workspace:0.7.1' = {
  name: 'logAnalytics-deployment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    location: location
    tags: resourceTags
    name: 'log-${resourceSuffix}'
    skuName: 'PerGB2018'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    dataRetention: 30
    useResourcePermissions: true
    managedIdentities: {
      systemAssigned: true
    }
  }
}

module appi 'br/public:avm/res/insights/component:0.4.1' = {
  name: 'applicationInsights-deployment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    location: location
    tags: resourceTags
    name: 'ains-main-${resourceSuffix}'
    workspaceResourceId: log.outputs.resourceId
    applicationType: 'web'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    retentionInDays: 90
  }
}


module aspFront 'br/public:avm/res/web/serverfarm:0.3.0' = {
  name: 'appserviceplanui-deployment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    location: aspLocation
    tags: resourceTags
    name: 'asp-front-${resourceSuffix}'
    skuName: uiPlanSku
    skuCapacity: 1
    kind: 'Linux'
  }
}

// Web Apps

module app_Ui 'br/public:avm/res/web/site:0.11.1' = {
  name: 'appservice-ui-deployment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    location: aspLocation
    tags: resourceTags
    name: 'app-ui-${resourceSuffix}'
    serverFarmResourceId: aspFront.outputs.resourceId
    kind: 'app,linux,container'
    managedIdentities: {
      systemAssigned: true
    }
    publicNetworkAccess: 'Enabled'
    siteConfig: {
      minTlsVersion: '1.3'
      http20Enabled: true
      linuxFxVersion: 'NODE|22-lts'
      alwaysOn: true   
      cors: {
        allowedOrigins: ['*']
        supportCredentials: false
        allowedMethods: ['*']
        allowedHeaders: ['*']
      }
    }
    appSettingsKeyValuePairs: {
      SCM_DO_BUILD_DURING_DEPLOYMENT: '1'
      WEBSITE_NODE_DEFAULT_VERSION: '22-lts'
      PORT: '8080'
      WEBSITES_PORT: '8080'
    }
    diagnosticSettings: [
      {
        workspaceResourceId: log.outputs.resourceId
        logCategoriesAndGroups: [
          {
            categoryGroup: 'allLogs'
            enabled: true
          }
        ]
        metricCategories: []
      }
    ]
  }
}

module appapi 'br/public:avm/res/web/site:0.15.1' = {
  name: 'appserviceapi-deployment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    location: aspLocation
    tags: resourceTags
    name: 'app-api-${resourceSuffix}'
    serverFarmResourceId: aspFront.outputs.resourceId
    kind: 'app,linux'
    managedIdentities: {
      systemAssigned: true
    }
    publicNetworkAccess: 'Enabled'
    siteConfig: {
      minTlsVersion: '1.3'
      http20Enabled: true
      linuxFxVersion: 'Python|3.11'
      appCommandLine: 'gunicorn --workers 4 --threads 2 --timeout 1200 --access-logfile "-" --error-logfile "-" --bind=0.0.0.0:8000 -k uvicorn.workers.UvicornWorker agentic_framework.run:app_fastapi'
      cors: {
        allowedOrigins: ['*']
        supportCredentials: false
        allowedMethods: ['*']
        allowedHeaders: ['*']
      }
      alwaysOn: true   
    }
    appSettingsKeyValuePairs: {
      SCM_DO_BUILD_DURING_DEPLOYMENT: '1'
    }
    diagnosticSettings: [
      {
        workspaceResourceId: log.outputs.resourceId
        logCategoriesAndGroups: [
          {
            categoryGroup: 'allLogs'
            enabled: true
          }
        ]
      }
    ]
  }
}

// Azure Search

module search 'br/public:avm/res/search/search-service:0.7.2' = {
  name: 'search-deployment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    location: location
    tags: resourceTags
    name: 'srch-${resourceSuffix}'
    sku: azureSearchSku
    managedIdentities: {
      systemAssigned: true
    }
    replicaCount: azureSearchReplicaCount
    partitionCount: azureSearchPartitionCount
    authOptions: null
    semanticSearch: 'standard'
    hostingMode: 'default'
    disableLocalAuth: false
    roleAssignments: [
      {
        principalId: appapi.outputs.systemAssignedMIPrincipalId
        roleDefinitionIdOrName: 'Search Index Data Contributor'
      }
      {
        principalId: appapi.outputs.systemAssignedMIPrincipalId
        roleDefinitionIdOrName: 'Search Service Contributor'
      }  
    ]
    publicNetworkAccess: 'Enabled'
    diagnosticSettings: [
      {
        workspaceResourceId: log.outputs.resourceId
        logCategoriesAndGroups: [
          {
            categoryGroup: 'allLogs'
            enabled: true
          }
        ]
        metricCategories: []
      }
    ]
  }
}

// It needs a separated module to update the private link connections to avoid circular dependencies with storage due to RBAC assignments

module roleSearchBlobContributor 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  name: 'search-stadata-indexcontributor-roleassignment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    principalId: search.outputs.systemAssignedMIPrincipalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe' // Storage Blob Data Contributor
    resourceId: staData.outputs.resourceId
  }
}

module roleSearchOpenAIUser 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  name: 'search-openai-user-roleassignment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    principalId: search.outputs.systemAssignedMIPrincipalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
    resourceId: aiservices.outputs.resourceId
  }
}

module roleSearchAIServicesUser 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  name: 'search-cognitiveservices-user-roleassignment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    principalId: search.outputs.systemAssignedMIPrincipalId
    roleDefinitionId: 'a97b65f3-24c7-4388-baec-2e87135dc908' // Cognitive Services User
    resourceId: aiservices.outputs.resourceId
  }
}

module roleSearchCosmosDBAccountReaderRole 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  name: 'search-cosmosdb-user-roleassignment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    principalId: search.outputs.systemAssignedMIPrincipalId
    roleDefinitionId: 'fbdf93bf-df7d-467e-a4d2-9458aa1360c8' // Cosmos DB Account Reader Role
    resourceId: cosmosdb.outputs.resourceId
  }
}


module roleSearchCosmosBuiltIn 'modules/document-db/database-account/sql-role/main.bicep' = {
    name: 'search-cosmosdb-built-in-roleassignment'
    params: {
      name: 'search-cosmos-contributor'
      databaseAccountName: cosmosdb.outputs.name
      roleName: '00000000-0000-0000-0000-000000000002'
      roleType: 'BuiltInRole'
      principalIds: [search.outputs.systemAssignedMIPrincipalId]
    }
  }


// Storage Account

module staData 'br/public:avm/res/storage/storage-account:0.14.3' = {
  name: 'stadata-deployment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    location: location
    tags: resourceTags
    name: 'stdata${resourceSuffixNoSpecialChars}'
    skuName: 'Standard_LRS'
    allowSharedKeyAccess: true
    allowBlobPublicAccess: true 
    managedIdentities: {
      systemAssigned: true
    }
    enableHierarchicalNamespace: true
    keyType: 'Account'
    blobServices: {
      deleteRetentionPolicyEnabled: true
      deleteRetentionPolicyDays: 7
      containers : [
        {
          name: 'documents'
          publicAccess: 'Container'
        }
        {
          name: 'documents-images'
          publicAccess: 'Container'
        }
      ]
    }
    roleAssignments: [
      {
        principalId: appapi.outputs.systemAssignedMIPrincipalId
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
    ]
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
    diagnosticSettings: [
      {
        workspaceResourceId: log.outputs.resourceId
        logCategoriesAndGroups: [
          {
            categoryGroup: 'allLogs'
            enabled: true
          }
        ]
        metricCategories: []
      }
    ]
  }
}


// Cosmos DB

module cosmosdb 'br/public:avm/res/document-db/database-account:0.8.1' = {
  name: 'cosmosdb-deployment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    location: aspLocation
    tags: resourceTags
    name: 'cosmos-${resourceSuffix}'
    databaseAccountOfferType: 'Standard'
    managedIdentities: {
      systemAssigned: true
    }
    backupPolicyType: 'Periodic'
    backupIntervalInMinutes: 240
    backupRetentionIntervalInHours: 8
    backupStorageRedundancy: 'Geo'
    maxStalenessPrefix: 100
    maxIntervalInSeconds: 5
    disableKeyBasedMetadataWriteAccess: false
    disableLocalAuth: false
    automaticFailover: false
    networkRestrictions: {
        ipRules: []
        virtualNetworkRules: []
        networkAclBypass: 'None'
        publicNetworkAccess: 'Enabled'
    }
    locations: [
      {
        failoverPriority: 0
        isZoneRedundant: false
        locationName: aspLocation
      }
    ]
    sqlDatabases: [
      {
        name: 'agentic-framework'
        autoscaleSettingsMaxThroughput: 4000
        containers: [
          {
            name: 'checkpoint'
            paths: [
              '/thread_id'
            ]
            defaultTtl: -1
          }
        ]
      }
    ]
    sqlRoleAssignmentsPrincipalIds: [ appapi.outputs.systemAssignedMIPrincipalId ]
    sqlRoleDefinitions: [
      {
        name: 'cosmosdb-contributor'
        roleName: '00000000-0000-0000-0000-000000000002'
        roleType: 'BuiltInRole'
      }
    ]
    diagnosticSettings: [
      {
        workspaceResourceId: log.outputs.resourceId
        logCategoriesAndGroups: [
          {
            categoryGroup: 'allLogs'
            enabled: true
          }
        ]
        metricCategories: []
      }
    ]
  }
}


// AI Services
module aiservices 'br/public:avm/res/cognitive-services/account:0.8.1' = {
  name: 'aiservices-deployment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    location: location
    tags: resourceTags
    name: 'aisvc-${resourceSuffix}'
    customSubDomainName: 'aisvc-${resourceSuffix}'
    sku: 'S0'
    kind: 'AIServices'
    disableLocalAuth: false
    networkAcls: {
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
    deployments: [
      {
        name: openAiEmbeddingDeploymentId
        model: {
          format: 'OpenAI'
          name: openAiEmbeddingModelName
          version: openAiEmbeddingModelVersion
        }
        sku: {
          name: 'GlobalStandard'
          capacity: openAiEmbeddingModelCapacity
        }
      }
      {
        name: openAiMainModelDeploymentId
        model: {
          format: 'OpenAI'
          name: openAiMainModelName
          version: openAiMainModelVersion
        }
        sku: {
          name: 'GlobalStandard'
          capacity: openAiMainModelCapacity
        }
      }
    ]
    roleAssignments: [
      {
        principalId: appapi.outputs.systemAssignedMIPrincipalId
        roleDefinitionIdOrName: 'Cognitive Services OpenAI User'
      }
    ]
    diagnosticSettings: [
      {
        workspaceResourceId: log.outputs.resourceId
        logCategoriesAndGroups: [
          {
            categoryGroup: 'allLogs'
            enabled: true
          }
        ]
        metricCategories: []
      }
    ]
  }

}

// Keyvault
module kvt 'br/public:avm/res/key-vault/vault:0.9.0' = {
  name: 'keyvault-deployment'
  scope: resourceGroup(subscription().subscriptionId, resourceGroupName)
  params: {
    location: location
    tags: resourceTags
    name: 'kvt-${resourceSuffix}'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
    secrets: [
      {
        name: 'aisearch-endpoint'
        value: 'https://${search.outputs.name}.search.windows.net'
      }
      {
        name: 'aisvc-embedding-deploymentname'
        value: openAiEmbeddingDeploymentId
      }
      {
        name: 'aisvc-embedding-model'
        value: openAiEmbeddingModelName
      }
      {
        name: 'aisvc-endpoint'
        value: 'https://${aiservices.outputs.name}.cognitiveservices.azure.com'
      }
      // {
      //   name: 'blobstore-account-name'
      //   value: staData.outputs.name
      // }
      // {
      //   name: 'ds-resource-id'
      //   value: 'ResourceId=${staData.outputs.resourceId}'
      // }
      {
        name: 'cosmosdb-url'
        value: 'https://${cosmosdb.outputs.name}.documents.azure.com:443/'
      }
      {
        name: 'app-insight-connection-string'
        value: appi.outputs.connectionString
      }
    ]
    roleAssignments: [
      {
        principalId: appapi.outputs.systemAssignedMIPrincipalId
        roleDefinitionIdOrName: 'Key Vault Secrets User'
      }
    ]
    diagnosticSettings: [
      {
        workspaceResourceId: log.outputs.resourceId
        logCategoriesAndGroups: [
          {
            categoryGroup: 'allLogs'
            enabled: true
          }
        ]
        metricCategories: []
      }
    ]
  }
}


// Outputs

output logName string = log.outputs.name
output appiName string = appi.outputs.name
output appapiName string = appapi.outputs.name
output searchName string = search.outputs.name
output staDataName string = staData.outputs.name
output cosmosdbName string = cosmosdb.outputs.name
output aiservicesName string = aiservices.outputs.name
output kvtName string = kvt.outputs.name
