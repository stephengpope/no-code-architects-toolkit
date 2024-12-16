# NCA Toolkit Test API Endpoint

## 1. Overview

The `/v1/toolkit/test` endpoint is a part of the NCA Toolkit API and is designed to test the API setup. It creates a temporary file, uploads it to cloud storage, and then returns the upload URL. This endpoint serves as a simple test to ensure that the API is properly configured and functioning correctly.

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
  https://api.example.com/v1/toolkit/test \
  -H 'x-api-key: YOUR_API_KEY'
```

## 4. Response

### Success Response

```json
{
  "endpoint": "/v1/toolkit/test",
  "code": 200,
  "id": null,
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "response": "https://storage.example.com/success.txt",
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

**Status Code: 401 Unauthorized**

```json
{
  "code": 401,
  "message": "Unauthorized"
}
```

**Status Code: 500 Internal Server Error**

```json
{
  "code": 500,
  "id": null,
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "message": "Error message",
  "pid": 12345,
  "queue_id": 1234567890,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

## 5. Error Handling

- **401 Unauthorized**: This error occurs when the provided `x-api-key` is missing or invalid.
- **500 Internal Server Error**: This error occurs when an unexpected exception is raised during the execution of the endpoint.

## 6. Usage Notes

This endpoint is primarily used for testing purposes and does not require any specific input parameters. It can be called to verify that the API is set up correctly and can successfully upload files to cloud storage.

## 7. Common Issues

- Incorrect or missing `x-api-key` header.
- Temporary file creation or upload failures due to permissions or storage issues.

## 8. Best Practices

- Use this endpoint as a simple health check to ensure the API is functioning correctly before attempting more complex operations.
- Regularly test the API setup, especially after updates or changes to the environment.
- Monitor the API logs for any errors or exceptions that may occur during the test.