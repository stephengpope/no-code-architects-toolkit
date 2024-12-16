# `/v1/code/execute/python` API Documentation

## Overview
This endpoint allows users to execute Python code on the server. The code is executed in a secure, sandboxed environment with a configurable timeout. The endpoint returns the output (stdout, stderr) and the return value of the executed code.

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
- `id` (string, optional): A unique identifier for the execution request.

### Example Request

```json
{
    "code": "print('Hello, World!')",
    "timeout": 10
}
```

```bash
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"code": "print('Hello, World!')", "timeout": 10}' \
     https://api.example.com/v1/code/execute/python
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
    "error": "Failed to parse execution result"
}
```

## Error Handling
- Missing or invalid `code` parameter: `400 Bad Request`
- Execution timeout: `408 Request Timeout`
- Execution failure or error: `400 Bad Request` with error details
- Internal server error: `500 Internal Server Error`

## Usage Notes
- The executed code runs in a sandboxed environment, so it cannot access external resources or make system calls.
- The `timeout` parameter can be used to limit the execution time and prevent long-running or infinite loops.
- The `webhook_url` and `id` parameters are optional and can be used for tracking and notification purposes.

## Common Issues
- Code that takes too long to execute may be terminated due to the timeout.
- Code that attempts to access external resources or make system calls will fail.
- Large output (stdout, stderr) may be truncated or cause performance issues.

## Best Practices
- Keep the executed code concise and focused on the specific task.
- Use the `timeout` parameter to prevent long-running or infinite loops.
- Validate and sanitize user input to prevent code injection attacks.
- Monitor and limit the usage of this endpoint to prevent abuse or resource exhaustion.