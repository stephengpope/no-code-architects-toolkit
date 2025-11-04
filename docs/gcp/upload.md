# GCP Upload API

This endpoint allows you to stream a file from a remote URL directly to Google Cloud Storage without using local disk space.

## Endpoint

`POST /v1/gcp/upload`

## Authentication

This endpoint requires an API key to be provided in the `X-API-Key` header.

## Request Body

The request body should be a JSON object with the following properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| file_url | string | Yes | The URL of the file to upload to GCS |
| filename | string | No | Custom filename to use for the uploaded file. If not provided, the original filename will be used |
| public | boolean | No | Whether to make the file publicly accessible. Defaults to `false` |
| download_headers | object | No | Optional headers to include in the download request for authentication |

Example request body:
```json
{
  "file_url": "https://example.com/path/to/file.mp4",
  "filename": "custom-name.mp4",
  "public": true,
  "download_headers": {
    "Authorization": "Bearer your-token"
  }
}
```

## Response

The response will be a JSON object with the following properties:

| Property | Type | Description |
|----------|------|-------------|
| file_url | string | The public URL of the uploaded file |
| filename | string | The filename of the uploaded file |
| bucket | string | The name of the GCS bucket where the file was uploaded |
| public | boolean | Whether the file is publicly accessible |
| content_type | string | The detected content type of the uploaded file |

Example response:
```json
{
  "file_url": "https://storage.googleapis.com/bucket-name/custom-name.mp4",
  "filename": "custom-name.mp4",
  "bucket": "bucket-name",
  "public": true,
  "content_type": "video/mp4"
}
```

## Error Handling

If an error occurs, the response will include an error message with an appropriate HTTP status code.

## Technical Details

This endpoint uses the Google Cloud Storage API to stream the file directly from the source URL to GCS without saving it locally. This allows for efficient transfer of large files with minimal memory usage.

The implementation:
1. Streams the file from the source URL
2. Detects the content type from the response headers
3. Uploads the file directly to GCS using the streaming upload API

This approach supports efficient handling of large files and maintains the original content type of the uploaded file. 