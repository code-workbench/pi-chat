@description('The name of the service bus namespace')
param serviceBusNamespaceName string

@description('The principal ID of the managed identity')
param principalId string

// Azure Service Bus Data Sender role definition ID
var serviceBusDataSenderRoleDefinitionId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '69a216fc-b8fb-44d8-bc22-1f3c2cd27a39')

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' existing = {
  name: serviceBusNamespaceName
}

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(serviceBusNamespace.id, principalId, serviceBusDataSenderRoleDefinitionId)
  scope: serviceBusNamespace
  properties: {
    roleDefinitionId: serviceBusDataSenderRoleDefinitionId
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

output roleAssignmentId string = roleAssignment.id
