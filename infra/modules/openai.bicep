@description('The location for the OpenAI service')
param location string

@description('The name of the OpenAI service')
param openAIName string

@description('The SKU name for the OpenAI service')
param skuName string = 'S0'

@description('The name of the model deployment')
param deploymentName string = 'gpt-4o-mini'

@description('The model name')
param modelName string = 'gpt-4o-mini'

@description('The model version')
param modelVersion string = '2024-07-18'

@description('The deployment capacity')
param deploymentCapacity int = 10

resource openAI 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAIName
  location: location
  kind: 'OpenAI'
  sku: {
    name: skuName
  }
  properties: {
    customSubDomainName: openAIName
    publicNetworkAccess: 'Enabled'
  }
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAI
  name: deploymentName
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
    raiPolicyName: 'Microsoft.Default'
  }
  sku: {
    name: 'Standard'
    capacity: deploymentCapacity
  }
}

output openAIName string = openAI.name
output openAIEndpoint string = openAI.properties.endpoint
output openAIId string = openAI.id
output deploymentName string = modelDeployment.name
