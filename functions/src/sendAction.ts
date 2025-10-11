import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { ServiceBusClient } from "@azure/service-bus";

interface ActionRequest {
  actionType: string;
  actionSpec: string;
}

export async function sendAction(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
  context.log(`Http function processed request for url "${request.url}"`);

  try {
    // Parse the request body
    const body = await request.json() as ActionRequest;

    // Validate required fields
    if (!body || !body.actionType || !body.actionSpec) {
      return {
        status: 400,
        jsonBody: {
          error: "Invalid request. Required fields: actionType, actionSpec"
        }
      };
    }

    // Get Service Bus connection string from environment
    const connectionString = process.env.ServiceBusConnectionString;
    if (!connectionString) {
      context.error("ServiceBusConnectionString is not configured");
      return {
        status: 500,
        jsonBody: {
          error: "Service Bus connection not configured"
        }
      };
    }

    // Create Service Bus client and sender
    const serviceBusClient = new ServiceBusClient(connectionString);
    const sender = serviceBusClient.createSender("Action");

    try {
      // Send message to Action topic
      await sender.sendMessages({
        body: body,
        contentType: "application/json"
      });

      context.log(`Message sent to Action topic for actionType: ${body.actionType}`);

      return {
        status: 200,
        jsonBody: {
          success: true,
          message: "Action request submitted successfully"
        }
      };
    } finally {
      // Clean up
      await sender.close();
      await serviceBusClient.close();
    }
  } catch (error) {
    context.error("Error processing action request:", error);
    return {
      status: 500,
      jsonBody: {
        error: "Failed to process action request",
        details: error instanceof Error ? error.message : String(error)
      }
    };
  }
}

app.http('sendAction', {
  methods: ['POST'],
  authLevel: 'function',
  handler: sendAction
});
