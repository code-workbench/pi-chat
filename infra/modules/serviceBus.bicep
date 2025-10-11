@description('The location for the service bus')
param location string

@description('The name of the service bus namespace')
param serviceBusName string

@description('The name of the service bus queue')
param queueName string

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: serviceBusName
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    minimumTlsVersion: '1.2'
  }
}

resource serviceBusQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: queueName
  properties: {
    lockDuration: 'PT5M'
    maxSizeInMegabytes: 1024
    requiresDuplicateDetection: false
    requiresSession: false
    defaultMessageTimeToLive: 'P14D'
    deadLetteringOnMessageExpiration: false
    enableBatchedOperations: true
    maxDeliveryCount: 10
  }
}

resource telemetryTopic 'Microsoft.ServiceBus/namespaces/topics@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: 'Telemetry'
  properties: {
    maxSizeInMegabytes: 1024
    requiresDuplicateDetection: false
    defaultMessageTimeToLive: 'P14D'
    enableBatchedOperations: true
  }
}

resource actionTopic 'Microsoft.ServiceBus/namespaces/topics@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: 'Action'
  properties: {
    maxSizeInMegabytes: 1024
    requiresDuplicateDetection: false
    defaultMessageTimeToLive: 'P14D'
    enableBatchedOperations: true
  }
}

resource serviceBusAuthRule 'Microsoft.ServiceBus/namespaces/authorizationRules@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: 'RootManageSharedAccessKey'
  properties: {
    rights: [
      'Listen'
      'Manage'
      'Send'
    ]
  }
}

output serviceBusNamespace string = serviceBusNamespace.name
output serviceBusConnectionString string = serviceBusAuthRule.listKeys().primaryConnectionString
output serviceBusQueueName string = serviceBusQueue.name
