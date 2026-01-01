## 🎯 Requirements to enable private networking

1. Virtual Network with subnets:
    - `PrivateEndpoints `subnet (for private endpoints)
    - `VNetIntegration` subnet (for App Service VNet integration)
2. Private DNS Zones:
    - `privatelink.azurewebsites.net`
    - `privatelink.search.windows.net`
    - `privatelink.blob.core.windows.net`
    - `privatelink.documents.azure.com`
    - `privatelink.cognitiveservices.azure.com`
    - `privatelink.openai.azure.com`
    - `privatelink.vaultcore.azure.net`
    - `privatelink.ods.opinsights.azure.com`
    - `privatelink.oms.opinsights.azure.com`
3. Network Configuration Changes:
    - Change all `publicNetworkAccess` from `'Enabled'` to `'Disabled'`
    - Change `allowBlobPublicAccess` from `true` to `false`
    - Change `networkAcls.defaultAction` from `'Allow'` to `'Deny'`
    - Add VNet integration to App Services
    - Configure shared private link resources for Azure Search
 
Private Endpoints required:
1. UI App Service
    - Private DNS Zone: `privatelink.azurewebsites.net`
2. Requirements Agent API
    - Private DNS Zone: `privatelink.azurewebsites.net`
3. Azure Cognitive Search
    - Private DNS Zone: `privatelink.search.windows.net`
4. Data Storage Account
    - Service: Blob
    - Private DNS Zone: `privatelink.blob.core.windows.net`
5. Cosmos DB
    - Service: SQL
    - Private DNS Zone: `privatelink.documents.azure.com`
6. AI Services
    - Private DNS Zones:
      - `privatelink.cognitiveservices.azure.com`
      - `privatelink.openai.azure.com`
7. Key Vault
    - Private DNS Zone: `privatelink.vaultcore.azure.net`
8. Log Analytics Workspace
    - Private DNS Zones:
      - `privatelink.ods.opinsights.azure.com`
      - `privatelink.oms.opinsights.azure.com`
