# Execute Python Code Endpoint

## 1. Overview

The `/v1/code/execute/python` endpoint allows users to execute Python code on the server. This endpoint is part of the version 1 API and is registered in the main `app.py` file. It is designed to provide a secure and controlled environment for executing Python code, with features like input validation, timeout handling, and output capturing.

## 2. Endpoint

**URL Path:** `/v1/code/execute/python`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

- `code` (required, string): The Python code to be executed.
- `timeout` (optional, integer): The maximum execution time in seconds, between 1 and 300. Default is 30 seconds.
- `webhook_url` (optional, string): The URL to send the execution results to as a webhook.
- `id` (optional, string): An identifier for the request.

#### Example Request

```json
{
    "code": "print('Hello, World!')",
    "timeout": 10,
    "webhook_url": "https://example.com/webhook",
    "id": "request-123"
}
```

```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"code": "print('Hello, World!')", "timeout": 10, "webhook_url": "https://example.com/webhook", "id": "request-123"}' \
     http://localhost:8080/v1/code/execute/python
```

## 4. Response

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
    "error": "Error message",
    "stdout": "Output from the executed code",
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
    "stdout": "Output from the executed code",
    "stderr": "Error output from the executed code",
    "exit_code": 1
}
```

## 5. Error Handling

- Missing or invalid parameters will result in a `400 Bad Request` error.
- If the execution times out, a `408 Request Timeout` error is returned.
- Any other execution errors or server-side errors will result in a `500 Internal Server Error`.
- The main application context handles errors related to the task queue, such as reaching the maximum queue length (`429 Too Many Requests`).

## 6. Usage Notes

- The executed code runs in a sandboxed environment, with limited access to system resources.
- The code's output (both stdout and stderr) is captured and returned in the response.
- If a `webhook_url` is provided, the execution results will be sent to that URL as a webhook.

## 7. Common Issues

- Executing code that takes too long or consumes too many resources may result in a timeout or server error.
- Code that attempts to access restricted system resources or perform unauthorized operations may fail or produce unexpected results.

## 8. Best Practices

- Always validate and sanitize user input before executing code.
- Set an appropriate timeout value based on the expected execution time of the code.
- Monitor the server's resource usage and adjust the maximum queue length or other limits as needed.
- Implement additional security measures, such as code sandboxing or whitelisting, to prevent malicious code execution.