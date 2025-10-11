import json
import logging
import os
import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('GetTelemetry function processing a request.')

    try:
        # Parse the request body
        req_body = req.get_json()
        
        # Validate required fields
        if not req_body:
            return func.HttpResponse(
                "Please pass a TelemetryRequest in the request body",
                status_code=400
            )
        
        sensor_key = req_body.get('SensorKey')
        start_date = req_body.get('StartDate')
        end_date = req_body.get('EndDate')
        
        # Validate that all required fields are present
        if not sensor_key or not start_date or not end_date:
            return func.HttpResponse(
                "TelemetryRequest must include SensorKey, StartDate, and EndDate",
                status_code=400
            )
        
        # Create the telemetry request message
        telemetry_request = {
            'SensorKey': sensor_key,
            'StartDate': start_date,
            'EndDate': end_date
        }
        
        # Get Service Bus namespace from environment
        service_bus_namespace = os.environ.get('ServiceBusNamespace')
        
        if not service_bus_namespace:
            logging.error('ServiceBusNamespace not configured')
            return func.HttpResponse(
                "Service Bus namespace not configured",
                status_code=500
            )
        
        # Send message to Service Bus topic using managed identity
        credential = DefaultAzureCredential()
        with ServiceBusClient(service_bus_namespace, credential) as client:
            with client.get_topic_sender(topic_name="Telemetry") as sender:
                message = ServiceBusMessage(json.dumps(telemetry_request))
                sender.send_messages(message)
                logging.info(f'Sent telemetry request to Service Bus topic: {telemetry_request}')
        
        return func.HttpResponse(
            json.dumps({"status": "success", "message": "Telemetry request sent"}),
            mimetype="application/json",
            status_code=200
        )
        
    except ValueError as e:
        logging.error(f'Invalid JSON in request: {str(e)}')
        return func.HttpResponse(
            "Invalid JSON in request body",
            status_code=400
        )
    except Exception as e:
        logging.error(f'Error processing request: {str(e)}')
        return func.HttpResponse(
            f"Error processing request: {str(e)}",
            status_code=500
        )
