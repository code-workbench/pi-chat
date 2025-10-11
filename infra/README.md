# Infrastructure

This directory contains the Azure infrastructure as code (IaC) using Bicep templates for the pi-chat project.

## Architecture

The infrastructure deploys the following Azure resources:

1. **Azure Container Registry (ACR)** - Stores container images for the application
2. **Azure App Service** - Hosts the containerized chat application
   - Connects to ACR via Managed Identity for secure image pulling
   - No credentials needed for registry authentication
3. **Azure Function App** - Python-based MCP endpoints for telemetry and action requests
   - Configured with Python runtime
   - Consumption (serverless) plan for cost efficiency
   - Two HTTP endpoints: GetTelemetry and SendAction
4. **Azure Service Bus** - Message broker for async request processing
   - Standard tier with a queue named 'requests'
   - Topics: 'Telemetry' for sensor data and 'Action' for device commands
   - Connected to the Function App for message handling
5. **Azure OpenAI Service** - Provides AI capabilities with GPT-4o-mini model
   - Deployed with gpt-4o-mini model for chat completions
   - Standard tier with customizable capacity
6. **Azure AI Foundry Hub** - Machine learning workspace for AI operations
   - Hub workspace for managing AI resources and projects
   - Connected to OpenAI service, Container Registry, Key Vault, and Storage
7. **Supporting Resources**:
   - **Application Insights** - Monitoring and telemetry for AI Hub
   - **Log Analytics Workspace** - Log aggregation for insights
   - **Key Vault** - Secure storage for secrets and keys
   - **Storage Account** - Required storage for AI Foundry Hub

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
- OpenAI Service: `pichat-dev-openai`
- AI Foundry Hub: `pichat-dev-ai-hub`
- Key Vault: `pichatdevkv` (no hyphens allowed)
- Storage Account: `pichatdevai` (no hyphens allowed)

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
- **Runtime**: Python 3.x
- **Functions Version**: 4
- **Includes**: Storage account for function state
- **Endpoints**:
  - `GetTelemetry`: Receives telemetry requests and sends to "Telemetry" topic
  - `SendAction`: Receives action requests and sends to "Action" topic
- **Environment Variables**:
  - `ServiceBusConnectionString`: Connection to Service Bus
  - `ServiceBusQueueName`: Name of the queue to send messages to

#### Service Bus
- **Tier**: Standard
- **Queue**: `requests`
  - Lock duration: 5 minutes
  - Max size: 1024 MB
  - Message TTL: 14 days
  - Max delivery count: 10
- **Topics**: `Telemetry` and `Action`
  - Max size: 1024 MB
  - Message TTL: 14 days
  - Batch operations: Enabled
- **Subscriptions**:
  - `pi-telemetry-subscription` on Telemetry topic
    - For Raspberry Pi telemetry receiver
    - Lock duration: 5 minutes
    - Max delivery count: 10

#### Azure OpenAI Service
- **SKU**: S0
- **Kind**: OpenAI
- **Model**: gpt-4o-mini (2024-07-18)
- **Deployment**: Standard tier with configurable capacity (default: 10)
- **Public Access**: Enabled

#### Azure AI Foundry Hub
- **SKU**: Basic
- **Kind**: Hub (Machine Learning Workspace)
- **Identity**: System-assigned managed identity
- **Network**: Public access enabled
- **Connections**: Integrated with OpenAI service
- **Dependencies**: Storage Account, Application Insights, Container Registry, Key Vault

#### Application Insights
- **Type**: Web application monitoring
- **Workspace**: Connected to Log Analytics workspace
- **Retention**: 30 days

#### Key Vault
- **SKU**: Standard
- **Authorization**: RBAC enabled
- **Soft Delete**: Enabled with 7-day retention
- **Public Access**: Enabled

#### Storage Account (AI Hub)
- **SKU**: Standard_LRS
- **Kind**: StorageV2
- **HTTPS Only**: Enforced
- **TLS**: Minimum version 1.2
- **Blob Public Access**: Disabled

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
    ├── roleAssignment.bicep            # ACR role assignment module
    ├── openai.bicep                    # Azure OpenAI Service module
    ├── aiFoundryHub.bicep              # Azure AI Foundry Hub module
    ├── applicationInsights.bicep       # Application Insights module
    ├── keyVault.bicep                  # Key Vault module
    └── storageAccount.bicep            # Storage Account module
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
2. Deploy Python Function App code to handle MCP requests
   - See [functions/README.md](../functions/README.md) for detailed documentation
   - Deploy using: `func azure functionapp publish <function-app-name> --python`
3. Configure the App Service to use the deployed container image
4. Set up CI/CD pipeline for automated deployments

## Function Endpoints

The deployed Function App provides two MCP endpoints:

- **GetTelemetry** (`POST /api/GetTelemetry`)
  - Accepts telemetry requests with SensorKey, StartDate, EndDate
  - Sends messages to Service Bus "Telemetry" topic
  
- **SendAction** (`POST /api/SendAction`)
  - Accepts action requests with ActionType and ActionSpec
  - Sends messages to Service Bus "Action" topic

For detailed API documentation and testing examples, see [functions/README.md](../functions/README.md).
