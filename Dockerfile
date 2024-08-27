# Base image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WHISPER_MODEL=base \
    WHISPER_CACHE_DIR=/models/whisper

# Set work directory
WORKDIR /app

# Copy requirements.txt first (for caching)
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download the Whisper model and store it in the specified directory
RUN mkdir -p $WHISPER_CACHE_DIR && \
    python -c "import whisper; whisper.load_model('$WHISPER_MODEL', download_root='$WHISPER_CACHE_DIR')"

# Copy the rest of the application code
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser /app /models
USER appuser

# Expose the port the app runs on
EXPOSE 8080

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "300", "app:app"]
