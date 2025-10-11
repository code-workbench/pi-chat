import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { ServiceBusClient } from "@azure/service-bus";

interface TelemetryRequest {
  sensorKey: string;
  startDate: string;
  endDate: string;
}

export async function getTelemetry(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
  context.log(`Http function processed request for url "${request.url}"`);

  try {
    // Parse the request body
    const body = await request.json() as TelemetryRequest;

    // Validate required fields
    if (!body || !body.sensorKey || !body.startDate || !body.endDate) {
      return {
        status: 400,
        jsonBody: {
          error: "Invalid request. Required fields: sensorKey, startDate, endDate"
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
    const sender = serviceBusClient.createSender("Telemetry");

    try {
      // Send message to Telemetry topic
      await sender.sendMessages({
        body: body,
        contentType: "application/json"
      });

      context.log(`Message sent to Telemetry topic for sensor: ${body.sensorKey}`);

      return {
        status: 200,
        jsonBody: {
          success: true,
          message: "Telemetry request submitted successfully"
        }
      };
    } finally {
      // Clean up
      await sender.close();
      await serviceBusClient.close();
    }
  } catch (error) {
    context.error("Error processing telemetry request:", error);
    return {
      status: 500,
      jsonBody: {
        error: "Failed to process telemetry request",
        details: error instanceof Error ? error.message : String(error)
      }
    };
  }
}

app.http('getTelemetry', {
  methods: ['POST'],
  authLevel: 'function',
  handler: getTelemetry
});
