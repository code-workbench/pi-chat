# Quick Deployment Guide

## Quick Start

### 1. Prerequisites Check
```bash
# Check Azure CLI is installed
az version

# Login to Azure
az login

# Set your subscription (if you have multiple)
az account set --subscription "Your-Subscription-Name"
```

### 2. Deploy Everything
```bash
# Navigate to the infra directory
cd infra

# Create resource group
az group create \
  --name rg-pichat-dev \
  --location eastus

# Deploy infrastructure
az deployment group create \
  --resource-group rg-pichat-dev \
  --template-file main.bicep \
  --parameters main.bicepparam
```

### 3. Verify Deployment
```bash
# Check deployment status
az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.provisioningState

# Get all outputs
az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs -o table
```

## What Gets Created

| Resource Type | Resource Name Pattern | Purpose |
|--------------|----------------------|---------|
| Resource Group | `rg-pichat-dev` | Container for all resources |
| Container Registry | `pichatdev` | Stores container images |
| App Service Plan | `pichat-dev-app-plan` | Hosts the web app |
| App Service | `pichat-dev-app` | Runs the chat application |
| Storage Account | `pichatdevfuncsa` | Required for Function App |
| App Service Plan (Consumption) | `pichat-dev-func-plan` | Hosts the function |
| Function App | `pichat-dev-func` | Python-based MCP endpoints |
| Service Bus Namespace | `pichat-dev` | Message broker |
| Service Bus Queue | `requests` | Stores messages |
| Service Bus Topic | `Telemetry` | Telemetry data routing |
| Service Bus Topic | `Action` | Action command routing |
| OpenAI Service | `pichat-dev-openai` | AI model service (gpt-4o-mini) |
| AI Foundry Hub | `pichat-dev-ai-hub` | Machine learning workspace |
| Storage Account (AI) | `pichatdevai` | Storage for AI Hub |
| Application Insights | `pichat-dev-ai-insights` | Monitoring for AI resources |
| Log Analytics Workspace | `pichat-dev-ai-logs` | Log aggregation |
| Key Vault | `pichatdevkv` | Secure secrets storage |

## Next Steps After Deployment

### 1. Push a Container Image to ACR
```bash
# Get ACR login server
ACR_LOGIN_SERVER=$(az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.containerRegistryLoginServer.value -o tsv)

# Login to ACR
az acr login --name pichatdev

# Tag and push your image
docker tag your-local-image:latest $ACR_LOGIN_SERVER/chat-app:latest
docker push $ACR_LOGIN_SERVER/chat-app:latest
```

### 2. Deploy Function App Code
```bash
# Get function app name
FUNC_NAME=$(az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.functionAppName.value -o tsv)

# Navigate to functions directory and deploy
cd ../functions
func azure functionapp publish $FUNC_NAME --python
```

**Note:** The Function App includes two Python-based MCP endpoints:
- **GetTelemetry**: Receives telemetry requests and sends them to the "Telemetry" Service Bus topic
- **SendAction**: Receives action requests and sends them to the "Action" Service Bus topic

See [functions/README.md](../functions/README.md) for detailed endpoint documentation and testing examples.

### 3. Restart App Service
```bash
# Get app service name
APP_NAME=$(az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.appServiceName.value -o tsv)

# Restart to pull the new image
az webapp restart --name $APP_NAME --resource-group rg-pichat-dev
```

### 4. Test Your Deployment
```bash
# Get endpoints
echo "App Service URL:"
az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.appServiceUrl.value -o tsv

echo "Function App URL:"
az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.functionAppUrl.value -o tsv

echo "OpenAI Endpoint:"
az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.openAIEndpoint.value -o tsv

echo "AI Foundry Hub Name:"
az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.aiHubName.value -o tsv
```

### 5. Get OpenAI API Key
```bash
# Get OpenAI service name
OPENAI_NAME=$(az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.openAIName.value -o tsv)

# Get the API key
az cognitiveservices account keys list \
  --name $OPENAI_NAME \
  --resource-group rg-pichat-dev \
  --query key1 -o tsv
```

## Troubleshooting

### Check App Service Logs
```bash
az webapp log tail --name pichat-dev-app --resource-group rg-pichat-dev
```

### Check Function App Logs
```bash
az functionapp log tail --name pichat-dev-func --resource-group rg-pichat-dev
```

### Verify Managed Identity Assignment
```bash
# Check if role assignment exists
az role assignment list \
  --assignee $(az webapp identity show --name pichat-dev-app --resource-group rg-pichat-dev --query principalId -o tsv) \
  --scope $(az acr show --name pichatdev --query id -o tsv)
```

## Clean Up

### Delete Everything
```bash
az group delete --name rg-pichat-dev --yes --no-wait
```

This will delete all resources created in the deployment.
