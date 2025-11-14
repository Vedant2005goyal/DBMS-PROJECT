FROM python:3.10-slim

# Install system dependencies (including dlib build requirements)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    cmake-data \
    libopencv-dev \
    python3-opencv \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    libboost-python-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (skip face_recognition for now - install separately if needed)
RUN pip install --no-cache-dir Flask==2.3.2 Flask-CORS==4.0.0 Werkzeug==2.3.6 mysql-connector-python==8.0.33 opencv-python==4.8.0.74 numpy==1.24.3 python-dotenv==1.0.0 schedule==1.2.0

# Help dlib's CMake cope with newer CMake policy changes
ENV CMAKE_POLICY_VERSION_MINIMUM=3.5

# Try to install face_recognition and dlib
# If this fails during image build, the build will fail so we notice it.
RUN pip install --no-cache-dir dlib==19.24.2 face_recognition==1.3.0

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
