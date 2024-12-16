# `/v1/code/execute/python` API Documentation

## Overview
This endpoint allows users to execute Python code on the server. It accepts a Python code snippet, an optional timeout value, an optional webhook URL, and an optional ID. The code is executed in a secure environment, and the output (including stdout, stderr, and return value) is returned as a JSON response.

## Endpoint
**URL Path:** `/v1/code/execute/python`
**HTTP Method:** `POST`

## Request

### Headers
- `Authorization` (required): Bearer token for authentication.

### Body Parameters
- `code` (string, required): The Python code to be executed.
- `timeout` (integer, optional): The maximum execution time in seconds, between 1 and 300. Default is 30 seconds.
- `webhook_url` (string, optional): A URL to receive a webhook notification upon completion.
- `id` (string, optional): An identifier for the execution request.

### Example Request

```json
{
  "code": "print('Hello, World!')",
  "timeout": 10,
  "webhook_url": "https://example.com/webhook",
  "id": "abc123"
}
```

```bash
curl -X POST \
  https://api.example.com/v1/code/execute/python \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "code": "print('Hello, World!')",
    "timeout": 10,
    "webhook_url": "https://example.com/webhook",
    "id": "abc123"
  }'
```

## Response

### Success Response
**Status Code:** `200 OK`

```json
{
  "result": null,
  "stdout": "Hello, World!\n",
  "stderr": "",
  "exit_code": 0
}
```

### Error Responses
**Status Code:** `400 Bad Request`

```json
{
  "error": "Execution failed",
  "stdout": "",
  "exit_code": 1
}
```

**Status Code:** `408 Request Timeout`

```json
{
  "error": "Execution timed out after 10 seconds"
}
```

**Status Code:** `500 Internal Server Error`

```json
{
  "error": "Failed to parse execution result",
  "stdout": "...",
  "stderr": "...",
  "exit_code": 1
}
```

## Error Handling
- Missing or invalid `code` parameter: `400 Bad Request`
- Execution timeout: `408 Request Timeout`
- Execution failure or error: `400 Bad Request` (with error details in the response)
- Internal server error: `500 Internal Server Error`

## Usage Notes
- The `code` parameter should contain valid Python code.
- The `timeout` parameter is optional and defaults to 30 seconds if not provided.
- The `webhook_url` and `id` parameters are optional and can be used for tracking or notification purposes.

## Common Issues
- Code execution may fail due to syntax errors, runtime errors, or resource constraints.
- Long-running or resource-intensive code may be terminated due to the timeout.

## Best Practices
- Validate and sanitize user input to prevent code injection attacks.
- Set appropriate timeouts to prevent resource exhaustion.
- Implement rate limiting and access controls to prevent abuse.
- Log and monitor execution errors and failures for debugging and security purposes.