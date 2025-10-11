import { getTelemetry } from '../src/getTelemetry';
import { HttpRequest, InvocationContext } from '@azure/functions';

// Mock the ServiceBusClient
jest.mock('@azure/service-bus', () => ({
  ServiceBusClient: jest.fn().mockImplementation(() => ({
    createSender: jest.fn().mockReturnValue({
      sendMessages: jest.fn().mockResolvedValue(undefined),
      close: jest.fn().mockResolvedValue(undefined)
    }),
    close: jest.fn().mockResolvedValue(undefined)
  }))
}));

describe('getTelemetry', () => {
  let mockContext: InvocationContext;

  beforeEach(() => {
    mockContext = {
      log: jest.fn(),
      error: jest.fn()
    } as unknown as InvocationContext;

    process.env.ServiceBusConnectionString = 'Endpoint=sb://test.servicebus.windows.net/;SharedAccessKeyName=test;SharedAccessKey=testkey';
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return 400 when sensorKey is missing', async () => {
    const mockRequest = {
      json: jest.fn().mockResolvedValue({
        startDate: '2024-01-01T00:00:00Z',
        endDate: '2024-01-31T23:59:59Z'
      }),
      url: 'http://localhost/api/getTelemetry'
    } as unknown as HttpRequest;

    const response = await getTelemetry(mockRequest, mockContext);

    expect(response.status).toBe(400);
    expect(response.jsonBody).toEqual({
      error: 'Invalid request. Required fields: sensorKey, startDate, endDate'
    });
  });

  it('should return 400 when startDate is missing', async () => {
    const mockRequest = {
      json: jest.fn().mockResolvedValue({
        sensorKey: 'sensor-123',
        endDate: '2024-01-31T23:59:59Z'
      }),
      url: 'http://localhost/api/getTelemetry'
    } as unknown as HttpRequest;

    const response = await getTelemetry(mockRequest, mockContext);

    expect(response.status).toBe(400);
    expect(response.jsonBody).toEqual({
      error: 'Invalid request. Required fields: sensorKey, startDate, endDate'
    });
  });

  it('should return 400 when endDate is missing', async () => {
    const mockRequest = {
      json: jest.fn().mockResolvedValue({
        sensorKey: 'sensor-123',
        startDate: '2024-01-01T00:00:00Z'
      }),
      url: 'http://localhost/api/getTelemetry'
    } as unknown as HttpRequest;

    const response = await getTelemetry(mockRequest, mockContext);

    expect(response.status).toBe(400);
    expect(response.jsonBody).toEqual({
      error: 'Invalid request. Required fields: sensorKey, startDate, endDate'
    });
  });

  it('should return 200 when request is valid', async () => {
    const mockRequest = {
      json: jest.fn().mockResolvedValue({
        sensorKey: 'sensor-123',
        startDate: '2024-01-01T00:00:00Z',
        endDate: '2024-01-31T23:59:59Z'
      }),
      url: 'http://localhost/api/getTelemetry'
    } as unknown as HttpRequest;

    const response = await getTelemetry(mockRequest, mockContext);

    expect(response.status).toBe(200);
    expect(response.jsonBody).toEqual({
      success: true,
      message: 'Telemetry request submitted successfully'
    });
  });

  it('should return 500 when ServiceBusConnectionString is not configured', async () => {
    delete process.env.ServiceBusConnectionString;

    const mockRequest = {
      json: jest.fn().mockResolvedValue({
        sensorKey: 'sensor-123',
        startDate: '2024-01-01T00:00:00Z',
        endDate: '2024-01-31T23:59:59Z'
      }),
      url: 'http://localhost/api/getTelemetry'
    } as unknown as HttpRequest;

    const response = await getTelemetry(mockRequest, mockContext);

    expect(response.status).toBe(500);
    expect(response.jsonBody).toEqual({
      error: 'Service Bus connection not configured'
    });
  });
});
