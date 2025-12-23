#!/bin/bash
# Deployment script for Pi Chat Web Application

set -e

echo "🚀 Pi Chat Web Application Deployment"
echo "======================================"

# Check if resource group is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <resource-group-name>"
    echo "Example: $0 rg-pichat-dev"
    exit 1
fi

RESOURCE_GROUP=$1

# Get deployment outputs
echo ""
echo "📋 Getting deployment information..."

DEPLOYMENT_NAME="main"

# Get resource names from infrastructure deployment
ACR_NAME=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.containerRegistryName.value -o tsv)

APP_NAME=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.appServiceName.value -o tsv)

FUNCTION_APP_NAME=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.functionAppName.value -o tsv)

FUNCTION_APP_URL=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.functionAppUrl.value -o tsv)

OPENAI_NAME=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.openAIName.value -o tsv)

OPENAI_ENDPOINT=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.openAIEndpoint.value -o tsv)

DEPLOYMENT_NAME_OUTPUT=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.openAIDeploymentName.value -o tsv)

AI_INSIGHTS_CONNECTION=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.appInsightsConnectionString.value -o tsv)

echo "✓ Container Registry: $ACR_NAME"
echo "✓ App Service: $APP_NAME"
echo "✓ Function App: $FUNCTION_APP_NAME"
echo "✓ OpenAI Service: $OPENAI_NAME"

# Build and push container image
echo ""
echo "🐳 Building and pushing container image..."
cd webapp
az acr build --registry $ACR_NAME --image chat-app:latest .
cd ..

echo "✓ Container image pushed successfully"

# Get API keys
echo ""
echo "🔑 Retrieving API keys..."

OPENAI_KEY=$(az cognitiveservices account keys list \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

FUNCTION_KEY=$(az functionapp keys list \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query functionKeys.default -o tsv)

# Generate Flask secret key
FLASK_SECRET=$(openssl rand -hex 32)

# Configure App Service
echo ""
echo "⚙️  Configuring App Service..."

az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    AZURE_OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
    AZURE_OPENAI_API_KEY="$OPENAI_KEY" \
    AZURE_OPENAI_DEPLOYMENT_NAME="$DEPLOYMENT_NAME_OUTPUT" \
    FUNCTION_APP_URL="$FUNCTION_APP_URL" \
    FUNCTION_APP_KEY="$FUNCTION_KEY" \
    APPLICATIONINSIGHTS_CONNECTION_STRING="$AI_INSIGHTS_CONNECTION" \
    FLASK_SECRET_KEY="$FLASK_SECRET" \
    PORT="8000" \
    WEBSITES_PORT="8000" \
  > /dev/null

echo "✓ App Service configured successfully"

# Restart App Service
echo ""
echo "🔄 Restarting App Service..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP > /dev/null

echo "✓ App Service restarted"

# Get App Service URL
APP_URL=$(az webapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query defaultHostName -o tsv)

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Web Application URL: https://$APP_URL"
echo "🔧 Function App URL: $FUNCTION_APP_URL"
echo ""
echo "You can now access the chat interface at: https://$APP_URL"
