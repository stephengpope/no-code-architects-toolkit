# S3 File Upload API

This endpoint allows you to upload a file directly to an S3-compatible storage service using multipart upload.

## Endpoint

`POST /v1/s3/upload/file`

## Authentication

This endpoint requires an API key to be provided in the `X-API-Key` header.

## Request

The request should be a multipart form with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | file | Yes | The file to upload to S3 |
| filename | string | No | Custom filename to use for the uploaded file. If not provided, the original filename will be used |
| public | boolean | No | Whether to make the file publicly accessible. Defaults to `false` |

Example curl request:
```bash
curl -X POST "https://api.example.com/v1/s3/upload/file" \
  -H "X-API-Key: your-api-key" \
  -F "file=@/path/to/your/file.mp4" \
  -F "filename=custom-name.mp4" \
  -F "public=true"
```

## Response

The response will be a JSON object with the following properties:

| Property | Type | Description |
|----------|------|-------------|
| file_url | string | The URL of the uploaded file. For public files, this is a direct URL. For private files, this is a pre-signed URL that will expire after 1 hour |
| filename | string | The filename of the uploaded file |
| bucket | string | The name of the S3 bucket where the file was uploaded |
| public | boolean | Whether the file is publicly accessible |

Example response:
```json
{
  "file_url": "https://bucket-name.s3.region.amazonaws.com/custom-name.mp4",
  "filename": "custom-name.mp4",
  "bucket": "bucket-name",
  "public": true
}
```

## Error Handling

If an error occurs, the response will include an error message with an appropriate HTTP status code.

## Technical Details

This endpoint uses the S3-compatible multipart upload API to stream the file directly to S3 without saving it completely to local disk. This allows for efficient transfer of large files with minimal memory usage.

The implementation:
1. Reads the uploaded file in chunks
2. Uploads each chunk to S3 as a part of a multipart upload
3. Completes the multipart upload once all parts are uploaded

This approach supports large file uploads and handles them efficiently.
