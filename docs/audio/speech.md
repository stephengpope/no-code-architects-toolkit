# TTS (Text-to-Speech) API Endpoint Documentation

**Implemented by:** [Harrison Fisher](https://github.com/HarrisonFisher)

## Overview

The `/v1/audio/speech` endpoint allows clients to convert text into speech using different Text-to-Speech (TTS) engines. The service supports `edge-tts` and `streamlabs-polly` as TTS providers, offering flexibility in the choice of voices and speech synthesis options. It integrates with the application’s queuing system to manage potentially time-consuming operations, ensuring smooth processing of requests.

## Endpoint

- **URL**: `/v1/audio/speech`
- **Method**: `POST`

## Request

### Headers

- `x-api-key`: Required. Your API authentication key.

### Body Parameters

| Parameter     | Type   | Required | Description |
|---------------|--------|----------|-------------|
| `tts`         | String | No       | The TTS engine to use. Default is `edge-tts`. Options: `edge-tts`, `streamlabs-polly` |
| `text`        | String | Yes      | The text to convert to speech. |
| `voice`       | String | No       | The voice to use. The valid voice list depends on the TTS engine. |
| `webhook_url` | String | No       | A URL to receive a callback notification when processing is complete. If provided, the request will be processed asynchronously. |
| `id`          | String | No       | A custom identifier for tracking the request. |

### Available Voices

- For `edge-tts` (default TTS engine):
  - Default voice: "en-US-AvaNeural"  - Supports a wide range of voices in multiple languages
  - Many voices can be previewed at: https://tts.travisvn.com/ (note: this is a third-party site)
  - Examples include: "en-US-AvaNeural", "en-GB-SoniaNeural", "es-ES-ElviraNeural", etc.
  
- For `streamlabs-polly`:
  - Default voice: "Brian"
  - Available voices:
    ```
    Brian, Emma, Russell, Joey, Matthew, Joanna, Kimberly, 
    Amy, Geraint, Nicole, Justin, Ivy, Kendra, Salli, Raveena
    ```

> To get a complete list of available voices for either engine, make a request with an invalid voice name - the error response will include all valid voices.

### Example Request

```json
{
  "tts": "edge-tts",
  "text": "Hello, world!",
  "voice": "en-US-AvaNeural",
  "webhook_url": "https://your-webhook-endpoint.com/callback",
  "id": "custom-request-id-123"
}
```

### Example cURL Command

```bash
curl -X POST \
  https://api.example.com/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: your-api-key-here' \
  -d '{
    "tts": "edge-tts",
    "text": "Hello, world!",
    "voice": "en-US-AvaNeural",
    "webhook_url": "https://your-webhook-endpoint.com/callback",
    "id": "custom-request-id-123"
  }'
```

## Response

### Synchronous Response (No webhook\_url provided)

If no `webhook_url` is provided, the request will be processed synchronously and return:

```json
{
  "code": 200,
  "id": "custom-request-id-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "https://storage.example.com/audio-file.mp3",
  "message": "success",
  "run_time": 2.345,
  "queue_time": 0,
  "total_time": 2.345,
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

### Asynchronous Response (webhook\_url provided)

If a `webhook_url` is provided, the request will be queued for processing and immediately return:

```json
{
  "code": 202,
  "id": "custom-request-id-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "processing",
  "pid": 12345,
  "queue_id": 67890,
  "max_queue_length": "unlimited",
  "queue_length": 1,
  "build_number": "1.0.123"
}
```

When processing is complete, a webhook will be sent to the provided URL with the following payload:

```json
{
  "endpoint": "/v1/audio/speech",
  "code": 200,
  "id": "custom-request-id-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "https://storage.example.com/audio-file.mp3",
  "message": "success",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 3.456,
  "queue_time": 1.234,
  "total_time": 4.690,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

### Error Responses

#### Invalid Request Format (400 Bad Request)

```json
{
  "code": 400,
  "id": null,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "IInvalid request: 'text' is a required property",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

#### Authentication Error (401 Unauthorized)

```json
{
  "code": 401,
  "message": "Invalid or missing API key",
  "build_number": "1.0.123"
}
```

#### Queue Limit Reached (429 Too Many Requests)

```json
{
  "code": 429,
  "id": "custom-request-id-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "MAX_QUEUE_LENGTH (100) reached",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 100,
  "build_number": "1.0.123"
}
```

#### Processing Error (500 Internal Server Error)

```json
{
  "code": 500,
  "id": "custom-request-id-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Error downloading audio file: Connection refused",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

## Error Handling

* **Missing Required Parameters**: If `text` is missing or empty, a 400 Bad Request response will be returned.
* **Invalid TTS Engine**: If the `tts` parameter is invalid (e.g., not `edge-tts` or `streamlabs-polly`), a 400 Bad Request response will be returned.
* **Authentication Failure**: If the API key is invalid or missing, a 401 Unauthorized response will be returned.
* **Queue Limit**: If the queue is full (when MAX\_QUEUE\_LENGTH is set), a 429 Too Many Requests response will be returned.
* **Processing Errors**: Any errors during text processing, speech synthesis, or audio file generation will result in a 500 Internal Server Error response with details in the message field.

## Usage Notes

1. **Asynchronous Processing**: For longer processing times (e.g., generating speech from large texts), it's recommended to use the `webhook_url` parameter for asynchronous processing.
2. **Queue Behavior**: If the system is under heavy load, requests with `webhook_url` will be queued. The `MAX_QUEUE_LENGTH` environment variable controls the maximum queue size.

## Common Issues

1. **Invalid Voice**: Make sure the selected voice is valid for the chosen TTS engine.
2. **Webhook Failures**: If your webhook endpoint is unavailable when processing completes, you might not receive the completion notification.
3. **Timeout Issues**: Long texts or heavy load might cause timeouts during speech synthesis.

## Best Practices

1. **Use Webhooks for Large Texts**: Consider using the webhook approach for large text-to-speech requests to avoid timeouts.
2. **Include an ID**: Always include a custom `id` parameter to help track your requests, especially in webhook responses.
3. **Error Handling**: Implement robust error handling to manage various HTTP status codes.
4. **Webhook Reliability**: Ensure your webhook endpoint is reliable and can handle retries if necessary.
5. **Text Chunking**: If you're processing large bodies of text, chunk it appropriately to avoid exceeding character limits.
