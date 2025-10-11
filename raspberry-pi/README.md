# Raspberry Pi Telemetry Receiver

A Python application that runs as a systemd service on a Raspberry Pi (Ubuntu 22.04) to receive and process telemetry requests from Azure Service Bus.

## Overview

This application connects to Azure Service Bus and listens to the "Telemetry" topic. When messages are received, it processes them based on the `SensorKey` field and executes the appropriate action.

### Supported Sensor Types

Currently supports the following sensor types (placeholders for implementation):

- **Temperature**: Processes temperature sensor telemetry requests
- **Light**: Processes light sensor telemetry requests  
- **CPU**: Processes CPU metrics telemetry requests

## Architecture

```
Azure Function (GetTelemetry) 
    ↓
Service Bus Telemetry Topic
    ↓
Raspberry Pi Telemetry Receiver (this application)
    ↓
Local Sensor Reading / Action Execution
```

## Prerequisites

- Raspberry Pi running Ubuntu 22.04
- Python 3.9 or higher
- Azure Service Bus namespace with "Telemetry" topic configured
- Azure Service Bus subscription created for this application
- Network connectivity to Azure

## Installation

### Quick Install

Run the automated installation script:

```bash
sudo ./install.sh
```

This script will:
1. Create installation directory at `/opt/pi-telemetry-receiver`
2. Install Python dependencies
3. Set up a Python virtual environment
4. Install the systemd service
5. Configure logging

### Manual Installation

If you prefer manual installation:

1. **Install system dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3 python3-pip python3-venv
   ```

2. **Create installation directory:**
   ```bash
   sudo mkdir -p /opt/pi-telemetry-receiver
   cd /opt/pi-telemetry-receiver
   ```

3. **Copy application files:**
   ```bash
   sudo cp telemetry_receiver.py /opt/pi-telemetry-receiver/
   sudo cp requirements.txt /opt/pi-telemetry-receiver/
   ```

4. **Create virtual environment:**
   ```bash
   sudo python3 -m venv /opt/pi-telemetry-receiver/venv
   ```

5. **Install Python dependencies:**
   ```bash
   sudo /opt/pi-telemetry-receiver/venv/bin/pip install -r /opt/pi-telemetry-receiver/requirements.txt
   ```

6. **Create configuration file:**
   ```bash
   sudo cp .env.example /opt/pi-telemetry-receiver/.env
   ```

7. **Install systemd service:**
   ```bash
   sudo cp pi-telemetry-receiver.service /etc/systemd/system/
   sudo systemctl daemon-reload
   ```

## Configuration

Edit the configuration file at `/opt/pi-telemetry-receiver/.env`:

```bash
sudo nano /opt/pi-telemetry-receiver/.env
```

Required configuration:

```env
# Azure Service Bus Configuration
SERVICE_BUS_NAMESPACE=your-namespace.servicebus.windows.net
SUBSCRIPTION_NAME=pi-telemetry-subscription
```

### Azure Service Bus Setup

Before running the application, you need to:

1. **Create a subscription on the Telemetry topic:**
   ```bash
   az servicebus topic subscription create \
     --resource-group rg-pichat-dev \
     --namespace-name pichat-dev \
     --topic-name Telemetry \
     --name pi-telemetry-subscription
   ```

2. **Configure authentication:**
   
   **Option A: Managed Identity (Recommended for Azure VMs)**
   - If running on an Azure VM, assign a managed identity to the VM
   - Grant the identity "Azure Service Bus Data Receiver" role on the Service Bus namespace
   
   **Option B: Service Principal (For on-premises Raspberry Pi)**
   - Create a service principal and note the credentials
   - Add these to your `.env` file:
     ```env
     AZURE_CLIENT_ID=your-client-id
     AZURE_TENANT_ID=your-tenant-id
     AZURE_CLIENT_SECRET=your-client-secret
     ```
   - Grant the service principal "Azure Service Bus Data Receiver" role

## Usage

### Start the Service

```bash
sudo systemctl start pi-telemetry-receiver
```

### Enable Auto-start on Boot

```bash
sudo systemctl enable pi-telemetry-receiver
```

### Check Service Status

```bash
sudo systemctl status pi-telemetry-receiver
```

### View Logs

**View recent logs:**
```bash
sudo journalctl -u pi-telemetry-receiver -n 50
```

**Follow logs in real-time:**
```bash
sudo journalctl -u pi-telemetry-receiver -f
```

**View application log file:**
```bash
sudo tail -f /var/log/pi-telemetry-receiver.log
```

### Stop the Service

```bash
sudo systemctl stop pi-telemetry-receiver
```

### Restart the Service

```bash
sudo systemctl restart pi-telemetry-receiver
```

## Testing

### Send a Test Message

You can test the receiver by sending a message through the Azure Function:

```bash
curl -X POST https://pichat-dev-func.azurewebsites.net/api/GetTelemetry?code=<function-key> \
  -H "Content-Type: application/json" \
  -d '{
    "SensorKey": "Temperature",
    "StartDate": "2025-01-01T00:00:00Z",
    "EndDate": "2025-01-02T00:00:00Z"
  }'
```

Then check the logs to see if the message was received and processed:

```bash
sudo journalctl -u pi-telemetry-receiver -n 20
```

## Development

### Message Format

Messages received from the Service Bus have the following format:

```json
{
  "SensorKey": "Temperature|Light|CPU",
  "StartDate": "2025-01-01T00:00:00Z",
  "EndDate": "2025-01-02T00:00:00Z"
}
```

### Adding New Sensor Types

To add support for a new sensor type:

1. Add a new processing method in `telemetry_receiver.py`:
   ```python
   def process_newsensor_request(self, message_body):
       logger.info(f"Processing NEWSENSOR request: {message_body}")
       # Implement sensor-specific logic here
   ```

2. Add a case in the `process_message` method:
   ```python
   elif sensor_key == 'newsensor':
       self.process_newsensor_request(message_body)
   ```

### Local Development

For local development without installing as a service:

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file with your configuration

4. Run the application:
   ```bash
   python3 telemetry_receiver.py
   ```

## Troubleshooting

### Service Won't Start

Check the service status and logs:
```bash
sudo systemctl status pi-telemetry-receiver
sudo journalctl -u pi-telemetry-receiver -n 50
```

### Authentication Errors

Verify your Azure credentials and permissions:
- Check that the `.env` file has correct values
- Verify the managed identity or service principal has the "Azure Service Bus Data Receiver" role
- Test connectivity to Azure Service Bus

### No Messages Received

- Verify the subscription exists on the Telemetry topic
- Check that messages are being sent to the Service Bus topic
- Verify network connectivity from the Raspberry Pi to Azure
- Check firewall settings

### Permission Errors

Ensure proper file permissions:
```bash
sudo chown -R pi:pi /opt/pi-telemetry-receiver
sudo chown pi:pi /var/log/pi-telemetry-receiver.log
```

## File Structure

```
raspberry-pi/
├── telemetry_receiver.py          # Main application
├── requirements.txt                # Python dependencies
├── .env.example                    # Example configuration file
├── pi-telemetry-receiver.service   # Systemd service file
├── install.sh                      # Installation script
└── README.md                       # This file
```

## Security Considerations

- Store credentials securely in the `.env` file
- Use managed identity when possible (Azure VMs)
- Restrict file permissions on `.env` file
- Keep Python dependencies up to date
- Monitor logs for suspicious activity

## Contributing

To contribute improvements or add new sensor support:

1. Test changes locally
2. Update documentation
3. Submit a pull request

## Related Documentation

- [Azure Functions Documentation](../functions/README.md)
- [Infrastructure Documentation](../infra/README.md)
- [Azure Service Bus Python SDK](https://docs.microsoft.com/en-us/python/api/overview/azure/servicebus)

## License

See [LICENSE](../LICENSE) file in the root of the repository.
