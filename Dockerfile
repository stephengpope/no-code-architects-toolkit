# Base image
FROM python:3.9-slim

# Install system dependencies, build tools, and libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    tar \
    xz-utils \
    fonts-liberation \
    fontconfig \
    build-essential \
    yasm \
    cmake \
    meson \
    ninja-build \
    nasm \
    libssl-dev \
    libvpx-dev \
    libx264-dev \
    libx265-dev \
    libnuma-dev \
    libmp3lame-dev \
    libopus-dev \
    libvorbis-dev \
    libtheora-dev \
    libspeex-dev \
    libass-dev \
    libfreetype6-dev \
    libfontconfig1-dev \
    libgnutls28-dev \
    libaom-dev \
    libdav1d-dev \
    librav1e-dev \
    libsvtav1-dev \
    libzimg-dev \
    libwebp-dev \
    git \
    pkg-config \
    autoconf \
    automake \
    libtool \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# ... (keep the rest of the build steps unchanged)

# Set environment variables
ENV PATH="/usr/local/bin:${PATH}"
ENV WHISPER_CACHE_DIR="/app/whisper_cache"
ENV TRANSFORMERS_CACHE=/tmp/transformers_cache
ENV NUMBA_CACHE_DIR=/tmp/numba_cache
ENV PYTHONUNBUFFERED=1
ENV NUMBA_DISABLE_JIT=1

# Create cache directories and set permissions
RUN mkdir -p ${WHISPER_CACHE_DIR} && chmod 777 ${WHISPER_CACHE_DIR} && \
    mkdir -p /tmp/transformers_cache && chmod 777 /tmp/transformers_cache && \
    mkdir -p /tmp/numba_cache && chmod 777 /tmp/numba_cache

# Copy the requirements file first to optimize caching
COPY requirements.txt .

# Install Python dependencies, upgrade pip, and pre-download the Whisper model
RUN pip install openai-whisper && \
    pip install jsonschema && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir torch torchaudio --extra-index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir tortoise-tts && \
    pip install --no-cache-dir scipy && \
    python -c "import os; os.environ['WHISPER_CACHE_DIR'] = '${WHISPER_CACHE_DIR}'; import whisper; whisper.load_model('base')"

# Copy the rest of the application code
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
RUN mkdir -p /home/appuser/.cache && chown -R appuser:appuser /home/appuser/.cache
USER appuser

# Expose the port the app runs on
EXPOSE 8080

RUN echo '#!/bin/bash\n\
gunicorn --bind 0.0.0.0:8080 \
    --workers ${GUNICORN_WORKERS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-300} \
    --worker-class sync \
    app:app' > /app/run_gunicorn.sh && \
    chmod +x /app/run_gunicorn.sh

# Run the shell script
CMD ["/app/run_gunicorn.sh"]