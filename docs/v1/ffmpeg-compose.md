# `/v1/ffmpeg/compose` API Documentation

## Overview
The `/v1/ffmpeg/compose` endpoint allows for complex media compositions using FFmpeg. This includes support for multiple inputs, filters, outputs, and metadata options.

## Endpoint
- **URL**: `/v1/ffmpeg/compose`
- **Method**: `POST`

## Request

### Headers
- **X-API-Key** (string, required): The API key used for authentication.

### Body Parameters
- **inputs** (array, required): List of media inputs with URLs and options.
  - Each item in `inputs` contains:
    - **file_url** (string, required): URL of the input file.
    - **options** (array, optional): Array of FFmpeg options (e.g., codec settings).
- **filters** (array, optional): List of filters to apply to the media.
  - Each filter object contains:
    - **filter** (string, required): The filter string for FFmpeg.
- **outputs** (array, required): Specifications for output files.
  - Each output object contains:
    - **options** (array, required): Array of FFmpeg options (e.g., format, codec).
- **global_options** (array, optional): Global options to apply across all inputs and outputs.
- **metadata** (object, optional): Additional metadata to retrieve, such as `thumbnail`, `filesize`, `duration`, and `bitrate`.
- **webhook_url** (string, optional): URL to receive the composition result upon completion.
- **id** (string, optional): Unique identifier for tracking the job.

### Example Request
```json
{
  "inputs": [
    {
      "file_url": "https://example.com/input1.mp4",
      "options": [
        { "option": "-vf", "argument": "scale=1280:720" }
      ]
    }
  ],
  "filters": [
    { "filter": "hue=s=0" }
  ],
  "outputs": [
    {
      "options": [
        { "option": "-f", "argument": "mp4" },
        { "option": "-c:v", "argument": "libx264" }
      ]
    }
  ],
  "global_options": [
    { "option": "-y" }
  ],
  "metadata": {
    "thumbnail": true,
    "filesize": true,
    "duration": true,
    "bitrate": true
  },
  "webhook_url": "https://your-webhook-url.com/notify",
  "id": "compose123"
}
```

### Example using `curl`
```bash
curl -X POST "https://your-api-domain.com/v1/ffmpeg/compose" \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
      "inputs": [
        {
          "file_url": "https://example.com/input1.mp4",
          "options": [{ "option": "-vf", "argument": "scale=1280:720" }]
        }
      ],
      "filters": [{ "filter": "hue=s=0" }],
      "outputs": [
        {
          "options": [{ "option": "-f", "argument": "mp4" }, { "option": "-c:v", "argument": "libx264" }]
        }
      ],
      "global_options": [{ "option": "-y" }],
      "metadata": { "thumbnail": true, "filesize": true, "duration": true, "bitrate": true },
      "webhook_url": "https://your-webhook-url.com/notify",
      "id": "compose123"
    }'
```

## Response

### Success Response (200 OK)
If the composition is successful and no `webhook_url` is provided:
- **Status Code**: `200 OK`
- **Body**:
    ```json
    {
      "job_id": "compose123",
      "outputs": [
        {
          "file_url": "https://cloud-storage-url.com/output1.mp4",
          "metadata": {
            "thumbnail_url": "https://cloud-storage-url.com/thumbnail.jpg",
            "filesize": 10485760,
            "duration": 180.5,
            "bitrate": 128000
          }
        }
      ],
      "message": "success"
    }
    ```

### Accepted Response (202 Accepted)
If a `webhook_url` is provided, the request is queued, and this response is returned:
- **Status Code**: `202 Accepted`
- **Body**:
    ```json
    {
      "job_id": "compose123",
      "message": "processing"
    }
    ```

### Error Responses
- **400 Bad Request**: Missing or invalid parameters (e.g., `inputs`, `outputs`).
  ```json
  {
    "error": "Missing required inputs or outputs parameter"
  }
  ```
- **500 Internal Server Error**: Composition process failed.
  ```json
  {
    "error": "Error during media composition"
  }
  ```

## Error Handling
- **400 Bad Request**: Returned if required parameters (`inputs` or `outputs`) are missing or malformed.
- **500 Internal Server Error**: Returned for FFmpeg processing errors.

## Usage Notes
- Use `global_options` to set options like `-y` for overwriting output files without confirmation.
- Metadata fields like `thumbnail`, `filesize`, `duration`, and `bitrate` provide additional details about each output.

## Common Issues
1. **Invalid Media URLs**: Ensure that all media URLs in `inputs` are accessible and valid.
2. **Filter Errors**: Ensure filters are in the correct FFmpeg format and compatible with input/output specifications.

## Best Practices
- **Use Webhook for Long Compositions**: Provide a `webhook_url` to avoid waiting for the full composition process.
- **Specify Output Formats**: Use `outputs` to define formats, codecs, and container settings to ensure compatibility.
