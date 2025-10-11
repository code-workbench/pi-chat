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
  }
}

// Azure Function App
module functionApp './modules/functionApp.bicep' = {
  name: 'functionApp'
  params: {
    location: location
    functionAppName: '${resourceSuffix}-func'
    serviceBusConnectionString: serviceBus.outputs.serviceBusConnectionString
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

// Outputs
output containerRegistryName string = containerRegistry.outputs.containerRegistryName
output containerRegistryLoginServer string = containerRegistry.outputs.containerRegistryLoginServer
output appServiceName string = appService.outputs.appServiceName
output appServiceUrl string = appService.outputs.appServiceUrl
output functionAppName string = functionApp.outputs.functionAppName
output functionAppUrl string = functionApp.outputs.functionAppUrl
output serviceBusNamespace string = serviceBus.outputs.serviceBusNamespace
