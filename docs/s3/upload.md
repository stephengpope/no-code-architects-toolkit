# S3 Upload API

This endpoint allows you to stream a file from a remote URL directly to an S3-compatible storage service without using local disk space.

## Endpoint

`POST /v1/s3/upload`

## Authentication

This endpoint requires an API key to be provided in the `X-API-Key` header.

## Request Body

The request body should be a JSON object with the following properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| file_url | string | Yes | The URL of the file to upload to S3 |
| filename | string | No | Custom filename to use for the uploaded file. If not provided, the original filename will be used |
| public | boolean | No | Whether to make the file publicly accessible. Defaults to `false` |

Example request body:
```json
{
  "file_url": "https://example.com/path/to/file.mp4",
  "filename": "custom-name.mp4",
  "public": true
}
```

## Response

The response will be a JSON object with the following properties:

| Property | Type | Description |
|----------|------|-------------|
| url | string | The URL of the uploaded file. For public files, this is a direct URL. For private files, this is a pre-signed URL that will expire after 1 hour |
| filename | string | The filename of the uploaded file |
| bucket | string | The name of the S3 bucket where the file was uploaded |
| public | boolean | Whether the file is publicly accessible |

Example response:
```json
{
  "url": "https://bucket-name.s3.region.amazonaws.com/custom-name.mp4",
  "filename": "custom-name.mp4",
  "bucket": "bucket-name",
  "public": true
}
```

## Error Handling

If an error occurs, the response will include an error message with an appropriate HTTP status code.

## Technical Details

This endpoint uses the S3-compatible multipart upload API to stream the file directly from the source URL to S3 without saving it locally. This allows for efficient transfer of large files with minimal memory usage.

The implementation:
1. Streams the file from the source URL in chunks
2. Uploads each chunk to S3 as a part of a multipart upload
3. Completes the multipart upload once all parts are uploaded

This approach supports resumable uploads and can handle large files efficiently.