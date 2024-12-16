# `/v1/ffmpeg/compose` API Documentation

## Overview
This endpoint allows users to submit a flexible FFmpeg request for processing media files. It accepts various input files, filters, output options, and metadata options, and returns the processed output files along with their URLs and metadata.

## Endpoint
**URL Path:** `/v1/ffmpeg/compose`
**HTTP Method:** `POST`

## Request

### Headers
- `Authorization` (Required): Bearer token for authentication.

### Body Parameters
- `inputs` (Required, Array): An array of input file objects.
  - `file_url` (Required, String): The URL of the input file.
  - `options` (Optional, Array): An array of input file options.
    - `option` (Required, String): The FFmpeg option to apply.
    - `argument` (Optional, String/Number/Null): The argument for the option.
- `filters` (Optional, Array): An array of filter objects.
  - `filter` (Required, String): The FFmpeg filter to apply.
- `outputs` (Required, Array): An array of output file options.
  - `options` (Required, Array): An array of output file options.
    - `option` (Required, String): The FFmpeg option to apply.
    - `argument` (Optional, String/Number/Null): The argument for the option.
- `global_options` (Optional, Array): An array of global FFmpeg options.
  - `option` (Required, String): The FFmpeg option to apply.
  - `argument` (Optional, String/Number/Null): The argument for the option.
- `metadata` (Optional, Object): An object specifying which metadata to include in the response.
  - `thumbnail` (Optional, Boolean): Whether to include a thumbnail URL.
  - `filesize` (Optional, Boolean): Whether to include the file size.
  - `duration` (Optional, Boolean): Whether to include the duration.
  - `bitrate` (Optional, Boolean): Whether to include the bitrate.
  - `encoder` (Optional, Boolean): Whether to include the encoder information.
- `webhook_url` (Optional, String): The URL to send a webhook notification upon completion.
- `id` (Optional, String): A unique identifier for the request.

### Example Request

```json
{
  "inputs": [
    {
      "file_url": "https://example.com/video.mp4",
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
    "duration": true
  }
}
```

```bash
curl -X POST \
  https://api.example.com/v1/ffmpeg/compose \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "inputs": [
      {
        "file_url": "https://example.com/video.mp4",
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
      "duration": true
    }
  }'
```

## Response

### Success Response
**Status Code:** `200 OK`

```json
[
  {
    "file_url": "https://storage.googleapis.com/bucket/output.mp4",
    "thumbnail_url": "https://storage.googleapis.com/bucket/thumbnail.jpg",
    "filesize": 12345678,
    "duration": 120.5
  }
]
```

### Error Responses
**Status Code:** `400 Bad Request`

```json
{
  "error": "Invalid request payload"
}
```

**Status Code:** `401 Unauthorized`

```json
{
  "error": "Authentication failed"
}
```

**Status Code:** `500 Internal Server Error`

```json
{
  "error": "An error occurred while processing the request"
}
```

## Error Handling
- Missing or invalid request parameters will result in a `400 Bad Request` error.
- Authentication failures will result in a `401 Unauthorized` error.
- Any other errors during processing will result in a `500 Internal Server Error`.

## Usage Notes
- This endpoint supports flexible FFmpeg configurations, allowing users to specify input files, filters, output options, and global options.
- The `metadata` object in the request payload controls which metadata fields are included in the response.
- The `webhook_url` parameter can be used to receive a notification when the processing is complete.
- The `id` parameter can be used to track the request and associate it with other systems.

## Common Issues
- Providing invalid or inaccessible input file URLs.
- Specifying invalid FFmpeg options or filters.
- Exceeding the maximum allowed file size or processing time.

## Best Practices
- Validate input file URLs and ensure they are accessible before submitting the request.
- Test your FFmpeg configurations locally before using this API to ensure they work as expected.
- Use the `id` parameter to track requests and associate them with other systems or processes.
- Monitor the response for errors and handle them appropriately in your application.
- Consider using the `webhook_url` parameter to receive notifications and avoid polling for completion.