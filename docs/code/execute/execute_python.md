# Execute Python Code Endpoint

## 1. Overview

The `/v1/code/execute/python` endpoint allows users to execute Python code on the server. This endpoint is part of the `v1` API and is registered in the `app.py` file. It is designed to provide a secure and controlled environment for executing Python code, with features like input validation, timeout handling, and output capturing.

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

The `validate_payload` decorator in the routes file enforces the following JSON schema for the request body:

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

```json
{
    "code": "print('Hello, World!')",
    "timeout": 10,
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id"
}
```

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
    "pid": 1234,
    "queue_id": 12345678,
    "run_time": 0.123,
    "queue_time": 0.0,
    "total_time": 0.123,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

### Error Responses

- **400 Bad Request**:
  - Example: `{"error": "Execution failed", "stdout": "", "exit_code": 1}`
  - Reason: The Python code execution failed, or there was an error in the user's code.

- **408 Request Timeout**:
  - Example: `{"error": "Execution timed out after 10 seconds"}`
  - Reason: The Python code execution exceeded the specified timeout.

- **500 Internal Server Error**:
  - Example: `{"error": "Failed to parse execution result"}`
  - Reason: An internal error occurred while parsing the execution result.

## 5. Error Handling

The endpoint handles the following common errors:

- **Missing or invalid parameters**: If the request body is missing or contains invalid parameters, a `400 Bad Request` error is returned.
- **Execution timeout**: If the Python code execution exceeds the specified timeout, a `408 Request Timeout` error is returned.
- **Internal errors**: If an internal error occurs during code execution or result parsing, a `500 Internal Server Error` is returned.

Additionally, the main application context (`app.py`) includes error handling for queue overload. If the maximum queue length is reached, a `429 Too Many Requests` error is returned.

## 6. Usage Notes

- The Python code is executed in a sandboxed environment, with limited access to system resources and libraries.
- The execution output (stdout and stderr) is captured and included in the response.
- The return value of the executed code is included in the response if the execution is successful.
- The `webhook_url` parameter is optional and can be used to receive the execution result via a webhook.

## 7. Common Issues

- **Syntax errors or exceptions in the user's code**: These will result in a `400 Bad Request` error, with the error message and traceback included in the response.
- **Infinite loops or long-running code**: The execution will be terminated after the specified timeout, resulting in a `408 Request Timeout` error.
- **Excessive resource usage**: The sandboxed environment may impose limits on memory, CPU, or other resources, which could cause the execution to fail.

## 8. Best Practices

- **Validate user input**: Always validate and sanitize user input to prevent code injection or other security vulnerabilities.
- **Set appropriate timeouts**: Choose a reasonable timeout value based on the expected complexity of the code to be executed.
- **Monitor resource usage**: Keep an eye on the resource usage of the execution environment to prevent excessive consumption or denial of service attacks.
- **Implement rate limiting**: Consider implementing rate limiting to prevent abuse or overload of the endpoint.
- **Log and monitor errors**: Ensure that errors are properly logged and monitored for debugging and security purposes.