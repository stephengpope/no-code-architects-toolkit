## Below is a comprehensive guide to every parameter and option supported by the capton-video API, along with explanations on how they influence the caption generation process.

## Overview

The API accepts a JSON POST request body with several fields that define:

1. **The Input Video:**  
   - `video_url`: The URL to the source video.
   - `caption_srt` (optional): Inline SRT subtitle content if already available.
   - `caption_ass` (optional): Inline ASS subtitle content if already available.

   If neither `caption_srt` nor `caption_ass` is provided, the API will automatically generate captions from the video's audio track using speech-to-text transcription.

2. **Job Metadata:**
   - `job_id`: A unique identifier for the captioning job.
   - `language`: The language of the audio (or `auto` to let the system detect it).

3. **Caption Customization Options:**
   The `options` array allows you to control how the captions look, feel, and are formatted. Each element in `options` is an object with an `option` key and a `value` key. For example:
   ```json
   { "option": "line-color", "value": "#FF0000" }
   ```
   
   The following sections detail every available option.

---

## Request Body Structure

### Example

```json
{
  "video_url": "https://example.com/path/to/video.mp4",
  "caption_srt": null,
  "caption_ass": null,
  "options": [
    { "option": "line-color", "value": "#FF0000" },
    { "option": "word-color", "value": "#00FF00" },
    { "option": "outline-color", "value": "#0000FF" },
    { "option": "box-color", "value": "#FFFF00" },
    { "option": "highlight-color", "value": "#FF00FF" },
    { "option": "all-caps", "value": true },
    { "option": "replace", "value": { "hello": "hi" } },
    { "option": "max-words-per-line", "value": 5 },
    { "option": "position", "value": "top-center" },
    { "option": "font-family", "value": "Roboto" },
    { "option": "font-size", "value": 24 },
    { "option": "bold", "value": true },
    { "option": "italic", "value": false },
    { "option": "underline", "value": false },
    { "option": "strikeout", "value": false }
  ],
  "job_id": "f3873330-83fb-42f7-98cf-5a256016fe3e",
  "language": "en"
}
```

---

## Top-Level Fields

### `video_url` (string, required)
The URL of the video to be processed. The API will download and analyze this video to generate or apply captions.

- **Example:** `"https://example.com/path/to/video.mp4"`

### `caption_srt` (string or null, optional)
Inline SRT subtitle data. If provided, the API will use these subtitles instead of generating them. If set to `null`, the API will rely on `caption_ass` or generate subtitles.

- **Example:** `null` or `"1\n00:00:00,000 --> 00:00:02,000\nHello world!"`

### `caption_ass` (string or null, optional)
Inline ASS subtitle data. Similar to `caption_srt`, but in ASS format. Overrides the need for transcription if provided.

- **Example:** `null` or an ASS-formatted subtitle string.

### `job_id` (string, required)
A unique identifier for the captioning job. Useful for tracking processing and retrieving logs.

- **Example:** `"f3873330-83fb-42f7-98cf-5a256016fe3e"`

### `language` (string, optional)
Specifies the language of the video's audio.  
- Use `"auto"` to let the system detect the language automatically.
- Use a supported language code (e.g., `en`, `fr`, `de`, etc.) if known.

- **Default:** `"auto"`
- **Example:** `"en"`

---

## The `options` Array

The `options` array is where you customize every visual and formatting aspect of the subtitles. Each object in this array has the form:
```json
{
  "option": "<option-name>",
  "value": "<option-value>"
}
```

Below is a detailed list of all supported options:

### 1. Color and Appearance

**`line-color`**
- **Description:** Sets the main color of subtitle text (primary color).
- **Value:** A hex color code in `#RRGGBB` format.
- **Default:** `#FFFFFF` (white)
- **Example:** `{"option": "line-color", "value": "#FF0000"}` (red text)

**`word-color`**
- **Description:** For karaoke or progressive styles, defines the color of the currently "active" spoken word.
- **Value:** A hex color code.
- **Default:** `#FFFF00` (yellow)
- **Example:** `{"option": "word-color", "value": "#00FF00"}` (green active word)

**`outline-color`**
- **Description:** The color of the outline stroke around the subtitle text.
- **Value:** A hex color code.
- **Default:** `#000000` (black)
- **Example:** `{"option": "outline-color", "value": "#0000FF"}` (blue outline)

**`box-color`**
- **Description:** The background or "box" color behind the subtitle line (if the selected style uses one).
- **Value:** A hex color code.
- **Default:** `#000000` (black)
- **Example:** `{"option": "box-color", "value": "#FFFF00"}` (yellow box)

**`highlight-color`**
- **Description:** Used creatively in karaoke-style captions to highlight the active word. Due to ASS limitations, this often affects text color rather than a true background highlight.
- **Value:** A hex color code.
- **Default:** `#FF0000` (red)
- **Example:** `{"option": "highlight-color", "value": "#FF00FF"}` (magenta highlight)

**`shadow-color`** *(Not directly supported by ASS)*
- **Description:** Intended for shadow color customization. ASS does not natively support a separate shadow color from the text and outline colors.
- **Value:** A hex color code.
- **Default:** `#000000` (black)
- **Note:** Currently not applied due to ASS limitations.

### 2. Text Transformations and Formatting

**`all-caps`**
- **Description:** Convert all subtitle text to uppercase.
- **Value:** Boolean (`true` or `false`)
- **Default:** `false`
- **Example:** `{"option": "all-caps", "value": true}` (all text will be uppercase)

**`replace`**
- **Description:** Replace certain words or phrases in the text. This is useful for correcting common transcription errors or using preferred terminology.
- **Value:** A JSON object mapping original words to their replacements.
- **Example:** `{"option": "replace", "value": {"hello": "hi"}}` (replaces "hello" with "hi")

**`max-words-per-line`**
- **Description:** Limits the maximum number of words per subtitle line, wrapping to the next line once the limit is reached. Helps improve readability.
- **Value:** Integer (0 means no limit)
- **Default:** 0 (no limit)
- **Example:** `{"option": "max-words-per-line", "value": 5}`

### 3. Position and Layout

**`position`**
- **Description:** Sets the subtitle alignment on the screen.
- **Allowed Values:** `top-left`, `top-center`, `top-right`, `center-left`, `center-center`, `center-right`, `bottom-left`, `bottom-center`, `bottom-right`
- **Default:** `bottom-center`
- **Example:** `{"option": "position", "value": "top-center"}` (Subtitles appear at the top center of the screen)

**`x`** and **`y`**
- **Description:** Customize the exact position of the subtitles using coordinates. Used in conjunction with override tags to precisely place subtitles.
- **Value:** Integer coordinates
- **Default:** not set (depends on alignment)
- **Example:** `{"option": "x", "value": 100}`, `{"option": "y", "value": 200}`

### 4. Font and Style

**`font-family`**
- **Description:** Choose the font family for the subtitle text. The font must be available on the system.
- **Value:** String (font name)
- **Default:** `Arial`
- **Example:** `{"option": "font-family", "value": "Roboto"}`

**`font-size`**
- **Description:** Sets the font size. Usually a value in pixels or a relative size.
- **Value:** Integer
- **Default:** Approximately 5% of the video height if not specified.
- **Example:** `{"option": "font-size", "value": 24}`

**`bold`**
- **Description:** Make the subtitle text bold.
- **Value:** Boolean
- **Default:** `false`
- **Example:** `{"option": "bold", "value": true}`

**`italic`**
- **Description:** Make the subtitle text italic.
- **Value:** Boolean
- **Default:** `false`
- **Example:** `{"option": "italic", "value": true}`

**`underline`**
- **Description:** Underline the subtitle text.
- **Value:** Boolean
- **Default:** `false`
- **Example:** `{"option": "underline", "value": true}`

**`strikeout`**
- **Description:** Apply a strike-through effect to the text.
- **Value:** Boolean
- **Default:** `false`
- **Example:** `{"option": "strikeout", "value": true}`

**`scale_x` and `scale_y`**
- **Description:** Scale the subtitles horizontally (`scale_x`) or vertically (`scale_y`) as a percentage.
- **Value:** Integer representing percentage.
- **Default:** `100`
- **Example:** `{"option": "scale_x", "value": "120"}` (makes text 20% wider)

**`spacing`**
- **Description:** Adjust spacing between characters.
- **Value:** Integer (pixel units)
- **Default:** `0`
- **Example:** `{"option": "spacing", "value": 2}`

**`angle`**
- **Description:** Rotate the subtitle text by a given angle in degrees.
- **Value:** Integer (degrees)
- **Default:** `0`
- **Example:** `{"option": "angle", "value": 45}` (rotates text by 45 degrees)

**`border_style`**
- **Description:** Determines the style of the subtitle background and border.
- **Value:** `1` for outline+shadow style, `3` for opaque box background style.
- **Default:** `1`
- **Example:** `{"option": "border-style", "value": "3"}` (opaque box background)

**`outline_width`**
- **Description:** The thickness of the outline around the text.
- **Value:** Integer (pixel units)
- **Default:** `2`
- **Example:** `{"option": "outline-width", "value": 4}` (thicker outline)

**`shadow_offset`**
- **Description:** The offset (distance) of the subtitle shadow from the text.
- **Value:** Integer
- **Default:** `0`
- **Example:** `{"option": "shadow-offset", "value": 1}`

---

## Additional Behavior and Styles

- If `caption_srt` or `caption_ass` is provided, no automatic transcription occurs.
- If neither is provided, the API automatically transcribes the video.
- The API can produce several "styles," such as `classic` and `karaoke`. These styles determine how `word_color` and `highlight_color` are applied. By default, `style` is `classic`.

### Setting the Style

Although not shown in the original snippet, you can set:
```json
{"option": "style", "value": "karaoke"}
```
to enable karaoke-style subtitles. Other styles may be available or implemented in the future (`highlight`, `underline`, `word-by-word`), each using these options differently.

---

## Error Handling

- If a specified font is not available, the API returns an error object with a list of available fonts.
- If FFmpeg fails to process the video, the `error` field in the response describes the issue.
- If invalid values are provided for any options, the API may fallback to defaults or return an error, depending on the implementation.

---

## Example Usage Scenarios

1. **Simple Captions with Defaults:**
   Only provide `video_url`, no `options` or subtitles. The API auto-generates captions and uses default styles.

2. **Add a Red Outline and Larger Font:**
   ```json
   { "option": "outline-color", "value": "#FF0000" },
   { "option": "font-size", "value": 36 }
   ```

3. **Create Karaoke-Style Captions with Active Word Highlighting:**
   ```json
   { "option": "style", "value": "karaoke" },
   { "option": "word-color", "value": "#00FF00" },
   { "option": "highlight-color", "value": "#FF00FF" }
   ```

4. **Restrict Captions to Three Words per Line:**
   ```json
   { "option": "max-words-per-line", "value": 3 }
   ```

5. **Replace Certain Words:**
   ```json
   { "option": "replace", "value": { "um": "", "like": "" } }
   ```
   This removes filler words.
