FROM python:3.10-slim

WORKDIR /app

# Copy dependencies first to leverage Docker caching layers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY backend.py .

# Use CMD instead of RUN to execute the server at container runtime
CMD ["python", "backend.py"]
