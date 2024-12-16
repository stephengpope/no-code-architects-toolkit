# `/v1/video/caption` API Documentation

## Overview
This endpoint allows users to caption a video by providing a video URL and optional settings. The captioning process is handled asynchronously, and the captioned video is uploaded to cloud storage upon completion.

## Endpoint
**URL Path:** `/v1/video/caption`
**HTTP Method:** `POST`

## Request

### Headers
- `Authorization` (required): Bearer token for authentication.

### Body Parameters
- `video_url` (required, string): The URL of the video to be captioned.
- `captions` (optional, string): The captions to be applied to the video.
- `settings` (optional, object): An object containing various settings for the captioning process.
  - `line_color` (optional, string): The color of the caption lines.
  - `word_color` (optional, string): The color of the caption words.
  - `outline_color` (optional, string): The color of the caption outline.
  - `all_caps` (optional, boolean): Whether to display captions in all capital letters.
  - `max_words_per_line` (optional, integer): The maximum number of words per caption line.
  - `x` (optional, integer): The x-coordinate position of the captions.
  - `y` (optional, integer): The y-coordinate position of the captions.
  - `position` (optional, string): The position of the captions on the video (e.g., "bottom_left", "middle_center", etc.).
  - `alignment` (optional, string): The alignment of the captions (e.g., "left", "center", "right").
  - `font_family` (optional, string): The font family for the captions.
  - `font_size` (optional, integer): The font size for the captions.
  - `bold` (optional, boolean): Whether to display captions in bold.
  - `italic` (optional, boolean): Whether to display captions in italic.
  - `underline` (optional, boolean): Whether to underline the captions.
  - `strikeout` (optional, boolean): Whether to strike out the captions.
  - `style` (optional, string): The style of the captions (e.g., "classic", "karaoke", "highlight", etc.).
  - `outline_width` (optional, integer): The width of the caption outline.
  - `spacing` (optional, integer): The spacing between caption lines.
  - `angle` (optional, integer): The angle of the captions.
  - `shadow_offset` (optional, integer): The offset of the caption shadow.
- `replace` (optional, array): An array of objects containing find and replace rules for the captions.
  - `find` (required, string): The text to be replaced.
  - `replace` (required, string): The replacement text.
- `webhook_url` (optional, string): The URL to receive a webhook notification upon completion.
- `id` (optional, string): An identifier for the captioning job.
- `language` (optional, string): The language of the captions (default is "auto").

### Example Request

```json
{
  "video_url": "https://example.com/video.mp4",
  "captions": "This is a sample caption.",
  "settings": {
    "line_color": "#FFFFFF",
    "word_color": "#000000",
    "outline_color": "#000000",
    "all_caps": false,
    "max_words_per_line": 10,
    "x": 50,
    "y": 100,
    "position": "bottom_left",
    "alignment": "left",
    "font_family": "Arial",
    "font_size": 24,
    "bold": false,
    "italic": false,
    "underline": false,
    "strikeout": false,
    "style": "classic",
    "outline_width": 2,
    "spacing": 10,
    "angle": 0,
    "shadow_offset": 2
  },
  "replace": [
    {
      "find": "sample",
      "replace": "example"
    }
  ],
  "webhook_url": "https://example.com/webhook",
  "id": "job123",
  "language": "en"
}
```

```bash
curl -X POST \
  https://api.example.com/v1/video/caption \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "captions": "This is a sample caption.",
    "settings": {
      "line_color": "#FFFFFF",
      "word_color": "#000000",
      "outline_color": "#000000",
      "all_caps": false,
      "max_words_per_line": 10,
      "x": 50,
      "y": 100,
      "position": "bottom_left",
      "alignment": "left",
      "font_family": "Arial",
      "font_size": 24,
      "bold": false,
      "italic": false,
      "underline": false,
      "strikeout": false,
      "style": "classic",
      "outline_width": 2,
      "spacing": 10,
      "angle": 0,
      "shadow_offset": 2
    },
    "replace": [
      {
        "find": "sample",
        "replace": "example"
      }
    ],
    "webhook_url": "https://example.com/webhook",
    "id": "job123",
    "language": "en"
  }'
```

## Response

### Success Response

**Status Code:** `200 OK`

**Response Body:**

```json
{
  "cloud_url": "https://storage.example.com/captioned_video.mp4"
}
```

### Error Responses

**Status Code:** `400 Bad Request`

**Response Body (Font Error):**

```json
{
  "error": "Invalid font family specified. Please choose from the available fonts.",
  "available_fonts": [
    "Arial",
    "Times New Roman",
    "Courier New"
  ]
}
```

**Response Body (Non-Font Error):**

```json
{
  "error": "Invalid video URL provided."
}
```

**Status Code:** `500 Internal Server Error`

**Response Body:**

```json
{
  "error": "An unexpected error occurred during the captioning process."
}
```

## Error Handling
- Missing or invalid `video_url` parameter: `400 Bad Request`
- Invalid settings or replace rules: `400 Bad Request`
- Font-related errors: `400 Bad Request` with a list of available fonts
- Other errors during the captioning process: `500 Internal Server Error`

## Usage Notes
- The captioning process is handled asynchronously, and the response will contain the URL of the captioned video once it's available in cloud storage.
- If a `webhook_url` is provided, a notification will be sent to that URL upon completion of the captioning process.
- The `id` parameter can be used to track the captioning job.

## Common Issues
- Providing an invalid or inaccessible video URL.
- Specifying invalid or unsupported settings or replace rules.
- Encountering font-related issues, such as using an unsupported font family.

## Best Practices
- Validate the `video_url` parameter before submitting the request.
- Use the `settings` and `replace` parameters judiciously to ensure optimal captioning results.
- Monitor the response for any errors or warnings, and handle them accordingly.
- Implement retry mechanisms for failed requests or temporary errors.