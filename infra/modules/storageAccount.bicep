@description('The location for the storage account')
param location string

@description('The name of the storage account')
param storageAccountName string

@description('The SKU name for the storage account')
param skuName string = 'Standard_LRS'

var storageAccountNameSafe = length(storageAccountName) > 24 ? substring(storageAccountName, 0, 24) : length(storageAccountName) < 3 ? '${storageAccountName}xxx' : storageAccountName

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountNameSafe
  location: location
  sku: {
    name: skuName
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

output storageAccountId string = storageAccount.id
output storageAccountName string = storageAccount.name
