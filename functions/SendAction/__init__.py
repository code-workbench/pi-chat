import json
import logging
import os
import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('SendAction function processing a request.')

    try:
        # Parse the request body
        req_body = req.get_json()
        
        # Validate required fields
        if not req_body:
            return func.HttpResponse(
                "Please pass an ActionRequest in the request body",
                status_code=400
            )
        
        action_type = req_body.get('ActionType')
        action_spec = req_body.get('ActionSpec')
        
        # Validate that all required fields are present
        if not action_type or not action_spec:
            return func.HttpResponse(
                "ActionRequest must include ActionType and ActionSpec",
                status_code=400
            )
        
        # Create the action request message
        action_request = {
            'ActionType': action_type,
            'ActionSpec': action_spec
        }
        
        # Get Service Bus connection string from environment
        connection_string = os.environ.get('ServiceBusConnectionString')
        
        if not connection_string:
            logging.error('ServiceBusConnectionString not configured')
            return func.HttpResponse(
                "Service Bus connection not configured",
                status_code=500
            )
        
        # Send message to Service Bus topic
        with ServiceBusClient.from_connection_string(connection_string) as client:
            with client.get_topic_sender(topic_name="Action") as sender:
                message = ServiceBusMessage(json.dumps(action_request))
                sender.send_messages(message)
                logging.info(f'Sent action request to Service Bus topic: {action_request}')
        
        return func.HttpResponse(
            json.dumps({"status": "success", "message": "Action request sent"}),
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
