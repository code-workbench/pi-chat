# Pi Chat Azure Functions

This Azure Functions app provides MCP (Model Context Protocol) endpoints for the Pi Chat application.

## Endpoints

### GetTelemetry
**POST** `/api/getTelemetry`

Submits a telemetry request to the Service Bus "Telemetry" topic.

**Request Body:**
```json
{
  "sensorKey": "string",
  "startDate": "2024-01-01T00:00:00Z",
  "endDate": "2024-01-31T23:59:59Z"
}
```

### SendAction
**POST** `/api/sendAction`

Submits an action request to the Service Bus "Action" topic.

**Request Body:**
```json
{
  "actionType": "string",
  "actionSpec": "{\"key\": \"value\"}"
}
```

### MCP Endpoints

- **GET** `/api/mcp/info` - Returns MCP server information
- **GET** `/api/mcp/tools` - Lists available MCP tools

## Development

### Prerequisites
- Node.js 18.x or higher
- Azure Functions Core Tools v4

### Install Dependencies
```bash
npm install
```

### Build
```bash
npm run build
```

### Run Locally
```bash
npm start
```

### Environment Variables
- `ServiceBusConnectionString` - Connection string for Azure Service Bus

## Deployment

The function app is deployed via Azure Bicep templates in the `infra` directory.
