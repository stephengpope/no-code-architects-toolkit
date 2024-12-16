# FFmpeg Compose API

## 1. Overview

The FFmpeg Compose API endpoint allows users to perform complex video and audio processing tasks using the powerful FFmpeg library. It provides a flexible way to combine multiple input files, apply various filters and options, and generate one or more output files. This endpoint fits into the overall API structure as part of the version 1 (`v1`) routes, specifically under the `/v1/ffmpeg/compose` path.

## 2. Endpoint

**URL Path:** `/v1/ffmpeg/compose`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body should be a JSON object with the following properties:

- `inputs` (required, array): An array of input file objects, each containing:
  - `file_url` (required, string): The URL of the input file.
  - `options` (optional, array): An array of option objects, each containing:
    - `option` (required, string): The FFmpeg option to apply.
    - `argument` (optional, string, number, or null): The argument for the option.
- `filters` (optional, array): An array of filter objects, each containing:
  - `filter` (required, string): The FFmpeg filter to apply.
- `outputs` (required, array): An array of output file objects, each containing:
  - `options` (required, array): An array of option objects, each containing:
    - `option` (required, string): The FFmpeg option to apply.
    - `argument` (optional, string, number, or null): The argument for the option.
- `global_options` (optional, array): An array of global option objects, each containing:
  - `option` (required, string): The FFmpeg global option to apply.
  - `argument` (optional, string, number, or null): The argument for the option.
- `metadata` (optional, object): An object specifying which metadata to include in the response, with boolean properties for `thumbnail`, `filesize`, `duration`, `bitrate`, and `encoder`.
- `webhook_url` (required, string): The URL to send the response webhook.
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
      "filter": "hflip"
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
        "filter": "hflip"
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

**Status Code:** `200 OK`

The response body will be a JSON array containing one or more objects, each representing an output file. Each object will have the following properties:

- `file_url` (string): The URL of the uploaded output file.
- `thumbnail_url` (string, optional): The URL of the uploaded thumbnail image, if requested.
- `filesize` (number, optional): The size of the output file in bytes, if requested.
- `duration` (number, optional): The duration of the output file in seconds, if requested.
- `bitrate` (number, optional): The bitrate of the output file in bits per second, if requested.
- `encoder` (string, optional): The encoder used for the output file, if requested.

```json
[
  {
    "file_url": "https://storage.googleapis.com/bucket/output1.mp4",
    "thumbnail_url": "https://storage.googleapis.com/bucket/output1_thumbnail.jpg",
    "filesize": 12345678,
    "duration": 42.5,
    "bitrate": 1234567,
    "encoder": "libx264"
  },
  {
    "file_url": "https://storage.googleapis.com/bucket/output2.mp4",
    "filesize": 87654321,
    "duration": 120.0,
    "bitrate": 7654321,
    "encoder": "libx264"
  }
]
```

### Error Responses

**Status Code:** `400 Bad Request`

```json
{
  "message": "Invalid request payload"
}
```

**Status Code:** `401 Unauthorized`

```json
{
  "message": "Missing or invalid API key"
}
```

**Status Code:** `500 Internal Server Error`

```json
{
  "message": "An error occurred while processing the request"
}
```

## 5. Error Handling

The endpoint performs the following error handling:

- **Missing or invalid API key**: Returns a `401 Unauthorized` status code with an error message.
- **Invalid request payload**: Returns a `400 Bad Request` status code with an error message.
- **FFmpeg processing error**: Returns a `500 Internal Server Error` status code with the error message from FFmpeg.
- **Output file not found**: Returns a `500 Internal Server Error` status code with an error message indicating that the expected output file was not found.

Additionally, the main application context includes error handling for the following cases:

- **Queue length exceeded**: If the maximum queue length is set and the queue size reaches that limit, the endpoint returns a `429 Too Many Requests` status code with an error message.
- **Missing webhook URL**: If the request does not include a `webhook_url`, the task is processed immediately without being queued, and the response is returned directly.

## 6. Usage Notes

- The FFmpeg Compose API provides a flexible way to perform complex video and audio processing tasks by combining multiple input files, applying filters and options, and generating one or more output files.
- The request payload allows for a wide range of customization, including specifying input file options, filters, output file options, and global options.
- The `metadata` object in the request payload allows users to request specific metadata to be included in the response, such as thumbnail images, file size, duration, bitrate, and encoder information.
- The response includes the URLs of the uploaded output files, as well as any requested metadata.

## 7. Common Issues

- **Invalid input file URLs**: Ensure that the provided input file URLs are valid and accessible.
- **Unsupported FFmpeg options or filters**: Double-check that the specified FFmpeg options and filters are valid and supported by the version of FFmpeg used by the API.
- **Large file sizes**: Processing large video or audio files may take longer and consume more resources. Consider breaking down large files into smaller chunks or adjusting the processing options to reduce the output file size.

## 8. Best Practices

- **Validate input file URLs**: Before submitting a request, ensure that the input file URLs are valid and accessible to avoid errors during processing.
- **Test with sample files**: Before processing large or important files, test the desired FFmpeg options and filters with sample files to ensure the expected output.
- **Monitor response webhooks**: Set up a webhook URL to receive notifications and monitor the progress and results of your FFmpeg processing tasks.
- **Optimize processing options**: Experiment with different FFmpeg options and filters to find the optimal balance between output quality and file size for your use case.
- **Handle errors gracefully**: Implement error handling in your application to gracefully handle any errors returned by the API and provide appropriate feedback to users.