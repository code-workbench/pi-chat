#!/usr/bin/env python3
"""
Raspberry Pi Action Receiver Service

This application runs on the Raspberry Pi and receives action requests
from Azure Service Bus Action topic. It processes messages based on the
ActionType field and executes the appropriate action.
"""

import json
import logging
import os
import sys
from datetime import datetime
from azure.servicebus import ServiceBusClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/pi-action-receiver.log')
    ]
)
logger = logging.getLogger(__name__)


class ActionReceiver:
    """Handles receiving and processing action messages from Service Bus."""
    
    def __init__(self, service_bus_namespace, subscription_name):
        """
        Initialize the ActionReceiver.
        
        Args:
            service_bus_namespace: The fully qualified Service Bus namespace (e.g., 'namespace.servicebus.windows.net')
            subscription_name: The name of the subscription to receive from
        """
        self.service_bus_namespace = service_bus_namespace
        self.subscription_name = subscription_name
        self.topic_name = "Action"
        logger.info(f"Initializing ActionReceiver for namespace: {service_bus_namespace}")
        
    def process_camera_action(self, message_body):
        """
        Process a camera action request.
        
        Args:
            message_body: Dictionary containing the action request
        """
        logger.info(f"Processing CAMERA action: {message_body}")
        action_type = message_body.get('ActionType')
        action_spec = message_body.get('ActionSpec')
        
        # Placeholder: Implement camera action logic here
        logger.info(f"Executing camera action '{action_type}' with spec: {action_spec}")
        # TODO: Implement actual camera control logic
        # Example: Capture photo, start/stop video recording, adjust settings
        
    def process_message(self, message):
        """
        Process a received Service Bus message.
        
        Args:
            message: ServiceBusReceivedMessage object
        """
        try:
            # Parse the message body
            message_body = json.loads(str(message))
            logger.info(f"Received message: {message_body}")
            
            # Extract ActionType
            action_type = message_body.get('ActionType', '').lower()
            
            # Route based on ActionType using case statement
            if action_type == 'camera':
                self.process_camera_action(message_body)
            else:
                logger.warning(f"Unknown ActionType: {action_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message as JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            
    def run(self):
        """
        Main loop to receive and process messages from Service Bus.
        """
        logger.info("Starting action receiver service...")
        
        try:
            # Use DefaultAzureCredential for authentication (supports managed identity)
            credential = DefaultAzureCredential()
            
            with ServiceBusClient(self.service_bus_namespace, credential) as client:
                logger.info(f"Connected to Service Bus: {self.service_bus_namespace}")
                
                # Create a receiver for the subscription
                with client.get_subscription_receiver(
                    topic_name=self.topic_name,
                    subscription_name=self.subscription_name,
                    max_wait_time=5
                ) as receiver:
                    logger.info(f"Listening for messages on topic '{self.topic_name}', subscription '{self.subscription_name}'...")
                    
                    while True:
                        # Receive messages in batches
                        received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=5)
                        
                        for msg in received_msgs:
                            self.process_message(msg)
                            # Complete the message to remove it from the subscription
                            receiver.complete_message(msg)
                            
        except KeyboardInterrupt:
            logger.info("Service interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error in service: {e}", exc_info=True)
            raise


def main():
    """Main entry point for the action receiver service."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration from environment variables
    service_bus_namespace = os.getenv('SERVICE_BUS_NAMESPACE')
    subscription_name = os.getenv('ACTION_SUBSCRIPTION_NAME', 'pi-action-subscription')
    
    # Validate configuration
    if not service_bus_namespace:
        logger.error("SERVICE_BUS_NAMESPACE environment variable is not set")
        sys.exit(1)
        
    logger.info("=" * 60)
    logger.info("Raspberry Pi Action Receiver Service")
    logger.info("=" * 60)
    logger.info(f"Service Bus Namespace: {service_bus_namespace}")
    logger.info(f"Subscription Name: {subscription_name}")
    logger.info(f"Started at: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    # Create and run the receiver
    receiver = ActionReceiver(service_bus_namespace, subscription_name)
    receiver.run()


if __name__ == "__main__":
    main()
