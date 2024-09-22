# Use the official Python image as the base image
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 \
    curl \
    ca-certificates \
    build-essential \
    pkg-config \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Add the NVIDIA package repositories and keys
RUN curl -s -L https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/3bf863cc.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/ /" > /etc/apt/sources.list.d/cuda.list

# Update and install CUDA toolkit
RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-toolkit-11-8 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for CUDA
ENV CUDA_HOME=/usr/local/cuda-11.8
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Verify CUDA installation by checking nvcc
RUN nvcc --version

# Install additional dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-dev \
    wget \
    tar \
    xz-utils \
    fonts-liberation \
    fontconfig \
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
    libsvtav1-dev \
    libzimg-dev \
    libwebp-dev \
    git \
    autoconf \
    automake \
    libtool \
    && rm -rf /var/lib/apt/lists/*

# Install Rust and Cargo
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH=/root/.cargo/bin:${PATH}

# Verify Cargo installation
RUN cargo --version

# Install SRT from source
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

# Manually build and install fdk-aac
RUN git clone https://github.com/mstorsjo/fdk-aac && \
    cd fdk-aac && \
    autoreconf -fiv && \
    ./configure && \
    make -j$(nproc) && \
    make install && \
    cd .. && rm -rf fdk-aac

# Install nv-codec-headers from the updated repository
RUN git clone https://github.com/FFmpeg/nv-codec-headers.git && \
    cd nv-codec-headers && \
    make install && \
    cd ..

# Use the official Python image as the base image
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 \
    curl \
    ca-certificates \
    build-essential \
    pkg-config \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Add the NVIDIA package repositories and keys
RUN curl -s -L https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/3bf863cc.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/ /" > /etc/apt/sources.list.d/cuda.list

# Update and install CUDA toolkit
RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-toolkit-11-8 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for CUDA
ENV CUDA_HOME=/usr/local/cuda-11.8
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64

# Verify CUDA installation by checking nvcc
RUN nvcc --version

# Install additional dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-dev \
    wget \
    tar \
    xz-utils \
    fonts-liberation \
    fontconfig \
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
    libsvtav1-dev \
    libzimg-dev \
    libwebp-dev \
    git \
    autoconf \
    automake \
    libtool \
    && rm -rf /var/lib/apt/lists/*

# Install Rust and Cargo
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH=/root/.cargo/bin:${PATH}

# Verify Cargo installation
RUN cargo --version

# Install SRT from source
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

# Manually build and install fdk-aac
RUN git clone https://github.com/mstorsjo/fdk-aac && \
    cd fdk-aac && \
    autoreconf -fiv && \
    ./configure && \
    make -j$(nproc) && \
    make install && \
    cd .. && rm -rf fdk-aac

# Install nv-codec-headers from the updated repository
RUN git clone https://github.com/FFmpeg/nv-codec-headers.git && \
    cd nv-codec-headers && \
    make install && \
    cd ..

# Ensure CUDA is correctly linked for FFmpeg
ENV PKG_CONFIG_PATH=${CUDA_HOME}/lib64/pkgconfig:/usr/local/lib/pkgconfig

# Build and install FFmpeg with NVIDIA GPU hardware acceleration (split into multiple RUN instructions)
RUN git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg 
RUN cd ffmpeg && git checkout n7.0.2 
RUN PATH="${CUDA_HOME}/bin:${PATH}"  # Set PATH before configure
RUN cd ffmpeg && ./configure --prefix=/usr/local \
    --enable-gpl \
    --enable-pthreads \
    --enable-nonfree \
    --enable-libnpp \
    --extra-cflags="-I${CUDA_HOME}/include" \
    --extra-ldflags="-L${CUDA_HOME}/lib64" \
    --disable-static \
    --enable-shared \
    --enable-libaom \
    --enable-libdav1d \
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
    --enable-gnutls \
    --nvccflags="-gencode arch=compute_61,code=sm_61 -O2" && \ 
    make -j$(nproc) && \
    make install 
RUN cd .. && rm -rf ffmpeg

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
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir openai-whisper && \
    pip3 install --no-cache-dir -r requirements.txt && \
    python3 -c "import os; os.environ['WHISPER_CACHE_DIR'] = '${WHISPER_CACHE_DIR}'; import whisper; whisper.load_model('base')"

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