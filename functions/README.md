# Azure Functions - MCP Endpoints

This directory contains Python-based Azure Functions that provide MCP (Model Context Protocol) endpoints for the Pi Chat application.

## Functions

### GetTelemetry

HTTP POST endpoint that receives telemetry requests and forwards them to the Service Bus "Telemetry" topic.

**Request Body (JSON):**
```json
{
  "SensorKey": "string",
  "StartDate": "ISO 8601 datetime string",
  "EndDate": "ISO 8601 datetime string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Telemetry request sent"
}
```

### SendAction

HTTP POST endpoint that receives action requests and forwards them to the Service Bus "Action" topic.

**Request Body (JSON):**
```json
{
  "ActionType": "string",
  "ActionSpec": "string (raw JSON)"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Action request sent"
}
```

## Local Development

### Prerequisites

- Python 3.9 or higher
- Azure Functions Core Tools
- Azure Service Bus namespace

### Setup

1. Install dependencies:
```bash
cd functions
pip install -r requirements.txt
```

2. Configure local settings:
Edit `local.settings.json` and add your Service Bus connection string:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "ServiceBusConnectionString": "Endpoint=sb://..."
  }
}
```

3. Run locally:
```bash
func start
```

## Deployment

Deploy to Azure using Azure Functions Core Tools:

```bash
func azure functionapp publish <FUNCTION_APP_NAME>
```

Or use the Azure CLI after infrastructure deployment:

```bash
# Get function app name from infrastructure output
FUNC_NAME=$(az deployment group show \
  --resource-group rg-pichat-dev \
  --name main \
  --query properties.outputs.functionAppName.value -o tsv)

# Deploy from functions directory
cd functions
func azure functionapp publish $FUNC_NAME
```

## Testing

### Automated Testing

Use the provided test scripts to test both endpoints:

**Bash script:**
```bash
./test_endpoints.sh https://pichat-dev-func.azurewebsites.net <function-key>
```

**Python script:**
```bash
python test_endpoints.py https://pichat-dev-func.azurewebsites.net <function-key>
```

To get your function key:
```bash
FUNC_NAME=pichat-dev-func
az functionapp keys list --name $FUNC_NAME --resource-group rg-pichat-dev --query functionKeys.default -o tsv
```

### Manual Testing with curl

#### Test GetTelemetry

```bash
curl -X POST https://<function-app>.azurewebsites.net/api/GetTelemetry?code=<function-key> \
  -H "Content-Type: application/json" \
  -d '{
    "SensorKey": "sensor-001",
    "StartDate": "2025-01-01T00:00:00Z",
    "EndDate": "2025-01-02T00:00:00Z"
  }'
```

#### Test SendAction

```bash
curl -X POST https://<function-app>.azurewebsites.net/api/SendAction?code=<function-key> \
  -H "Content-Type: application/json" \
  -d '{
    "ActionType": "turn_on",
    "ActionSpec": "{\"device\": \"led\", \"pin\": 17}"
  }'
```

## Architecture

```
HTTP Request → Azure Function → Service Bus Topic → Message Processing
```

- **GetTelemetry**: Sends messages to the "Telemetry" topic
- **SendAction**: Sends messages to the "Action" topic

Both functions use the Service Bus connection string from the `ServiceBusConnectionString` environment variable, which is automatically configured during infrastructure deployment.
