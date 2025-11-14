FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
# Copy frontend for serving
COPY frontend/ ./frontend/

# Create directories
RUN mkdir -p backend/student_photos backend/logs

# Set working directory to backend
WORKDIR /app/backend

# Expose port
EXPOSE 5000

# Default command
CMD ["python", "api.py"]
