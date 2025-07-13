# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by psycopg2 (libpq-dev),
# telethon (libffi-dev, libssl-dev for cryptography),
# and ultralytics (OpenCV dependencies like libgl1-mesa-glx, libsm6, libxrender1, libxext6).
# Combine apt-get update and install in a single RUN command to minimize layers.
# Use && to ensure that if any command fails, the whole RUN command fails.
# Clean up apt lists immediately after installation to reduce image size.
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
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy only the requirements file first.
# This is CRUCIAL for leveraging Docker's build cache.
# If requirements.txt doesn't change, this layer and the subsequent pip install layer will be cached.
COPY requirements.txt .

# Install Python dependencies.
# --no-cache-dir: Reduces image size by not storing pip's cache during installation.
# --compile: Compiles Python source files to bytecode after installation, can speed up startup.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
# This layer will only be invalidated if your application code (excluding requirements.txt) changes.
COPY . .

# Expose the ports that FastAPI and Dagster UI will run on.
# For FastAPI
EXPOSE 8000 
# For Dagster UI
EXPOSE 3000 

# Default command to run the application.
# This can be overridden by docker-compose.yml for specific services.
CMD ["bash"]
