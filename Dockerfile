# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by psycopg2 and other libraries
# For psycopg2: libpq-dev
# For Telethon: libffi-dev, libssl-dev (might be needed for cryptography)
# For YOLOv8 (Ultralytics): various image processing libraries might be needed,
# though pip install ultralytics often handles most Python dependencies.
# This is a good starting point, add more if build errors occur.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port FastAPI will run on (if applicable, for direct access)
EXPOSE 8000

# Command to run the application (e.g., start FastAPI or Dagster webserver)
# This will be overridden by docker-compose.yml for specific services.
CMD ["bash"]
