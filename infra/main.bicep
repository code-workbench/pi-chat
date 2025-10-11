targetScope = 'resourceGroup'

@description('The location for all resources')
param location string = resourceGroup().location

@description('The name of the environment (e.g., dev, staging, prod)')
param environmentName string = 'dev'

@description('The base name for all resources')
param baseName string = 'pichat'

@description('The name of the container image to deploy')
param containerImageName string = 'chat-app:latest'

var resourceSuffix = '${baseName}-${environmentName}'

// Storage Account for AI Foundry Hub
module aiStorage './modules/storageAccount.bicep' = {
  name: 'aiStorage'
  params: {
    location: location
    storageAccountName: replace('${resourceSuffix}ai', '-', '')
  }
}

// Application Insights for AI Foundry Hub
module appInsights './modules/applicationInsights.bicep' = {
  name: 'appInsights'
  params: {
    location: location
    appInsightsName: '${resourceSuffix}-ai-insights'
    logAnalyticsName: '${resourceSuffix}-ai-logs'
  }
}

// Key Vault for AI Foundry Hub
module keyVault './modules/keyVault.bicep' = {
  name: 'keyVault'
  params: {
    location: location
    keyVaultName: replace('${resourceSuffix}-kv', '-', '')
  }
}

// Azure Container Registry
module containerRegistry './modules/containerRegistry.bicep' = {
  name: 'containerRegistry'
  params: {
    location: location
    containerRegistryName: replace(resourceSuffix, '-', '')
  }
}

// Azure Service Bus
module serviceBus './modules/serviceBus.bicep' = {
  name: 'serviceBus'
  params: {
    location: location
    serviceBusName: resourceSuffix
    queueName: 'requests'
  }
}

// Azure Function App
module functionApp './modules/functionApp.bicep' = {
  name: 'functionApp'
  params: {
    location: location
    functionAppName: '${resourceSuffix}-func'
    serviceBusNamespace: serviceBus.outputs.serviceBusNamespaceFqdn
    serviceBusQueueName: 'requests'
  }
}

// Azure App Service
module appService './modules/appService.bicep' = {
  name: 'appService'
  params: {
    location: location
    appServiceName: '${resourceSuffix}-app'
    containerRegistryLoginServer: containerRegistry.outputs.containerRegistryLoginServer
    containerImageName: containerImageName
  }
}

// Role assignment for App Service to pull from Container Registry
module roleAssignment './modules/roleAssignment.bicep' = {
  name: 'roleAssignment'
  params: {
    containerRegistryName: containerRegistry.outputs.containerRegistryName
    principalId: appService.outputs.appServicePrincipalId
  }
}

// Role assignment for Function App to send messages to Service Bus
module serviceBusRoleAssignment './modules/serviceBusRoleAssignment.bicep' = {
  name: 'serviceBusRoleAssignment'
  params: {
    serviceBusNamespaceName: serviceBus.outputs.serviceBusNamespaceName
    principalId: functionApp.outputs.functionAppPrincipalId
  }
}

// Azure OpenAI Service
module openAI './modules/openai.bicep' = {
  name: 'openAI'
  params: {
    location: location
    openAIName: '${resourceSuffix}-openai'
  }
}

// Azure AI Foundry Hub
module aiHub './modules/aiFoundryHub.bicep' = {
  name: 'aiHub'
  params: {
    location: location
    hubName: '${resourceSuffix}-ai-hub'
    storageAccountId: aiStorage.outputs.storageAccountId
    applicationInsightsId: appInsights.outputs.appInsightsId
    containerRegistryId: containerRegistry.outputs.containerRegistryId
    keyVaultId: keyVault.outputs.keyVaultId
    openAIId: openAI.outputs.openAIId
  }
}

// Outputs
output containerRegistryName string = containerRegistry.outputs.containerRegistryName
output containerRegistryLoginServer string = containerRegistry.outputs.containerRegistryLoginServer
output appServiceName string = appService.outputs.appServiceName
output appServiceUrl string = appService.outputs.appServiceUrl
output functionAppName string = functionApp.outputs.functionAppName
output functionAppUrl string = functionApp.outputs.functionAppUrl
output serviceBusNamespace string = serviceBus.outputs.serviceBusNamespaceName
output openAIName string = openAI.outputs.openAIName
output openAIEndpoint string = openAI.outputs.openAIEndpoint
output openAIDeploymentName string = openAI.outputs.deploymentName
output aiHubName string = aiHub.outputs.hubName
