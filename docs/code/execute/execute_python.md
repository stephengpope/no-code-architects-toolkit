# Execute Python Code Endpoint

## 1. Overview

The `/v1/code/execute/python` endpoint allows users to execute Python code on the server. This endpoint is part of the version 1.0 API structure defined in `app.py`. It is designed to provide a secure and controlled environment for executing Python code, with features like input validation, output capturing, and timeout handling.

## 2. Endpoint

**URL Path:** `/v1/code/execute/python`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

- `code` (string, required): The Python code to be executed.
- `timeout` (integer, optional): The maximum execution time in seconds, between 1 and 300. Default is 30 seconds.
- `webhook_url` (string, optional): The URL to receive the execution result via a webhook.
- `id` (string, optional): A unique identifier for the request.

The `validate_payload` directive in the routes file enforces the following JSON schema for the request body:

```json
{
    "type": "object",
    "properties": {
        "code": {"type": "string"},
        "timeout": {"type": "integer", "minimum": 1, "maximum": 300},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["code"],
    "additionalProperties": False
}
```

### Example Request

**Request Payload:**

```json
{
    "code": "print('Hello, World!')",
    "timeout": 10,
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id"
}
```

**cURL Command:**

```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"code": "print('Hello, World!')", "timeout": 10, "webhook_url": "https://example.com/webhook", "id": "unique-request-id"}' \
     http://your-api-endpoint/v1/code/execute/python
```

## 4. Response

### Success Response

The success response follows the general response format defined in `app.py`. Here's an example:

```json
{
    "endpoint": "/v1/code/execute/python",
    "code": 200,
    "id": "unique-request-id",
    "job_id": "generated-job-id",
    "response": {
        "result": null,
        "stdout": "Hello, World!\n",
        "stderr": "",
        "exit_code": 0
    },
    "message": "success",
    "pid": 12345,
    "queue_id": 1234567890,
    "run_time": 0.123,
    "queue_time": 0.0,
    "total_time": 0.123,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

### Error Responses

#### Missing or Invalid Parameters

**Status Code:** 400 Bad Request

```json
{
    "error": "Missing or invalid parameters",
    "stdout": "",
    "exit_code": 400
}
```

#### Execution Error

**Status Code:** 400 Bad Request

```json
{
    "error": "Error message from the executed code",
    "stdout": "Output from the executed code",
    "exit_code": 400
}
```

#### Execution Timeout

**Status Code:** 408 Request Timeout

```json
{
    "error": "Execution timed out after 10 seconds"
}
```

#### Internal Server Error

**Status Code:** 500 Internal Server Error

```json
{
    "error": "An internal server error occurred",
    "stdout": "",
    "stderr": "",
    "exit_code": 500
}
```

## 5. Error Handling

The endpoint handles various types of errors, including:

- Missing or invalid parameters (400 Bad Request)
- Execution errors, such as syntax errors or exceptions (400 Bad Request)
- Execution timeout (408 Request Timeout)
- Internal server errors (500 Internal Server Error)

The main application context (`app.py`) also includes error handling for queue overload (429 Too Many Requests) and other general errors.

## 6. Usage Notes

- The executed code runs in a sandboxed environment, with limited access to system resources.
- The code execution is limited to a maximum of 300 seconds (5 minutes) by default, but this can be adjusted using the `timeout` parameter.
- The execution result, including stdout, stderr, and the return value, is captured and returned in the response.
- If a `webhook_url` is provided, the execution result will also be sent to the specified webhook.

## 7. Common Issues

- Attempting to execute code that accesses restricted resources or performs disallowed operations may result in an execution error.
- Long-running or resource-intensive code may trigger the execution timeout.
- Providing an invalid `webhook_url` will prevent the execution result from being delivered to the specified webhook.

## 8. Best Practices

- Always validate and sanitize user input to prevent code injection attacks.
- Set an appropriate timeout value based on the expected execution time of the code.
- Monitor the execution logs for any errors or unexpected behavior.
- Implement rate limiting or queue management to prevent abuse or overload of the endpoint.
- Consider implementing additional security measures, such as code sandboxing or whitelisting/blacklisting certain operations or modules.
