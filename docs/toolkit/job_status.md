# Job Status Endpoint Documentation

## 1. Overview

The `/v1/toolkit/job/status` endpoint is part of the Toolkit API and is used to retrieve the status of a specific job. It fits into the overall API structure as a utility endpoint for monitoring and managing jobs submitted to the various media processing endpoints.

## 2. Endpoint

**URL Path:** `/v1/toolkit/job/status`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following parameter:

- `job_id` (string, required): The unique identifier of the job for which the status is requested.

The `validate_payload` directive in the routes file enforces the following JSON schema for the request body:

```python
{
    "type": "object",
    "properties": {
        "job_id": {
            "type": "string"
        }
    },
    "required": ["job_id"],
}
```

### Example Request

```json
{
    "job_id": "e6d7f3c0-9c9f-4b8a-b7c3-f0e3c9f6b9d7"
}
```

```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"job_id": "e6d7f3c0-9c9f-4b8a-b7c3-f0e3c9f6b9d7"}' \
     http://your-api-endpoint/v1/toolkit/job/status
```

## 4. Response

### Success Response

The success response will contain the job status file content directly, as shown in the example response from `app.py`:

```json
{
    "endpoint": "/v1/toolkit/job/status",
    "code": 200,
    "id": null,
    "job_id": "e6d7f3c0-9c9f-4b8a-b7c3-f0e3c9f6b9d7",
    "response": {
        "job_status": "done",
        "job_id": "e6d7f3c0-9c9f-4b8a-b7c3-f0e3c9f6b9d7",
        "queue_id": 140368864456064,
        "process_id": 123456,
        "response": {
            "endpoint": "/v1/media/transcribe",
            "code": 200,
            "id": "transcribe_job_123",
            "job_id": "e6d7f3c0-9c9f-4b8a-b7c3-f0e3c9f6b9d7",
            "response": "Transcription completed successfully.",
            "message": "success",
            "pid": 123456,
            "queue_id": 140368864456064,
            "run_time": 5.234,
            "queue_time": 1.123,
            "total_time": 6.357,
            "queue_length": 0,
            "build_number": "1.0.0"
        }
    },
    "message": "success",
    "pid": 123456,
    "queue_id": 140368864456064,
    "run_time": 0.001,
    "queue_time": 0.0,
    "total_time": 0.001,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

### Error Responses

- **404 Not Found**: If the job with the provided `job_id` is not found, the response will be:

```json
{
    "error": "Job not found",
    "job_id": "e6d7f3c0-9c9f-4b8a-b7c3-f0e3c9f6b9d7"
}
```

- **500 Internal Server Error**: If an unexpected error occurs while retrieving the job status, the response will be:

```json
{
    "error": "Failed to retrieve job status: <error_message>",
    "code": 500
}
```

## 5. Error Handling

- **Missing or Invalid Parameters**: If the `job_id` parameter is missing or invalid, the request will be rejected with a 400 Bad Request error.
- **Job Not Found**: If the job with the provided `job_id` is not found, a 404 Not Found error will be returned.
- **Unexpected Errors**: Any unexpected errors that occur during the retrieval of the job status will result in a 500 Internal Server Error response.

The main application context (`app.py`) includes error handling for queue overflow situations, where a 429 Too Many Requests error is returned if the maximum queue length is reached.

## 6. Usage Notes

- Ensure that you have a valid API key for authentication.
- The `job_id` parameter must be a valid UUID string representing an existing job.
- This endpoint does not perform any media processing; it only retrieves the status of a previously submitted job.

## 7. Common Issues

- Providing an invalid or non-existent `job_id`.
- Attempting to retrieve the status of a job that has already been processed and removed from the system.

## 8. Best Practices

- Use this endpoint to monitor the progress of long-running jobs or to check the status of completed jobs.
- Implement proper error handling in your client application to handle different error scenarios, such as job not found or unexpected errors.
- Consider rate-limiting or implementing a queue system on the client side to avoid overwhelming the API with too many requests.