import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";

interface MCPTool {
  name: string;
  description: string;
  inputSchema: {
    type: string;
    properties: Record<string, any>;
    required: string[];
  };
}

interface MCPServerInfo {
  protocolVersion: string;
  serverInfo: {
    name: string;
    version: string;
  };
  capabilities: {
    tools: Record<string, any>;
  };
}

const MCP_TOOLS: MCPTool[] = [
  {
    name: "getTelemetry",
    description: "Request telemetry data from a sensor for a specified time range",
    inputSchema: {
      type: "object",
      properties: {
        sensorKey: {
          type: "string",
          description: "The identifier for the sensor"
        },
        startDate: {
          type: "string",
          description: "The start date for the telemetry request (ISO 8601 format)"
        },
        endDate: {
          type: "string",
          description: "The end date for the telemetry request (ISO 8601 format)"
        }
      },
      required: ["sensorKey", "startDate", "endDate"]
    }
  },
  {
    name: "sendAction",
    description: "Send an action command to be processed by the service",
    inputSchema: {
      type: "object",
      properties: {
        actionType: {
          type: "string",
          description: "The action key to indicate what action is being requested"
        },
        actionSpec: {
          type: "string",
          description: "A JSON string containing the action specification to be processed"
        }
      },
      required: ["actionType", "actionSpec"]
    }
  }
];

export async function mcpServerInfo(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
  context.log(`MCP server info requested`);

  const serverInfo: MCPServerInfo = {
    protocolVersion: "0.1.0",
    serverInfo: {
      name: "pi-chat-mcp-server",
      version: "1.0.0"
    },
    capabilities: {
      tools: {}
    }
  };

  return {
    status: 200,
    headers: {
      "Content-Type": "application/json"
    },
    jsonBody: serverInfo
  };
}

export async function mcpListTools(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
  context.log(`MCP list tools requested`);

  return {
    status: 200,
    headers: {
      "Content-Type": "application/json"
    },
    jsonBody: {
      tools: MCP_TOOLS
    }
  };
}

app.http('mcpServerInfo', {
  methods: ['GET'],
  route: 'mcp/info',
  authLevel: 'anonymous',
  handler: mcpServerInfo
});

app.http('mcpListTools', {
  methods: ['GET'],
  route: 'mcp/tools',
  authLevel: 'anonymous',
  handler: mcpListTools
});
