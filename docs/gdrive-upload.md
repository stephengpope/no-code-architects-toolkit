# `/gdrive-upload` API Documentation

## Overview
The `/gdrive-upload` endpoint uploads a file to a specified folder on Google Drive. This endpoint supports uploading large files in chunks for efficient transfer.

## Endpoint
- **URL**: `/gdrive-upload`
- **Method**: `POST`

## Request

### Headers
- **X-API-Key** (string, required): The API key used for authentication.

### Body Parameters
- **file_url** (string, required): URL of the file to upload to Google Drive.
- **filename** (string, required): Desired name for the file once uploaded.
- **folder_id** (string, optional): ID of the Google Drive folder where the file will be uploaded. If not specified, the file is uploaded to the root directory.
- **chunk_size** (integer, optional): Size of each upload chunk in bytes for large files. Defaults to a standard chunk size.
- **webhook_url** (string, optional): URL to receive the Google Drive file ID upon completion.
- **id** (string, optional): Unique identifier for tracking the job.

### Example Request
```json
{
  "file_url": "https://example.com/file-to-upload.zip",
  "filename": "uploaded_file.zip",
  "folder_id": "1a2b3c4d5e",
  "chunk_size": 1048576,
  "webhook_url": "https://your-webhook-url.com/notify",
  "id": "upload123"
}
```

### Example using `curl`
```bash
curl -X POST "https://your-api-domain.com/gdrive-upload" \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
      "file_url": "https://example.com/file-to-upload.zip",
      "filename": "uploaded_file.zip",
      "folder_id": "1a2b3c4d5e",
      "chunk_size": 1048576,
      "webhook_url": "https://your-webhook-url.com/notify",
      "id": "upload123"
    }'
```

## Response

### Success Response (200 OK)
If the upload is successful and no `webhook_url` is provided:
- **Status Code**: `200 OK`
- **Body**:
    ```json
    {
      "job_id": "upload123",
      "file_id": "1fGHIjklMnOPqrsTUvWxYZabCdefGhIJk",
      "message": "success"
    }
    ```

### Accepted Response (202 Accepted)
If a `webhook_url` is provided, the request is queued, and this response is returned:
- **Status Code**: `202 Accepted`
- **Body**:
    ```json
    {
      "job_id": "upload123",
      "message": "processing"
    }
    ```

### Error Responses
- **400 Bad Request**: Missing or invalid parameters (`file_url`, `filename`).
  ```json
  {
    "error": "Missing required file_url or filename"
  }
  ```
- **500 Internal Server Error**: Upload process failed.
  ```json
  {
    "error": "Error during file upload to Google Drive"
  }
  ```

## Error Handling
- **400 Bad Request**: Returned if required parameters like `file_url` or `filename` are missing or invalid.
- **500 Internal Server Error**: Returned if an error occurs during upload or Google Drive API interaction.

## Usage Notes
- **Chunk Size**: Adjust `chunk_size` for large files to improve upload efficiency.
- **Folder ID**: If no `folder_id` is provided, the file uploads to the root Google Drive directory.

## Common Issues
1. **Invalid File URL**: Ensure `file_url` is accessible and points directly to the file.
2. **Google Drive Permissions**: Verify that the Google Drive API has permissions to upload to the specified folder.

## Best Practices
- **Asynchronous Processing**: For large files, use `webhook_url` to receive the result asynchronously.
- **Folder Management**: Use `folder_id` to organize uploaded files in specific Google Drive folders.
