# FFmpeg Compose API Endpoint

## 1. Overview

The `/v1/ffmpeg/compose` endpoint is a part of the Flask API application and is designed to provide a flexible and powerful way to compose and manipulate media files using FFmpeg. This endpoint allows users to specify input files, filters, and output options, enabling a wide range of media processing tasks such as transcoding, concatenation, and video editing.

## 2. Endpoint

- **URL Path**: `/v1/ffmpeg/compose`
- **HTTP Method**: `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body should be a JSON object with the following properties:

- `inputs` (required, array): An array of input file objects, each containing:
  - `file_url` (required, string): The URL of the input file.
  - `options` (optional, array): An array of input file options, each containing:
    - `option` (required, string): The FFmpeg option to apply.
    - `argument` (optional, string, number, or null): The argument for the option.
- `filters` (optional, array): An array of filter objects, each containing:
  - `filter` (required, string): The FFmpeg filter to apply.
- `outputs` (required, array): An array of output file objects, each containing:
  - `options` (required, array): An array of output file options, each containing:
    - `option` (required, string): The FFmpeg option to apply.
    - `argument` (optional, string, number, or null): The argument for the option.
- `global_options` (optional, array): An array of global option objects, each containing:
  - `option` (required, string): The FFmpeg global option to apply.
  - `argument` (optional, string, number, or null): The argument for the option.
- `metadata` (optional, object): An object specifying which metadata to include in the response, with the following properties:
  - `thumbnail` (optional, boolean): Whether to include a thumbnail for the output file.
  - `filesize` (optional, boolean): Whether to include the file size of the output file.
  - `duration` (optional, boolean): Whether to include the duration of the output file.
  - `bitrate` (optional, boolean): Whether to include the bitrate of the output file.
  - `encoder` (optional, boolean): Whether to include the encoder used for the output file.
- `webhook_url` (required, string): The URL to send the response to.
- `id` (required, string): A unique identifier for the request.

### Example Request

```json
{
  "inputs": [
    {
      "file_url": "https://example.com/video1.mp4",
      "options": [
        {
          "option": "-ss",
          "argument": 10
        },
        {
          "option": "-t",
          "argument": 20
        }
      ]
    },
    {
      "file_url": "https://example.com/video2.mp4"
    }
  ],
  "filters": [
    {
      "filter": "scale=640:480"
    }
  ],
  "outputs": [
    {
      "options": [
        {
          "option": "-c:v",
          "argument": "libx264"
        },
        {
          "option": "-crf",
          "argument": 23
        }
      ]
    }
  ],
  "global_options": [
    {
      "option": "-y"
    }
  ],
  "metadata": {
    "thumbnail": true,
    "filesize": true,
    "duration": true,
    "bitrate": true,
    "encoder": true
  },
  "webhook_url": "https://example.com/webhook",
  "id": "unique-request-id"
}
```

```bash
curl -X POST \
  https://api.example.com/v1/ffmpeg/compose \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "inputs": [
      {
        "file_url": "https://example.com/video1.mp4",
        "options": [
          {
            "option": "-ss",
            "argument": 10
          },
          {
            "option": "-t",
            "argument": 20
          }
        ]
      },
      {
        "file_url": "https://example.com/video2.mp4"
      }
    ],
    "filters": [
      {
        "filter": "scale=640:480"
      }
    ],
    "outputs": [
      {
        "options": [
          {
            "option": "-c:v",
            "argument": "libx264"
          },
          {
            "option": "-crf",
            "argument": 23
          }
        ]
      }
    ],
    "global_options": [
      {
        "option": "-y"
      }
    ],
    "metadata": {
      "thumbnail": true,
      "filesize": true,
      "duration": true,
      "bitrate": true,
      "encoder": true
    },
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id"
  }'
```

## 4. Response

### Success Response

The response will be sent to the specified `webhook_url` as a JSON object with the following properties:

- `endpoint` (string): The endpoint that processed the request (`/v1/ffmpeg/compose`).
- `code` (number): The HTTP status code (200 for success).
- `id` (string): The unique identifier for the request.
- `job_id` (string): The unique job ID assigned to the request.
- `response` (array): An array of output file objects, each containing:
  - `file_url` (string): The URL of the uploaded output file.
  - `thumbnail_url` (string, optional): The URL of the uploaded thumbnail, if requested.
  - `filesize` (number, optional): The size of the output file in bytes, if requested.
  - `duration` (number, optional): The duration of the output file in seconds, if requested.
  - `bitrate` (number, optional): The bitrate of the output file in bits per second, if requested.
  - `encoder` (string, optional): The encoder used for the output file, if requested.
- `message` (string): A success message (`"success"`).
- `pid` (number): The process ID of the worker that processed the request.
- `queue_id` (number): The ID of the queue used for processing the request.
- `run_time` (number): The time taken to process the request, in seconds.
- `queue_time` (number): The time the request spent in the queue, in seconds.
- `total_time` (number): The total time taken to process the request, including queue time, in seconds.
- `queue_length` (number): The current length of the processing queue.
- `build_number` (string): The build number of the application.

### Error Responses

- **400 Bad Request**: The request payload is invalid or missing required parameters.
- **401 Unauthorized**: The provided API key is invalid or missing.
- **429 Too Many Requests**: The maximum queue length has been reached.
- **500 Internal Server Error**: An unexpected error occurred while processing the request.

Example error response (400 Bad Request):

```json
{
  "code": 400,
  "message": "Invalid request payload: 'inputs' is a required property"
}
```

## 5. Error Handling

The API handles various types of errors, including:

- **Missing or invalid parameters**: If the request payload is missing required parameters or contains invalid data types, a 400 Bad Request error will be returned.
- **Authentication failure**: If the provided API key is invalid or missing, a 401 Unauthorized error will be returned.
- **Queue limit reached**: If the maximum queue length is reached, a 429 Too Many Requests error will be returned.
- **Unexpected errors**: If an unexpected error occurs during request processing, a 500 Internal Server Error will be returned, along with an error message.

The main application context (`app.py`) includes error handling for the processing queue. If the maximum queue length is set and the queue size reaches that limit, new requests will be rejected with a 429 Too Many Requests error.

## 6. Usage Notes

- The `inputs` array can contain multiple input files, allowing for operations like concatenation or merging.
- The `filters` array allows applying FFmpeg filters to the input files.
- The `outputs` array specifies the output file options, such as codec, bitrate, and resolution.
- The `global_options` array allows setting global FFmpeg options that apply to the entire operation.
- The `metadata` object allows requesting specific metadata to be included in the response, such as thumbnail, file size, duration, bitrate, and encoder information.
- The `webhook_url` parameter is required, and the response will be sent to this URL as a POST request.
- The `id` parameter is a unique identifier for the request, which can be used for tracking and logging purposes.

## 7. Common Issues

- Providing invalid or malformed input file URLs.
- Specifying invalid or unsupported FFmpeg options or filters.
- Attempting to process large or high-resolution files, which may result in long processing times or queue delays.
- Reaching the maximum queue length, which will cause new requests to be rejected.

## 8. Best Practices

- Validate input file URLs and ensure they are accessible before submitting the request.
- Test FFmpeg options and filters with sample files before using them in production.
- Consider transcoding or downscaling large or high-resolution files to reduce processing time and queue delays.
- Monitor the queue length and adjust the maximum queue length as needed to prevent excessive queuing or request rejections.
- Implement retry mechanisms for failed requests or requests that encounter queue limits.
- Use the `id` parameter to track and correlate requests with responses for better logging and debugging.