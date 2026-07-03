## Multistage Dokcer file ,Production gunicorn + Uvicorn 
# ==========================================
# STAGE 1: The Builder
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies into an isolated local user directory
RUN pip install --no-cache-dir --user -r requirements.txt


# ==========================================
# STAGE 2: The Runtime (The production image)
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

# 1. Copy over dependencies and application files from your FastAPI folder
COPY --from=builder /root/.local /root/.local
COPY Counter.py ./app.py
COPY gunicorn_conf.py .

# 2. Update environment path so Python can find Uvicorn/Gunicorn binaries
ENV PATH=/root/.local/bin:$PATH

# 3. 🔒 SECURITY BEST PRACTICE: Run as a non-root system user
RUN useradd -u 1001 appuser && chown -R appuser:appuser /app
USER 1001

EXPOSE 8000

# 4. Start Gunicorn with Uvicorn async workers as detailed in your architecture docs
CMD ["gunicorn", "-c", "gunicorn_conf.py", "app:app"]
