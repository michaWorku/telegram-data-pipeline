FROM python:3.9-slim-bullseye

# Set environment variables for Python
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

# Install system dependencies
# These are needed for psycopg2-binary, telethon, and especially OpenCV (for ultralytics)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    git \
    # Common OpenCV dependencies for ultralytics
    libgl1-mesa-glx \
    libsm6 \
    libxrender1 \
    libxext6 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    # Install requirements, allowing pip to use its default cache
    && pip install -r requirements.txt

# Copy the rest of your application code
COPY . .

# Set default command (optional, can be overridden by docker-compose entrypoint)
CMD ["python", "app.py"]
