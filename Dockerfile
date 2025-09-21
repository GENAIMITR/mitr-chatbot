# Use a stable slim Python image
FROM python:3.11-slim

# Prevents Python from writing .pyc files & buffers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Force noninteractive mode for apt-get
ARG DEBIAN_FRONTEND=noninteractive

# Install minimal system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies for sounddevice
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker cache)
COPY requirements.txt .

# Install Python deps
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source and other files
COPY . .

# Expose port
ENV PORT=8080
EXPOSE 8080

# Run the emoAI.py script directly since it contains the HTTP server
CMD ["python", "emoAI.py"]