# Image Effects to Video Conversion

## 1. Overview

The `/v1/image/effects/video` endpoint converts an image into a video file with specific dynamic effects like zoom-in-out or panning. It's registered in `app.py` under the `v1_image_effects_video_bp` blueprint from `routes.v1.image.effects.image_effects_video`.

## 2. Endpoint

**URL Path:** `/v1/image/effects/video`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be in JSON format:

| Parameter     | Type    | Required | Description                                                                                            |
|---------------|---------|----------|--------------------------------------------------------------------------------------------------------|
| `image_url`   | string  | Yes      | The URL of the image to be converted.                                                                  |
| `effect_type` | string  | Yes      | The desired effect: "zoom_in_out" or "pan_rlr" (pan right-left-right).                              |
| `length`      | number  | No       | Desired video length in seconds (default: 5, max: 120).                                                |
| `frame_rate`  | integer | No       | Frame rate of the output video (default: 30, min: 15, max: 60).                                        |
| `orientation` | string  | No       | Desired output video orientation: "landscape" (1920x1080) or "portrait" (1080x1920). Default: landscape. |
| `webhook_url` | string  | No       | URL to receive a webhook notification upon completion.                                                 |
| `id`          | string  | No       | Optional identifier for the request.                                                                   |

The `validate_payload` decorator enforces this JSON schema:

```json
{
    "type": "object",
    "properties": {
        "image_url": {"type": "string", "format": "uri"},
        "effect_type": {"type": "string", "enum": ["zoom_in_out", "pan_rlr"]},
        "length": {"type": "number", "minimum": 0.1, "maximum": 120},
        "frame_rate": {"type": "integer", "minimum": 15, "maximum": 60},
        "orientation": {"type": "string", "enum": ["landscape", "portrait"]},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["image_url", "effect_type"],
    "additionalProperties": False
}
```

### Example Request (Zoom In/Out)

```json
{
    "image_url": "https://example.com/image.jpg",
    "effect_type": "zoom_in_out",
    "length": 10,
    "orientation": "landscape",
    "id": "request-zoom"
}
```

### Example Request (Pan Right-Left-Right)

```json
{
    "image_url": "https://example.com/image.jpg",
    "effect_type": "pan_rlr",
    "length": 15,
    "orientation": "portrait",
    "id": "request-pan"
}
```

## 4. Response

Success and error responses follow the same structure as other endpoints (e.g., `/v1/image/convert/video`), returning the cloud storage URL in the `response` field on success (200 OK), or appropriate error codes (400, 429, 500).

## 5. Error Handling

- Handles missing/invalid parameters (400).
- Handles queue length exceeded (429).
- Handles exceptions during processing (500).

## 6. Usage Notes

- `effect_type` is required and determines the animation applied.
- `zoom_in_out`: Zooms in towards the center for the first half of the `length`, then zooms out for the second half.
- `pan_rlr`: Pans the view across the image from right-to-left for the first half, then left-to-right for the second half. No zoom is applied.
- The maximum `length` is increased to 120 seconds for this endpoint.

## 7. Common Issues

- Providing an invalid `image_url`.
- Forgetting the required `effect_type` parameter.

## 8. Best Practices

- Use `webhook_url` for long processing times.
- Specify `orientation` if a specific output aspect ratio is needed. 
