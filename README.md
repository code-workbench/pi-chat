# pi-chat
A project showcasing a containerized chat application, which communicates and causes actions on a raspberry pi

## Project Structure

- **[webapp/](webapp/)** - Python Flask web application with chat interface powered by Azure AI Foundry
- **[functions/](functions/)** - Azure Functions for MCP endpoints (GetTelemetry and SendAction)
- **[infra/](infra/)** - Infrastructure as Code (Bicep) for Azure resources
- **[raspberry-pi/](raspberry-pi/)** - Python applications for receiving telemetry and action messages on Raspberry Pi

## Architecture

```
User Browser
    ↓ (HTTPS)
Web Application (Azure App Service - Flask)
    ↓ (Azure AI SDK)
Azure AI Foundry (GPT-4o-mini)
    ↓ (Function Calling / MCP Tools)
Azure Functions (MCP Endpoints)
    ↓ (Service Bus)
Azure Service Bus Topics (Telemetry & Action)
    ↓ (Subscriptions)
Raspberry Pi Services
    ├─ Telemetry Receiver → Sensor Reading
    └─ Action Receiver → Action Execution
```

## Components

### Web Application

A Python Flask-based web application that provides:
- Interactive chat interface for users
- Integration with Azure AI Foundry for intelligent conversations
- MCP tool integration for function calling to control Raspberry Pi
- Application Insights telemetry and monitoring

See [webapp/README.md](webapp/README.md) for details.

### Azure Functions
HTTP endpoints that receive requests and forward them to Service Bus topics:
- `GetTelemetry` - Sends telemetry requests to the Telemetry topic
- `SendAction` - Sends action requests to the Action topic

See [functions/README.md](functions/README.md) for details.

### Raspberry Pi Services

Two Python services that run on the Raspberry Pi:

1. **Telemetry Receiver** - Receives messages from the Service Bus Telemetry topic and processes them based on the SensorKey field (Temperature, Light, CPU).

2. **Action Receiver** - Receives messages from the Service Bus Action topic and processes them based on the ActionType field (Camera, etc.).

See [raspberry-pi/README.md](raspberry-pi/README.md) for installation and usage.

### Infrastructure
Azure resources deployed using Bicep templates, including:
- Container Registry
- App Service (for web application)
- Function App (for MCP endpoints)
- Service Bus (with topics and subscriptions)
- OpenAI Service (GPT-4o-mini)
- AI Foundry Hub
- Application Insights (monitoring and telemetry)

See [infra/README.md](infra/README.md) for deployment instructions.

## Quick Start

### 1. Deploy Infrastructure

```bash
# Create resource group
az group create --name rg-pichat-dev --location eastus

# Deploy infrastructure
cd infra
az deployment group create \
  --resource-group rg-pichat-dev \
  --template-file main.bicep \
  --parameters main.bicepparam
```

### 2. Deploy Azure Functions

```bash
cd functions
func azure functionapp publish <function-app-name>
```

### 3. Build and Deploy Web Application

```bash
# Build and push container image
cd webapp
az acr build --registry <acr-name> --image chat-app:latest .

# Configure App Service with environment variables (see webapp/README.md)
```

### 4. Configure Raspberry Pi Services

See [raspberry-pi/README.md](raspberry-pi/README.md) for setup instructions.

## Usage

Once deployed, access the web application at your App Service URL (e.g., `https://pichat-dev-app.azurewebsites.net`). The chat interface allows you to:

- Ask questions about sensor data: "What's the current temperature?"
- Control devices: "Take a picture with the camera"
- Get system information: "What's the CPU usage?"

The AI will automatically call the appropriate Azure Functions to interact with your Raspberry Pi.
