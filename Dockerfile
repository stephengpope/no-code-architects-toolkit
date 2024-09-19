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
    && rm -rf /var/lib/apt/lists/*

# Install SRT from source (latest version using cmake)
RUN git clone https://github.com/Haivision/srt.git && \
    cd srt && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && \
    cd ../.. && rm -rf srt

# Install SVT-AV1 from source
RUN git clone https://gitlab.com/AOMediaCodec/SVT-AV1.git && \
    cd SVT-AV1 && \
    git checkout v0.9.0 && \
    cd Build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && \
    cd ../.. && rm -rf SVT-AV1

# Install libvmaf from source
RUN git clone https://github.com/Netflix/vmaf.git && \
    cd vmaf/libvmaf && \
    meson build --buildtype release && \
    ninja -C build && \
    ninja -C build install && \
    cd ../.. && rm -rf vmaf && \
    ldconfig  # Update the dynamic linker cache

# Manually build and install fdk-aac (since it is not available via apt-get)
RUN git clone https://github.com/mstorsjo/fdk-aac && \
    cd fdk-aac && \
    autoreconf -fiv && \
    ./configure && \
    make -j$(nproc) && \
    make install && \
    cd .. && rm -rf fdk-aac

# Build and install FFmpeg with all required features (without macOS-specific options)
RUN git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg && \
    cd ffmpeg && \
    git checkout n7.0.2 && \
    ./configure --prefix=/usr/local \
    --enable-gpl \
    --enable-pthreads \
    --enable-neon \
    --enable-libaom \
    --enable-libdav1d \
    --enable-librav1e \
    --enable-libsvtav1 \
    --enable-libvmaf \
    --enable-libzimg \
    --enable-libx264 \
    --enable-libx265 \
    --enable-libvpx \
    --enable-libwebp \
    --enable-libmp3lame \
    --enable-libopus \
    --enable-libvorbis \
    --enable-libtheora \
    --enable-libspeex \
    --enable-libass \
    --enable-libfreetype \
    --enable-fontconfig \
    --enable-libsrt \
    --enable-gnutls && \
    make -j$(nproc) && \
    make install && \
    cd .. && rm -rf ffmpeg

# Add /usr/local/bin to PATH (if not already included)
ENV PATH="/usr/local/bin:${PATH}"

# Set work directory
WORKDIR /app

# Set environment variable for Whisper cache
ENV WHISPER_CACHE_DIR="/app/whisper_cache"

# Create cache directory
RUN mkdir -p ${WHISPER_CACHE_DIR} && chmod 777 ${WHISPER_CACHE_DIR}

# Copy the requirements file first to optimize caching
COPY requirements.txt .

# Install Python dependencies, upgrade pip, and pre-download the Whisper model
RUN pip install openai-whisper && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "import os; os.environ['WHISPER_CACHE_DIR'] = '${WHISPER_CACHE_DIR}'; import whisper; whisper.load_model('base')"

# Copy the rest of the application code
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8080

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "300", "app:app"]
