# pi-chat
A project showcasing a containerized chat application, which communicates and causes actions on a raspberry pi

## Project Structure

- **[functions/](functions/)** - Azure Functions for MCP endpoints (GetTelemetry and SendAction)
- **[infra/](infra/)** - Infrastructure as Code (Bicep) for Azure resources
- **[raspberry-pi/](raspberry-pi/)** - Python application for receiving telemetry messages on Raspberry Pi

## Architecture

```
Web Application (Azure App Service)
    ↓
Azure Functions (MCP Endpoints)
    ↓
Azure Service Bus Topics
    ↓
Raspberry Pi Telemetry Receiver
    ↓
Sensor Reading / Action Execution
```

## Components

### Azure Functions
HTTP endpoints that receive requests and forward them to Service Bus topics:
- `GetTelemetry` - Sends telemetry requests to the Telemetry topic
- `SendAction` - Sends action requests to the Action topic

See [functions/README.md](functions/README.md) for details.

### Raspberry Pi Telemetry Receiver
A Python service that runs on the Raspberry Pi and receives messages from the Service Bus Telemetry topic. It processes messages based on the SensorKey field (Temperature, Light, CPU).

See [raspberry-pi/README.md](raspberry-pi/README.md) for installation and usage.

### Infrastructure
Azure resources deployed using Bicep templates, including:
- Container Registry
- App Service
- Function App
- Service Bus (with topics and subscriptions)
- OpenAI Service
- AI Foundry Hub

See [infra/README.md](infra/README.md) for deployment instructions.
