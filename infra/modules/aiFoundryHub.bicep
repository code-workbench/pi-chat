@description('The location for the AI Foundry Hub')
param location string

@description('The name of the AI Foundry Hub')
param hubName string

@description('The storage account resource ID')
param storageAccountId string

@description('The Application Insights resource ID')
param applicationInsightsId string

@description('The Container Registry resource ID')
param containerRegistryId string

@description('The Key Vault resource ID')
param keyVaultId string

@description('The OpenAI service resource ID')
param openAIId string

@description('The SKU name for the hub')
param skuName string = 'Basic'

@description('The SKU tier for the hub')
param skuTier string = 'Basic'

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-07-01-preview' = {
  name: hubName
  location: location
  sku: {
    name: skuName
    tier: skuTier
  }
  kind: 'Hub'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: hubName
    storageAccount: storageAccountId
    applicationInsights: applicationInsightsId
    containerRegistry: containerRegistryId
    keyVault: keyVaultId
    publicNetworkAccess: 'Enabled'
    managedNetwork: {
      isolationMode: 'Disabled'
    }
  }
}

// Create a connection to the OpenAI service
resource openAIConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-07-01-preview' = {
  parent: aiHub
  name: 'openai-connection'
  properties: {
    category: 'AzureOpenAI'
    target: reference(openAIId, '2023-05-01').endpoint
    authType: 'ApiKey'
    credentials: {
      key: listKeys(openAIId, '2023-05-01').key1
    }
    metadata: {
      ApiVersion: '2023-05-01'
      ApiType: 'Azure'
      ResourceId: openAIId
    }
  }
}

output hubName string = aiHub.name
output hubId string = aiHub.id
output hubPrincipalId string = aiHub.identity.principalId
