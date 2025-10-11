#!/usr/bin/env python3
"""
Raspberry Pi Telemetry Receiver Service

This application runs on the Raspberry Pi and receives telemetry requests
from Azure Service Bus Telemetry topic. It processes messages based on the
SensorKey field and executes the appropriate action.
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
        logging.FileHandler('/var/log/pi-telemetry-receiver.log')
    ]
)
logger = logging.getLogger(__name__)


class TelemetryReceiver:
    """Handles receiving and processing telemetry messages from Service Bus."""
    
    def __init__(self, service_bus_namespace, subscription_name):
        """
        Initialize the TelemetryReceiver.
        
        Args:
            service_bus_namespace: The fully qualified Service Bus namespace (e.g., 'namespace.servicebus.windows.net')
            subscription_name: The name of the subscription to receive from
        """
        self.service_bus_namespace = service_bus_namespace
        self.subscription_name = subscription_name
        self.topic_name = "Telemetry"
        logger.info(f"Initializing TelemetryReceiver for namespace: {service_bus_namespace}")
        
    def process_temperature_request(self, message_body):
        """
        Process a temperature telemetry request.
        
        Args:
            message_body: Dictionary containing the telemetry request
        """
        logger.info(f"Processing TEMPERATURE request: {message_body}")
        sensor_key = message_body.get('SensorKey')
        start_date = message_body.get('StartDate')
        end_date = message_body.get('EndDate')
        
        # Placeholder: Implement temperature sensor reading logic here
        logger.info(f"Reading temperature data for sensor '{sensor_key}' from {start_date} to {end_date}")
        # TODO: Implement actual temperature sensor reading
        # Example: Read from /sys/class/thermal/thermal_zone0/temp
        
    def process_light_request(self, message_body):
        """
        Process a light telemetry request.
        
        Args:
            message_body: Dictionary containing the telemetry request
        """
        logger.info(f"Processing LIGHT request: {message_body}")
        sensor_key = message_body.get('SensorKey')
        start_date = message_body.get('StartDate')
        end_date = message_body.get('EndDate')
        
        # Placeholder: Implement light sensor reading logic here
        logger.info(f"Reading light data for sensor '{sensor_key}' from {start_date} to {end_date}")
        # TODO: Implement actual light sensor reading
        # Example: Read from GPIO-connected light sensor
        
    def process_cpu_request(self, message_body):
        """
        Process a CPU telemetry request.
        
        Args:
            message_body: Dictionary containing the telemetry request
        """
        logger.info(f"Processing CPU request: {message_body}")
        sensor_key = message_body.get('SensorKey')
        start_date = message_body.get('StartDate')
        end_date = message_body.get('EndDate')
        
        # Placeholder: Implement CPU metrics reading logic here
        logger.info(f"Reading CPU data for sensor '{sensor_key}' from {start_date} to {end_date}")
        # TODO: Implement actual CPU metrics reading
        # Example: Use psutil or read from /proc/stat
        
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
            
            # Extract SensorKey
            sensor_key = message_body.get('SensorKey', '').lower()
            
            # Route based on SensorKey using case statement
            if sensor_key == 'temperature':
                self.process_temperature_request(message_body)
            elif sensor_key == 'light':
                self.process_light_request(message_body)
            elif sensor_key == 'cpu':
                self.process_cpu_request(message_body)
            else:
                logger.warning(f"Unknown SensorKey: {sensor_key}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message as JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            
    def run(self):
        """
        Main loop to receive and process messages from Service Bus.
        """
        logger.info("Starting telemetry receiver service...")
        
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
    """Main entry point for the telemetry receiver service."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration from environment variables
    service_bus_namespace = os.getenv('SERVICE_BUS_NAMESPACE')
    subscription_name = os.getenv('SUBSCRIPTION_NAME', 'pi-telemetry-subscription')
    
    # Validate configuration
    if not service_bus_namespace:
        logger.error("SERVICE_BUS_NAMESPACE environment variable is not set")
        sys.exit(1)
        
    logger.info("=" * 60)
    logger.info("Raspberry Pi Telemetry Receiver Service")
    logger.info("=" * 60)
    logger.info(f"Service Bus Namespace: {service_bus_namespace}")
    logger.info(f"Subscription Name: {subscription_name}")
    logger.info(f"Started at: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    # Create and run the receiver
    receiver = TelemetryReceiver(service_bus_namespace, subscription_name)
    receiver.run()


if __name__ == "__main__":
    main()
