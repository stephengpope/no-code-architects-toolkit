# Get All Jobs Status

## 1. Overview

The `/v1/toolkit/jobs/status` endpoint is part of the Toolkit API and is used to retrieve the status of all jobs within a specified time range. This endpoint fits into the overall API structure by providing a way to monitor and manage the jobs that have been submitted to the system. It is a part of the `v1_toolkit_jobs_status_bp` blueprint, which is registered in the main `app.py` file.

## 2. Endpoint

**URL Path:** `/v1/toolkit/jobs/status`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

- `since_seconds` (optional, number): The number of seconds to look back for jobs. If not provided, the default value is 600 seconds (10 minutes).

The JSON payload is completely optional. If no payload is provided or if the payload is empty, the endpoint will use the default value of 600 seconds.

### Example Request

```json
{
    "since_seconds": 3600
}
```

Or with no body:

```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     http://your-api-url/v1/toolkit/jobs/status
```

With body:

```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"since_seconds": 3600}' \
     http://your-api-url/v1/toolkit/jobs/status
```

## 4. Response

### Success Response

The response will be a JSON object containing the job statuses for all jobs within the specified time range. The response format follows the general response structure defined in `app.py`.

```json
{
    "code": 200,
    "id": null,
    "job_id": "job_id_value",
    "response": {
        "job_id_1": "job_status_1",
        "job_id_2": "job_status_2",
        ...
    },
    "message": "success",
    "run_time": 0.123,
    "queue_time": 0,
    "total_time": 0.123,
    "pid": 12345,
    "queue_id": 1234567890,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

### Error Responses

- **404 Not Found**: If the jobs directory is not found.

```json
{
    "code": 404,
    "id": null,
    "job_id": "job_id_value",
    "response": null,
    "message": "Jobs directory not found",
    "run_time": 0.123,
    "queue_time": 0,
    "total_time": 0.123,
    "pid": 12345,
    "queue_id": 1234567890,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

- **500 Internal Server Error**: If an exception occurs while retrieving the job statuses.

```json
{
    "code": 500,
    "id": null,
    "job_id": "job_id_value",
    "response": null,
    "message": "Failed to retrieve job statuses: Error message",
    "run_time": 0.123,
    "queue_time": 0,
    "total_time": 0.123,
    "pid": 12345,
    "queue_id": 1234567890,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

## 5. Error Handling

- Missing or invalid `x-api-key` header: The `authenticate` decorator will return a 401 Unauthorized error.
- Jobs directory not found: The endpoint will return a 404 Not Found error if the jobs directory is not found.
- Exception during job status retrieval: The endpoint will return a 500 Internal Server Error if an exception occurs while retrieving the job statuses.

The main `app.py` file includes error handling for queue overflow (429 Too Many Requests) and logging of job statuses (queued, running, done) using the `log_job_status` function.

## 6. Usage Notes

- This endpoint is useful for monitoring the status of jobs submitted to the system, especially when dealing with long-running or queued jobs.
- The `since_seconds` parameter can be adjusted to retrieve job statuses within a specific time range, allowing for more targeted monitoring.

## 7. Common Issues

- Providing an invalid `x-api-key` header will result in an authentication error.
- If the jobs directory is not found or an exception occurs during job status retrieval, the endpoint will return an error.

## 8. Best Practices

- Always include the `x-api-key` header with a valid API key for authentication.
- Monitor the job statuses regularly to keep track of the progress and completion of submitted jobs.
- Adjust the `since_seconds` parameter based on your monitoring requirements to retrieve job statuses within a specific time range.
- Implement error handling and logging mechanisms to track and troubleshoot any issues that may arise.