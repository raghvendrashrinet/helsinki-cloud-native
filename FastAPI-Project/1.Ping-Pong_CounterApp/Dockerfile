FROM python:3.11-slim

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your FastAPI application code
COPY app.py .

EXPOSE 8000

# Start the application using Uvicorn directly
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]