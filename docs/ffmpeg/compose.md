# `/v1/ffmpeg/compose` API Documentation

## Overview
This endpoint allows you to perform flexible FFmpeg operations by composing multiple input files, applying filters, and specifying output options. It provides a powerful way to manipulate and process multimedia files using the FFmpeg library.

## Endpoint
**URL Path:** `/v1/ffmpeg/compose`
**HTTP Method:** `POST`

## Request

### Headers
- `Authorization` (required): Bearer token for authentication.

### Body Parameters
The request body should be a JSON object with the following properties:

- `inputs` (required, array): An array of input file objects, each containing:
  - `file_url` (required, string): The URL of the input file.
  - `options` (optional, array): An array of option objects, each containing:
    - `option` (required, string): The FFmpeg option to apply to the input file.
    - `argument` (optional, string/number/null): The argument for the specified option.
- `filters` (optional, array): An array of filter objects, each containing:
  - `filter` (required, string): The FFmpeg filter to apply.
- `outputs` (required, array): An array of output objects, each containing:
  - `options` (required, array): An array of option objects, each containing:
    - `option` (required, string): The FFmpeg option to apply to the output file.
    - `argument` (optional, string/number/null): The argument for the specified option.
- `global_options` (optional, array): An array of global option objects, each containing:
  - `option` (required, string): The global FFmpeg option to apply.
  - `argument` (optional, string/number/null): The argument for the specified option.
- `metadata` (optional, object): An object specifying which metadata to include in the response, with boolean properties for `thumbnail`, `filesize`, `duration`, `bitrate`, and `encoder`.
- `webhook_url` (optional, string): The URL to send a webhook notification upon completion.
- `id` (optional, string): A unique identifier for the request.

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
      "filter": "hue=s=0.5"
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
  https://your-api-endpoint.com/v1/ffmpeg/compose \
  -H 'Authorization: Bearer your-access-token' \
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
        "filter": "hue=s=0.5"
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

## Response

### Success Response
**Status Code:** `200 OK`

The response body will be a JSON array containing objects for each output file, with the following properties:

- `file_url` (string): The URL of the output file.
- `thumbnail_url` (string, optional): The URL of the thumbnail image, if requested.
- `filesize` (number, optional): The size of the output file in bytes, if requested.
- `duration` (number, optional): The duration of the output file in seconds, if requested.
- `bitrate` (number, optional): The bitrate of the output file in bits per second, if requested.
- `encoder` (string, optional): The encoder used for the output file, if requested.

```json
[
  {
    "file_url": "https://your-storage.com/output1.mp4",
    "thumbnail_url": "https://your-storage.com/output1_thumbnail.jpg",
    "filesize": 12345678,
    "duration": 120.5,
    "bitrate": 1234567,
    "encoder": "libx264"
  }
]
```

### Error Responses
- **Status Code:** `400 Bad Request`
  - Description: The request payload is invalid or missing required fields.
  - Example Response:
    ```json
    {
      "error": "Invalid request payload"
    }
    ```

- **Status Code:** `401 Unauthorized`
  - Description: The request is missing or has an invalid authentication token.
  - Example Response:
    ```json
    {
      "error": "Unauthorized"
    }
    ```

- **Status Code:** `500 Internal Server Error`
  - Description: An unexpected error occurred on the server while processing the request.
  - Example Response:
    ```json
    {
      "error": "Internal Server Error"
    }
    ```

## Error Handling
The API will return appropriate error status codes and error messages in the response body for common issues such as:

- Missing or invalid request parameters
- Authentication errors
- FFmpeg processing errors
- File upload or storage errors

## Usage Notes
- The `inputs` array must contain at least one input file object.
- The `outputs` array must contain at least one output object.
- The `options` and `filters` arrays can be empty or omitted if no options or filters are needed.
- The `global_options` array is optional and can be used to specify FFmpeg options that apply to the entire operation.
- The `metadata` object is optional and can be used to request specific metadata to be included in the response for each output file.
- The `webhook_url` is optional and can be used to receive a notification when the operation is complete.
- The `id` is optional and can be used to uniquely identify the request.

## Common Issues
- Providing invalid or inaccessible input file URLs.
- Specifying invalid or unsupported FFmpeg options or filters.
- Encountering file upload or storage errors due to network or storage service issues.
- Exceeding resource limits or timeouts for long-running or resource-intensive operations.

## Best Practices
- Validate input file URLs and ensure they are accessible before submitting the request.
- Test your FFmpeg options and filters locally before using them in the API.
- Monitor the response for errors and handle them appropriately in your application.
- Consider implementing retry mechanisms for failed requests due to transient errors.
- Optimize your input files and FFmpeg options to minimize processing time and resource usage.
- Use the `webhook_url` parameter to receive asynchronous notifications instead of polling for completion.