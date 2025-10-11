import { sendAction } from '../src/sendAction';
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

describe('sendAction', () => {
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

  it('should return 400 when actionType is missing', async () => {
    const mockRequest = {
      json: jest.fn().mockResolvedValue({
        actionSpec: '{"key": "value"}'
      }),
      url: 'http://localhost/api/sendAction'
    } as unknown as HttpRequest;

    const response = await sendAction(mockRequest, mockContext);

    expect(response.status).toBe(400);
    expect(response.jsonBody).toEqual({
      error: 'Invalid request. Required fields: actionType, actionSpec'
    });
  });

  it('should return 400 when actionSpec is missing', async () => {
    const mockRequest = {
      json: jest.fn().mockResolvedValue({
        actionType: 'test-action'
      }),
      url: 'http://localhost/api/sendAction'
    } as unknown as HttpRequest;

    const response = await sendAction(mockRequest, mockContext);

    expect(response.status).toBe(400);
    expect(response.jsonBody).toEqual({
      error: 'Invalid request. Required fields: actionType, actionSpec'
    });
  });

  it('should return 200 when request is valid', async () => {
    const mockRequest = {
      json: jest.fn().mockResolvedValue({
        actionType: 'test-action',
        actionSpec: '{"key": "value"}'
      }),
      url: 'http://localhost/api/sendAction'
    } as unknown as HttpRequest;

    const response = await sendAction(mockRequest, mockContext);

    expect(response.status).toBe(200);
    expect(response.jsonBody).toEqual({
      success: true,
      message: 'Action request submitted successfully'
    });
  });

  it('should return 500 when ServiceBusConnectionString is not configured', async () => {
    delete process.env.ServiceBusConnectionString;

    const mockRequest = {
      json: jest.fn().mockResolvedValue({
        actionType: 'test-action',
        actionSpec: '{"key": "value"}'
      }),
      url: 'http://localhost/api/sendAction'
    } as unknown as HttpRequest;

    const response = await sendAction(mockRequest, mockContext);

    expect(response.status).toBe(500);
    expect(response.jsonBody).toEqual({
      error: 'Service Bus connection not configured'
    });
  });
});
