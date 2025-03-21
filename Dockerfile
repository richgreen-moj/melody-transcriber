# Use a base image with Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including ffmpeg for audio processing)
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install "numpy<2" --force-reinstall


# Clone and install Demucs
RUN git clone https://github.com/adefossez/demucs.git && \
    pip install ./demucs

# Set the environment variable to use OpenBLAS with OpenMP
ENV OPENBLAS_NUM_THREADS=1 
    # TORCHAUDIO_USE_BACKEND_DISPATCHER=1

# Copy the Python script into the container
COPY transcribe.py .

# Set the default command
ENTRYPOINT ["python", "transcribe.py"]
