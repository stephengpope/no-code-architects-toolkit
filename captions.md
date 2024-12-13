## Captions and Subtitle Customization: Comprehensive Guide

This API allows you to submit a video and produce captions that can be generated automatically through speech-to-text transcription, or derived from provided SRT/ASS subtitles. In addition, it offers a wide range of styling and formatting options to fully control the appearance and behavior of your captions.

**Key Features:**
- Automatic transcription if no subtitles are provided.
- Support for inline SRT or ASS subtitles if you already have them.
- A comprehensive set of styling options (`options` array) to customize colors, fonts, positions, effects, and behaviors.
- Multiple “styles” of caption display, such as `classic`, `karaoke`, `highlight`, `underline`, and `word-by-word`, each controlling how active words or lines are presented.

---

## Request Body Structure

### Required and Optional Fields

**`video_url` (string, required)**  
The URL pointing to the video you want to process. The API will download and analyze this video.  
- **Example:** `"https://example.com/path/to/video.mp4"`  
If this field is not provided, the request is invalid as no video is available to process.

**`caption_srt` (string or null, optional)**  
If you have an SRT subtitle file (in plain text), you can inline it here. Providing this bypasses the need for automatic transcription.  
- **Example:** 
  - `null`: No inline SRT provided, rely on `caption_ass` or generate automatically.
  - A valid SRT could look like:
    ```  
    1
    00:00:00,000 --> 00:00:02,000
    Hello world!
    ```

**`caption_ass` (string or null, optional)**  
If you have an ASS subtitle file, provide it here. This also bypasses transcription, using your preexisting subtitles.  
- **Example:**  
  - `null`: No ASS provided.
  - A valid ASS file starting with `[Script Info]` section.

**Behavior When Subtitles Are Provided:**
- If `caption_ass` is provided, it overrides the need for transcription and uses the given ASS subtitles directly.
- If `caption_srt` is provided (and `caption_ass` is not), it uses the SRT subtitles and converts them to ASS format internally, applying your styling options.
- If neither `caption_srt` nor `caption_ass` is provided, the API will automatically transcribe the video’s audio to create captions.

**`job_id` (string, required)**  
A unique identifier for the captioning job. Use this to track logs, monitor progress, or reference results later.  
- **Example:** `"f3873330-83fb-42f7-98cf-5a256016fe3e"`

**`language` (string, optional)**  
Specifies the language of the audio. If set to `"auto"`, the API attempts to detect the language automatically. Otherwise, provide a specific language code (e.g., `"en"` for English, `"fr"` for French) to guide transcription.  
- **Default:** `"auto"`
- **Example:** `"en"`

**`options` (array of objects, optional)**  
An array of `{ "option": "<name>", "value": <value> }` objects that control every aspect of your captions, including color, font, size, position, styling (e.g., karaoke or highlight), and more. Each entry modifies a single parameter.

If no `options` are provided, sensible defaults are used, resulting in basic white text captions centered at the bottom of the screen.

---

### Example Request Body

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
    { "option": "strikeout", "value": false },
    { "option": "style", "value": "classic" }
  ],
  "job_id": "f3873330-83fb-42f7-98cf-5a256016fe3e",
  "language": "en"
}
```

---

## Detailed Description of Each Option

### 1. Color and Appearance Options

**`line-color`**  
- **Description:** Sets the primary color of the subtitle text.  
- **Type:** Hex color code (`#RRGGBB`)  
- **Default:** `#FFFFFF` (white)  
- **Impact:** Changes the color of all non-active words or the entire line’s text if no highlighting is applied.  
- **Example:** `{"option": "line-color", "value": "#FF0000"}` makes the base text red.

**`word-color`**  
- **Description:** For styles like `karaoke` or `underline`, this defines the color of the currently "active" spoken word if the style supports per-word highlighting.  
- **Type:** Hex color code  
- **Default:** `#FFFF00` (yellow)  
- **Example:** `{"option": "word-color", "value": "#00FF00"}` makes the active word appear green in karaoke mode.

**`outline-color`**  
- **Description:** The color of the outline stroke around the subtitle characters.  
- **Type:** Hex color code  
- **Default:** `#000000` (black)  
- **Impact:** Highly visible if `outline-width` is increased.  
- **Example:** `{"option": "outline-color", "value": "#0000FF"}` creates a blue outline.

**`box-color`**  
- **Description:** Background or "box" color behind the subtitles if the selected style and border settings support it.  
- **Type:** Hex color code  
- **Default:** `#000000` (black)  
- **When Visible:** If `border-style=3` (opaque box) is used, `box-color` fills the area behind the text.  
- **Example:** `{"option": "box-color", "value": "#FFFF00"}` for a yellow background box.

**`highlight-color`**  
- **Description:** Used in advanced styles like `highlight` or `karaoke` to emphasize the active word. In `highlight` style, this often changes the active word’s text color.  
- **Type:** Hex color code  
- **Default:** `#FF0000` (red)  
- **Example:** `{"option": "highlight-color", "value": "#FF00FF"}` makes highlighted words magenta.

**`shadow-color`** *(Limited Support)*  
- **Description:** Intended to define the shadow color. However, ASS does not directly support a separate shadow color distinct from text/outline color.  
- **Type:** Hex color code  
- **Default:** `#000000` (black)  
- **Note:** May have no visible effect depending on style and rendering engine.

---

### 2. Text Transformations and Formatting

**`all-caps`**  
- **Description:** Converts all subtitle text to uppercase, overriding original casing.  
- **Type:** Boolean  
- **Default:** `false`  
- **Example:** `{"option": "all-caps", "value": true}` ensures all displayed text is uppercase.

**`replace`**  
- **Description:** A dictionary of words to be replaced in the subtitles. Useful for correcting transcription errors or substituting certain words. Matching is case-insensitive.  
- **Type:** JSON object mapping strings to replacements.  
- **Default:** None (no replacements)  
- **Example:** `{"option": "replace", "value": {"hello": "hi"}}` replaces every "hello" with "hi".

**`max-words-per-line`**  
- **Description:** Limits how many words appear on a single line before wrapping to the next line. Improves readability by preventing overly long lines.  
- **Type:** Integer (0 = no limit)  
- **Default:** 0 (no wrapping based on word count)  
- **Example:** `{"option": "max-words-per-line", "value": 5}` breaks lines after every 5 words.

---

### 3. Position and Layout

**`position`**  
- **Description:** Sets the on-screen alignment of subtitles.  
- **Allowed Values:** `top-left`, `top-center`, `top-right`, `center-left`, `center-center`, `center-right`, `bottom-left`, `bottom-center`, `bottom-right`  
- **Default:** `bottom-center`  
- **Example:** `{"option": "position", "value": "top-center"}` displays subtitles at the top center.

**`x` and `y`**  
- **Description:** Fine-grained control over subtitle positioning in pixel coordinates. Used with override tags like `\pos(x,y)` inside dialogue lines.  
- **Type:** Integer  
- **Default:** Not set (aligns by `position`)  
- **Example:** `{"option": "x", "value": 100}`, `{"option": "y", "value": 200}` precisely places subtitles at (100,200).

---

### 4. Font and Style

**`font-family`**  
- **Description:** Sets the font used for rendering subtitles. The font must exist on the system.  
- **Type:** String (font name)  
- **Default:** `Arial`  
- **Example:** `{"option": "font-family", "value": "Roboto"}` selects Roboto if available.

**`font-size`**  
- **Description:** The size of the subtitle text, generally in pixels. Larger values produce more readable subtitles for testing.  
- **Type:** Integer  
- **Default:** Approximately 5% of the video height if not specified.  
- **Example:** `{"option": "font-size", "value": 36}` larger text.

**`bold`**  
- **Description:** Makes the subtitle text bold.  
- **Type:** Boolean  
- **Default:** `false`  
- **Example:** `{"option": "bold", "value": true}` creates bold text.

**`italic`**  
- **Description:** Italicizes the subtitle text.  
- **Type:** Boolean  
- **Default:** `false`  
- **Example:** `{"option": "italic", "value": true}` italicizes the text.

**`underline`**  
- **Description:** Underlines the subtitle text.  
- **Type:** Boolean  
- **Default:** `false`  
- **Example:** `{"option": "underline", "value": true}` underlines all text.

**`strikeout`**  
- **Description:** Applies a strike-through effect to the text.  
- **Type:** Boolean  
- **Default:** `false`  
- **Example:** `{"option": "strikeout", "value": true}` displays strikethrough text.

**`scale_x` and `scale_y`**  
- **Description:** Scales subtitles horizontally or vertically as a percentage.  
- **Type:** Integer representing a percentage (100 = no scale).  
- **Default:** `100` for both  
- **Example:** `{"option": "scale_x", "value": "120"}` widens text by 20%.

**`spacing`**  
- **Description:** Adjust character spacing. A positive integer increases space between letters, improving readability.  
- **Type:** Integer (pixels)  
- **Default:** `0`  
- **Example:** `{"option": "spacing", "value": 2}` adds slight extra space between characters.

**`angle`**  
- **Description:** Rotates the subtitle text by the given angle in degrees.  
- **Type:** Integer (degrees)  
- **Default:** `0` (no rotation)  
- **Example:** `{"option": "angle", "value": 45}` rotates text by 45°.

**`border-style`**  
- **Description:** Controls how the border and background are rendered.  
- **Type:** Integer (1 or 3 are most common)
  - `1`: Outlined text with optional shadow.
  - `3`: Opaque box behind text, making `box-color` visible.
- **Default:** `1` (outline + shadow)
- **Example:** `{"option": "border-style", "value": "3"}` creates an opaque background box behind the text.

**`outline-width`**  
- **Description:** Thickness of the text outline in pixels. Larger values produce a thicker, more visible outline.  
- **Type:** Integer  
- **Default:** `2`  
- **Example:** `{"option": "outline-width", "value": 4}` thicker outline.

**`shadow-offset`**  
- **Description:** The offset (distance) of the shadow from the text. A non-zero value creates a drop-shadow effect.  
- **Type:** Integer  
- **Default:** `0` (no shadow offset)  
- **Example:** `{"option": "shadow-offset", "value": 1}` small drop shadow.

---

### 5. Styles (e.g., `style` option)

**`style`**
- **Description:** Selects the overall display style of the captions. Different styles may interpret `highlight-color`, `word-color`, and other options differently.
- **Type:** String
- **Allowed Values:** 
  - `classic`: Standard subtitles with no special word highlighting.
  - `karaoke`: Shows each word "activating" in sequence, often using `word-color` and `highlight-color` to emphasize the currently spoken word.
  - `highlight`: The entire line is visible while the currently active word’s text color changes (`highlight-color`) over time. Multiple Dialogue events simulate a moving highlight.
  - `underline`: Similar to karaoke but underlines the active word instead of changing its color.
  - `word-by-word`: Displays each word individually, replacing the previous word as time progresses.
- **Default:** `classic`
- **Example:** `{"option": "style", "value": "karaoke"}` engages a karaoke-style display.

---

## Additional Behavior

- **Automatic Transcription:**  
  If neither `caption_srt` nor `caption_ass` is provided, the API will transcribe the video's audio to generate captions. Options like `replace` or `all-caps` then apply to the transcribed text.

- **Fallback Logic for Styles:**  
  Some styles (like `karaoke` and `highlight`) rely on word-level timing data from transcription. If word-level data is not available (e.g., using an SRT that doesn’t include word-level timestamps), the API attempts to evenly divide the segment duration among the words to simulate these effects.

- **Font Availability:**  
  If the specified `font-family` is not available on the system, the API returns an error. You can then choose a different font from the provided list.

---

## Error Handling

- **Invalid Fonts:**  
  If a chosen font is not found, the API responds with an error and a list of available fonts.
- **FFmpeg Errors:**  
  If the video cannot be processed, the API returns an error describing the issue (e.g., invalid video URL, unsupported format).
- **Invalid Values:**  
  If you provide invalid options or values (e.g., non-hex strings for colors, non-integer for `font-size`), the API may revert to defaults or return an error. Check logs and responses for details.

---

## Usage Scenarios and Tips

1. **Simple Setup:**  
   Provide only `video_url`. The API transcribes the audio and produces basic white captions at the bottom.

2. **Advanced Styling:**  
   Use a combination of `border-style=3`, a bright `outline-color`, and `highlight-color` for emphasis. Increase `font-size` and set `bold=true` for maximum readability during testing.

3. **Term Correction with `replace`:**  
   If transcription outputs "um" frequently, you can replace it with an empty string to remove filler words:
   ```json
   {"option": "replace", "value": {"um": ""}}
   ```

4. **Testing Different Styles:**
   - **Karaoke:**  
     ```json
     {"option": "style", "value": "karaoke"},
     {"option": "word-color", "value": "#00FF00"},
     {"option": "highlight-color", "value": "#FF00FF"}
     ```
     Makes each spoken word activate in sequence, changing colors as they are “spoken.”
   
   - **Highlight:**  
     ```json
     {"option": "style", "value": "highlight"},
     {"option": "highlight-color", "value": "#00FF00"}
     ```
     The entire line is visible while the active word changes color over time.

   - **Underline:**  
     ```json
     {"option": "style", "value": "underline"}
     ```
     The active word is underlined instead of recolored.

   - **Word-by-Word:**
     ```json
     {"option": "style", "value": "word-by-word"}
     ```
     Each word is displayed individually, replacing the previous one as time passes.
