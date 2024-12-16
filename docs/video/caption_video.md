# `/v1/video/caption` API Documentation

## Overview
This endpoint allows users to submit a video URL and optional captions, settings, and replacement rules to generate a captioned video with customized styling and text replacement. The captioned video is then uploaded to cloud storage, and the cloud URL is returned.

## Endpoint
**URL Path:** `/v1/video/caption`
**HTTP Method:** `POST`

## Request

### Headers
- `Authorization` (required): Bearer token for authentication.

### Body Parameters
- `video_url` (required, string): The URL of the video to be captioned.
- `captions` (optional, string): The captions to be applied to the video.
- `settings` (optional, object): An object containing various settings for customizing the captions' appearance and behavior.
  - `line_color` (optional, string): The color of the caption lines.
  - `word_color` (optional, string): The color of the caption words.
  - `outline_color` (optional, string): The color of the caption outline.
  - `all_caps` (optional, boolean): Whether to display the captions in all capital letters.
  - `max_words_per_line` (optional, integer): The maximum number of words per line in the captions.
  - `x` (optional, integer): The horizontal position of the captions.
  - `y` (optional, integer): The vertical position of the captions.
  - `position` (optional, string): The position of the captions on the video (e.g., `bottom_left`, `middle_center`, `top_right`).
  - `alignment` (optional, string): The alignment of the captions (e.g., `left`, `center`, `right`).
  - `font_family` (optional, string): The font family for the captions.
  - `font_size` (optional, integer): The font size for the captions.
  - `bold` (optional, boolean): Whether to display the captions in bold.
  - `italic` (optional, boolean): Whether to display the captions in italic.
  - `underline` (optional, boolean): Whether to underline the captions.
  - `strikeout` (optional, boolean): Whether to strike out the captions.
  - `style` (optional, string): The style of the captions (e.g., `classic`, `karaoke`, `highlight`, `underline`, `word_by_word`).
  - `outline_width` (optional, integer): The width of the caption outline.
  - `spacing` (optional, integer): The spacing between caption lines.
  - `angle` (optional, integer): The angle of the captions.
  - `shadow_offset` (optional, integer): The offset of the caption shadow.
- `replace` (optional, array): An array of objects containing find and replace rules for the captions.
  - `find` (required, string): The text to be replaced.
  - `replace` (required, string): The replacement text.
- `webhook_url` (optional, string): The URL to receive a webhook notification upon completion.
- `id` (optional, string): An identifier for the captioning job.
- `language` (optional, string): The language of the captions (default: `auto`).

### Example Request

```json
{
  "video_url": "https://example.com/video.mp4",
  "captions": "This is a sample caption.",
  "settings": {
    "line_color": "#FFFFFF",
    "word_color": "#000000",
    "outline_color": "#CCCCCC",
    "all_caps": false,
    "max_words_per_line": 10,
    "x": 20,
    "y": 40,
    "position": "bottom_left",
    "alignment": "center",
    "font_family": "Arial",
    "font_size": 24,
    "bold": true,
    "italic": false,
    "underline": false,
    "strikeout": false,
    "style": "classic",
    "outline_width": 2,
    "spacing": 4,
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
      "outline_color": "#CCCCCC",
      "all_caps": false,
      "max_words_per_line": 10,
      "x": 20,
      "y": 40,
      "position": "bottom_left",
      "alignment": "center",
      "font_family": "Arial",
      "font_size": 24,
      "bold": true,
      "italic": false,
      "underline": false,
      "strikeout": false,
      "style": "classic",
      "outline_width": 2,
      "spacing": 4,
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
  "cloud_url": "https://example.com/captioned_video.mp4"
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
- Missing or invalid `video_url` parameter: `400 Bad Request` with an error message.
- Invalid settings or replace rules: `400 Bad Request` with an error message.
- Font-related errors: `400 Bad Request` with an error message and a list of available fonts.
- Unexpected errors during the captioning process: `500 Internal Server Error` with an error message.

## Usage Notes
- The `video_url` parameter is required, and the video must be accessible and in a supported format.
- The `captions` parameter is optional, and if not provided, the service will attempt to generate captions automatically.
- The `settings` parameter allows for customization of the captions' appearance and behavior.
- The `replace` parameter allows for text replacement in the captions.
- The `webhook_url` parameter is optional and can be used to receive a notification when the captioning process is complete.
- The `id` parameter is optional and can be used to identify the captioning job.
- The `language` parameter is optional and specifies the language of the captions. If not provided, the service will attempt to detect the language automatically.

## Common Issues
- Providing an invalid or inaccessible `video_url`.
- Specifying invalid or unsupported settings or replace rules.
- Encountering font-related issues due to unsupported or invalid font families.

## Best Practices
- Validate the `video_url` parameter before submitting the request.
- Test the captioning process with different settings and replace rules to ensure the desired output.
- Monitor the response for any errors or warnings and handle them accordingly.
- Consider using the `webhook_url` parameter to receive notifications and handle the captioned video asynchronously.
- Ensure that the provided captions and replace rules are accurate and appropriate for the video content.