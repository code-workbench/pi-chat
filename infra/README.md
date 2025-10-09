# Infrastructure

This directory contains the Azure infrastructure as code (IaC) using Bicep templates for the pi-chat project.

## Architecture

The infrastructure deploys the following Azure resources:

1. **Azure Container Registry (ACR)** - Stores container images for the application
2. **Azure App Service** - Hosts the containerized chat application
   - Connects to ACR via Managed Identity for secure image pulling
   - No credentials needed for registry authentication
3. **Azure Function App** - Receives HTTP requests and forwards them to Service Bus
   - Configured with Node.js runtime
   - Consumption (serverless) plan for cost efficiency
4. **Azure Service Bus** - Message queue for async request processing
   - Standard tier with a queue named 'requests'
   - Connected to the Function App for message handling

## Prerequisites

- Azure CLI installed and authenticated
- Azure subscription with appropriate permissions
- Bicep CLI (comes with Azure CLI)

## Deployment

### 1. Login to Azure

```bash
az login
```

### 2. Create a Resource Group

```bash
az group create --name rg-pichat-dev --location eastus
```

### 3. Deploy the Infrastructure

Using the parameter file:

```bash
az deployment group create \
  --resource-group rg-pichat-dev \
  --template-file main.bicep \
  --parameters main.bicepparam
```

Or with inline parameters:

```bash
az deployment group create \
  --resource-group rg-pichat-dev \
  --template-file main.bicep \
  --parameters location=eastus environmentName=dev baseName=pichat
```

### 4. Get Deployment Outputs

```bash
az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `location` | Azure region for resources | `resourceGroup().location` |
| `environmentName` | Environment name (dev, staging, prod) | `dev` |
| `baseName` | Base name for all resources | `pichat` |
| `containerImageName` | Container image name to deploy | `chat-app:latest` |

## Resources Created

### Naming Convention

Resources follow the pattern: `{baseName}-{environmentName}-{resourceType}`

Example for dev environment:
- Container Registry: `pichatdev` (no hyphens allowed)
- App Service: `pichat-dev-app`
- Function App: `pichat-dev-func`
- Service Bus: `pichat-dev`

### Resource Details

#### Container Registry
- **SKU**: Basic
- **Admin Access**: Disabled (uses managed identity)
- **Public Access**: Enabled

#### App Service
- **Plan**: B1 Basic (Linux)
- **Authentication**: Managed Identity to ACR
- **HTTPS**: Enforced
- **TLS**: Minimum version 1.2

#### Function App
- **Plan**: Consumption (Y1)
- **Runtime**: Node.js 18
- **Functions Version**: 4
- **Includes**: Storage account for function state
- **Environment Variables**:
  - `ServiceBusConnectionString`: Connection to Service Bus
  - `ServiceBusQueueName`: Name of the queue to send messages to

#### Service Bus
- **Tier**: Standard
- **Queue Properties**:
  - Lock duration: 5 minutes
  - Max size: 1024 MB
  - Message TTL: 14 days
  - Max delivery count: 10

## Module Structure

```
infra/
├── main.bicep                          # Main orchestration template
├── main.bicepparam                     # Parameters file
├── README.md                           # This file
└── modules/
    ├── containerRegistry.bicep         # ACR module
    ├── appService.bicep                # App Service module
    ├── functionApp.bicep               # Function App module
    ├── serviceBus.bicep                # Service Bus module
    └── roleAssignment.bicep            # ACR role assignment module
```

## Security

- **Managed Identity**: App Service uses system-assigned managed identity with AcrPull role
- **HTTPS Only**: All web services enforce HTTPS
- **TLS 1.2**: Minimum TLS version enforced
- **No Admin Credentials**: ACR admin user is disabled
- **Secure Connections**: Service Bus connection string stored securely in Function App settings

## Cleanup

To delete all resources:

```bash
az group delete --name rg-pichat-dev --yes --no-wait
```

## Next Steps

1. Push a container image to the Container Registry
2. Deploy Function App code to handle HTTP requests
3. Configure the App Service to use the deployed container image
4. Set up CI/CD pipeline for automated deployments
