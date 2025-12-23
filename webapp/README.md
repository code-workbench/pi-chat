# Pi Chat Web Application

A Python-based web application that provides a chat interface powered by Azure AI Foundry, with integration to Azure Function MCP endpoints for controlling Raspberry Pi devices.

## Features

- 💬 **Interactive Chat Interface** - Clean, modern web UI for conversing with AI
- 🤖 **Azure AI Foundry Integration** - Powered by GPT-4o-mini for intelligent responses
- 🔧 **MCP Tool Integration** - Function calling to Azure Functions for:
  - 🌡️ **GetTelemetry** - Retrieve sensor data (Temperature, Light, CPU)
  - 📸 **SendAction** - Control Raspberry Pi devices (Camera, LEDs, etc.)
- 📊 **Application Insights** - Full telemetry and monitoring integration
- 🐳 **Containerized** - Docker support for easy deployment

## Architecture

```
User Browser
    ↓ (HTTP)
Flask Web Application
    ↓ (Azure AI SDK)
Azure AI Foundry (GPT-4o-mini)
    ↓ (Function Calling)
Flask App (MCP Client)
    ↓ (HTTP POST)
Azure Functions (MCP Endpoints)
    ↓ (Service Bus)
Raspberry Pi Services
```

## Prerequisites

- Python 3.11 or higher
- Azure OpenAI Service (or Azure AI Foundry Hub)
- Azure Functions with MCP endpoints deployed
- Application Insights instance (optional but recommended)

## Local Development

### 1. Install Dependencies

```bash
cd webapp
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your Azure credentials:

```bash
# Azure OpenAI / AI Foundry Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini

# Azure Function MCP Endpoints
FUNCTION_APP_URL=https://your-function-app.azurewebsites.net
FUNCTION_APP_KEY=your-function-key

# Application Insights
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key
PORT=5000
```

### 3. Run the Application

```bash
# Set environment variables (Linux/Mac)
export $(cat .env | xargs)

# Or on Windows
# set the variables manually or use a tool

# Run with Flask development server
python app.py

# Or run with Gunicorn (production-like)
gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
```

The application will be available at `http://localhost:5000`

## Docker Deployment

### Build the Docker Image

```bash
cd webapp
docker build -t pi-chat-webapp .
```

### Run the Container

```bash
docker run -p 8000:8000 \
  -e AZURE_OPENAI_ENDPOINT="https://..." \
  -e AZURE_OPENAI_API_KEY="..." \
  -e AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini" \
  -e FUNCTION_APP_URL="https://..." \
  -e FUNCTION_APP_KEY="..." \
  -e APPLICATIONINSIGHTS_CONNECTION_STRING="..." \
  -e FLASK_SECRET_KEY="..." \
  pi-chat-webapp
```

## Azure Deployment

### Deploy to Azure Container Registry

```bash
# Login to Azure
az login

# Get ACR login server
ACR_NAME=$(az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.containerRegistryName.value -o tsv)

ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

# Build and push image
cd webapp
az acr build --registry $ACR_NAME --image chat-app:latest .
```

### Configure App Service

The infrastructure already provisions an App Service. Configure it with environment variables:

```bash
APP_NAME=$(az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.appServiceName.value -o tsv)

OPENAI_ENDPOINT=$(az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.openAIEndpoint.value -o tsv)

FUNCTION_APP_URL=$(az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.functionAppUrl.value -o tsv)

# Get OpenAI API key
OPENAI_NAME=$(az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.openAIName.value -o tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
  --name $OPENAI_NAME \
  --resource-group rg-pichat-dev \
  --query key1 -o tsv)

# Get Function App key
FUNCTION_APP_NAME=$(az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.functionAppName.value -o tsv)

FUNCTION_KEY=$(az functionapp keys list \
  --name $FUNCTION_APP_NAME \
  --resource-group rg-pichat-dev \
  --query functionKeys.default -o tsv)

# Configure App Service environment variables
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group rg-pichat-dev \
  --settings \
    AZURE_OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
    AZURE_OPENAI_API_KEY="$OPENAI_KEY" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini" \
    FUNCTION_APP_URL="$FUNCTION_APP_URL" \
    FUNCTION_APP_KEY="$FUNCTION_KEY" \
    FLASK_SECRET_KEY="$(openssl rand -hex 32)" \
    PORT="8000"
```

### Add Application Insights

```bash
# Get Application Insights connection string from infrastructure
AI_CONNECTION_STRING=$(az monitor app-insights component show \
  --app pichat-dev-ai-insights \
  --resource-group rg-pichat-dev \
  --query connectionString -o tsv)

# Add to App Service
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group rg-pichat-dev \
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING="$AI_CONNECTION_STRING"
```

### Restart App Service

```bash
az webapp restart --name $APP_NAME --resource-group rg-pichat-dev
```

## API Endpoints

### POST /api/chat

Chat with the AI assistant.

**Request:**
```json
{
  "message": "What's the current temperature?",
  "history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

**Response:**
```json
{
  "response": "The current temperature is 22.5°C",
  "finish_reason": "stop"
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "azure_ai_configured": true,
  "app_insights_configured": true,
  "mcp_endpoints_configured": true,
  "timestamp": "2025-12-23T03:50:00.000Z"
}
```

## Usage Examples

Once deployed, users can interact with the chat interface using natural language:

- **Get sensor data**: "What's the current temperature?" or "Show me CPU usage"
- **Control devices**: "Take a picture" or "Turn on the LED"
- **General questions**: "What sensors are available?" or "What can you do?"

The AI will automatically call the appropriate MCP functions (GetTelemetry or SendAction) as needed.

## Monitoring

The application is integrated with Azure Application Insights for:

- Request tracking
- Error logging
- Custom event tracking (chat requests, function calls)
- Performance metrics

View telemetry in the Azure Portal under your Application Insights resource.

## Security Considerations

- **API Keys**: Never commit API keys to source control
- **Environment Variables**: Use Azure Key Vault or App Service configuration
- **HTTPS**: Always use HTTPS in production (enforced by Azure App Service)
- **Session Secret**: Use a strong, random secret key for Flask sessions
- **CORS**: Configure CORS policies if needed for API access

## Troubleshooting

### Chat not working

1. Check environment variables are set correctly
2. Verify Azure OpenAI endpoint and API key
3. Check Application Insights logs for errors

### MCP functions not being called

1. Verify FUNCTION_APP_URL and FUNCTION_APP_KEY are correct
2. Test Function App endpoints directly (see [functions/README.md](../functions/README.md))
3. Check Function App logs in Azure Portal

### Application Insights not receiving data

1. Verify APPLICATIONINSIGHTS_CONNECTION_STRING is set
2. Check connection string format is correct
3. Allow a few minutes for data to appear in Azure Portal

## Development

### Project Structure

```
webapp/
├── app.py                  # Main Flask application
├── templates/
│   └── index.html         # Chat interface HTML
├── static/
│   ├── style.css          # Styling
│   └── script.js          # Client-side JavaScript
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── .env.example          # Environment variable template
└── README.md            # This file
```

### Adding New Features

1. **New MCP Tools**: Add tool definitions in `app.py` under the `tools` list
2. **UI Changes**: Modify `templates/index.html` and `static/` files
3. **API Endpoints**: Add new routes in `app.py`

## License

See [LICENSE](../LICENSE) file in the repository root.
