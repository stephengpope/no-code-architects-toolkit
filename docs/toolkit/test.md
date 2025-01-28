# NCA Toolkit Test API Endpoint

## 1. Overview

The `/v1/toolkit/test` endpoint is a part of the NCA Toolkit API and is designed to test the API setup. It creates a temporary file, uploads it to cloud storage, and then returns the upload URL. This endpoint serves as a simple test to ensure that the API is properly configured and can perform basic file operations and cloud storage interactions.

## 2. Endpoint

**URL Path:** `/v1/toolkit/test`
**HTTP Method:** `GET`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

This endpoint does not require any request body parameters.

### Example Request

```bash
curl -X GET \
  https://your-api-url.com/v1/toolkit/test \
  -H 'x-api-key: your-api-key'
```

## 4. Response

### Success Response

```json
{
  "endpoint": "/v1/toolkit/test",
  "code": 200,
  "id": null,
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "response": "https://cloud-storage.com/success.txt",
  "message": "success",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 0.123,
  "queue_time": 0.0,
  "total_time": 0.123,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

### Error Responses

**Status Code: 401 Unauthorized**

```json
{
  "code": 401,
  "message": "Unauthorized: Invalid or missing API key"
}
```

**Status Code: 500 Internal Server Error**

```json
{
  "code": 500,
  "message": "An error occurred while processing the request"
}
```

## 5. Error Handling

- **Missing or Invalid API Key (401 Unauthorized)**: If the `x-api-key` header is missing or invalid, the API will return a 401 Unauthorized error.
- **Internal Server Error (500)**: If an unexpected error occurs during the file creation, upload, or any other operation, the API will return a 500 Internal Server Error with the error message.

## 6. Usage Notes

This endpoint is primarily used for testing purposes and does not require any specific input parameters. It can be called to verify that the API is set up correctly and can perform basic operations.

## 7. Common Issues

- Incorrect or missing API key: Ensure that the `x-api-key` header is included with a valid API key.
- Temporary file creation or upload issues: If there are any issues with creating or uploading the temporary file, the API will return an error.

## 8. Best Practices

- Use this endpoint during the initial setup and testing phase of the API integration to ensure that the API is configured correctly.
- Regularly test the API setup using this endpoint to catch any potential issues or configuration changes that may affect the API's functionality.