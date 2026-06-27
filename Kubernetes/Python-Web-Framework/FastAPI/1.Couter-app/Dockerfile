FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Installing requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app.py .

# How to start it , Two options

# Option A: Simple Uvicorn start (Perfect for your current exercise)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# Option B: Gunicorn Production start (Once you add gunicorn_conf.py)
# CMD ["gunicorn", "-c", "gunicorn_conf.py", "app:app"]
