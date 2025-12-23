import os
import json
import logging
import secrets
from flask import Flask, render_template, request, jsonify, session
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    SystemMessage,
    UserMessage,
    AssistantMessage,
    ChatCompletionsToolDefinition,
    FunctionDefinition,
    ToolMessage,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from applicationinsights import TelemetryClient
from applicationinsights.flask.ext import AppInsights
import requests
from datetime import datetime

app = Flask(__name__)
# Use a secure random secret key if not provided in environment
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application Insights configuration
app_insights_connection_string = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
if app_insights_connection_string:
    # Add Azure Monitor handler for logging
    logger.addHandler(AzureLogHandler(connection_string=app_insights_connection_string))
    # Initialize Application Insights for Flask
    app_insights = AppInsights(app)
    FlaskMiddleware(
        app,
        exporter=None,
        sampler=None,
    )
    telemetry_client = TelemetryClient(app_insights_connection_string)
    logger.info("Application Insights initialized successfully")
else:
    logger.warning("Application Insights not configured - APPLICATIONINSIGHTS_CONNECTION_STRING not set")
    app_insights = None
    telemetry_client = None

# Azure AI Foundry configuration
azure_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
azure_api_key = os.environ.get('AZURE_OPENAI_API_KEY')
azure_deployment_name = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o-mini')

# Azure Function MCP endpoints configuration
function_app_url = os.environ.get('FUNCTION_APP_URL')
function_app_key = os.environ.get('FUNCTION_APP_KEY')

# Initialize Azure AI client
if azure_endpoint and azure_api_key:
    client = ChatCompletionsClient(
        endpoint=azure_endpoint,
        credential=AzureKeyCredential(azure_api_key)
    )
    logger.info(f"Azure AI client initialized with endpoint: {azure_endpoint}")
else:
    client = None
    logger.warning("Azure AI client not initialized - missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY")

# Define MCP tools for function calling
tools = [
    ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_telemetry",
            description="Retrieve telemetry data from a sensor. Use this to get temperature, light, or CPU readings from the Raspberry Pi.",
            parameters={
                "type": "object",
                "properties": {
                    "sensor_key": {
                        "type": "string",
                        "description": "The type of sensor to query (e.g., 'Temperature', 'Light', 'CPU')",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date for telemetry data in ISO 8601 format (e.g., '2025-01-01T00:00:00Z')",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for telemetry data in ISO 8601 format (e.g., '2025-01-02T00:00:00Z')",
                    },
                },
                "required": ["sensor_key", "start_date", "end_date"],
            },
        )
    ),
    ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="send_action",
            description="Send an action command to the Raspberry Pi. Use this to control devices like camera, LEDs, or other actuators.",
            parameters={
                "type": "object",
                "properties": {
                    "action_type": {
                        "type": "string",
                        "description": "The type of action to perform (e.g., 'Camera', 'LED', 'Servo')",
                    },
                    "action_spec": {
                        "type": "string",
                        "description": "JSON string specifying the action details (e.g., '{\"operation\": \"capture\", \"resolution\": \"1920x1080\"}')",
                    },
                },
                "required": ["action_type", "action_spec"],
            },
        )
    ),
]


def call_mcp_function(function_name, arguments):
    """Call Azure Function MCP endpoints"""
    if not function_app_url or not function_app_key:
        logger.error("Function App URL or Key not configured")
        return {"error": "MCP endpoints not configured"}
    
    try:
        if function_name == "get_telemetry":
            url = f"{function_app_url}/api/GetTelemetry"
            payload = {
                "SensorKey": arguments.get("sensor_key"),
                "StartDate": arguments.get("start_date"),
                "EndDate": arguments.get("end_date")
            }
        elif function_name == "send_action":
            url = f"{function_app_url}/api/SendAction"
            payload = {
                "ActionType": arguments.get("action_type"),
                "ActionSpec": arguments.get("action_spec")
            }
        else:
            return {"error": f"Unknown function: {function_name}"}
        
        headers = {
            "Content-Type": "application/json",
            "x-functions-key": function_app_key
        }
        
        logger.info(f"Calling MCP function {function_name} with payload: {payload}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"MCP function {function_name} response: {result}")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling MCP function {function_name}: {str(e)}")
        return {"error": f"Failed to call {function_name}: {str(e)}"}


@app.route('/')
def index():
    """Render the chat interface"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests with Azure AI Foundry"""
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not client:
            return jsonify({'error': 'Azure AI client not configured'}), 500
        
        # Log the request
        logger.info(f"Received chat message: {user_message}")
        if telemetry_client:
            telemetry_client.track_event('chat_request', {'message_length': len(user_message)})
        
        # Build messages for AI
        messages = [
            SystemMessage(content="You are a helpful assistant that can interact with a Raspberry Pi system. You can retrieve telemetry data from sensors (Temperature, Light, CPU) and send action commands to control devices. When users ask about sensor data or want to control devices, use the appropriate functions to help them.")
        ]
        
        # Add conversation history
        for msg in conversation_history:
            if msg['role'] == 'user':
                messages.append(UserMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                messages.append(AssistantMessage(content=msg['content']))
        
        # Add current user message
        messages.append(UserMessage(content=user_message))
        
        # Call Azure AI with function calling capability
        response = client.complete(
            messages=messages,
            model=azure_deployment_name,
            tools=tools if function_app_url and function_app_key else None,
        )
        
        # Handle function calls
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            choice = response.choices[0]
            
            # If the model wants to call a function
            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                logger.info(f"Model requested function calls: {len(choice.message.tool_calls)}")
                
                # Add the assistant's message with tool calls to history
                messages.append(AssistantMessage(
                    content=choice.message.content or "",
                    tool_calls=choice.message.tool_calls
                ))
                
                # Execute each function call
                for tool_call in choice.message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Executing function: {function_name} with args: {function_args}")
                    
                    # Call the MCP function
                    function_result = call_mcp_function(function_name, function_args)
                    
                    # Add function result to messages
                    messages.append(ToolMessage(
                        tool_call_id=tool_call.id,
                        content=json.dumps(function_result)
                    ))
                
                # Get the next response from the model
                response = client.complete(
                    messages=messages,
                    model=azure_deployment_name,
                    tools=tools if function_app_url and function_app_key else None,
                )
                iteration += 1
            else:
                # No more function calls, return the final response
                break
        
        assistant_message = response.choices[0].message.content
        
        # Log the response
        logger.info(f"Generated response: {assistant_message[:100]}...")
        if telemetry_client:
            telemetry_client.track_event('chat_response', {
                'response_length': len(assistant_message),
                'function_calls_made': iteration
            })
        
        return jsonify({
            'response': assistant_message,
            'finish_reason': response.choices[0].finish_reason
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        if telemetry_client:
            telemetry_client.track_exception()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'azure_ai_configured': client is not None,
        'app_insights_configured': app_insights is not None,
        'mcp_endpoints_configured': function_app_url is not None and function_app_key is not None,
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(status)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
