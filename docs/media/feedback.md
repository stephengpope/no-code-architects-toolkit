# Media Feedback Portal

This endpoint serves a static web page for collecting media feedback.

## Endpoint

```
GET /v1/media/feedback
```

### Authentication

This endpoint does not require authentication and is publicly accessible.

### Response

Returns the HTML feedback form page.

## Static Files

Additional static files (CSS, JavaScript, images) can be accessed at:

```
GET /v1/media/feedback/<filename>
```

Replace `<filename>` with the path to the static resource relative to the static directory.

## Development

The static website files are stored in:

```
services/v1/media/feedback/static/
```

This directory contains:

- `index.html` - Main HTML file
- `css/styles.css` - Stylesheet
- `js/script.js` - JavaScript code
- `images/` - Directory for image assets

To modify the feedback page, edit these files directly.