##For ping app
# Use an official lightweight Python runtime as a parent image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for psycopg2 / Postgres connection
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt-lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app.py .

# Expose port 5000 for Flask
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
