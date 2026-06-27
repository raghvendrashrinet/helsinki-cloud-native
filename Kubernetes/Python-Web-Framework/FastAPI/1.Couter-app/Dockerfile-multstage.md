## Multistage 
Core philosophy: Separating your build-time tools from your actual production runtime.
 1. Massive Image Size Reduction (The Slim Down)
    - Single Stage: o install dependencies (like compiling C-extensions or running pip install), Python often needs extra system packages (gcc, g++, header files). If you use a single-stage Dockerfile, all those heavy build tools remain trapped in your final image forever.
    - Multi-Stage: The `builder` stage downloads the compilers, compiles the packages, and installs them. The final `runner` stage starts with a completely clean, tiny base image and only copies over the final installed artifacts.
    Result: Your container image drops from 800MB+ down to ~120MB.


```Dockerfile
# ==========================================
# STAGE 1: The Builder
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

# Install dependencies into a isolated local user directory
RUN pip install --no-cache-dir --user -r requirements.txt


# ==========================================
# STAGE 2: The Runtime (The only stage that gets deployed)
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

# 1. Copy over ONLY the compiled binaries/libraries from the builder stage
COPY --from=builder /root/.local /root/.local
COPY app.py .
# Note: Uncomment the line below if you switch to the Gunicorn setup later!
# COPY gunicorn_conf.py .

# 2. Update the environment path so Python can discover the Uvicorn/Gunicorn binaries
ENV PATH=/root/.local/bin:$PATH

# 3. 🔒 SECURITY BEST PRACTICE: Run as a non-root system user
RUN useradd -u 1001 appuser && chown -R appuser:appuser /app
USER 1001

EXPOSE 8000

# =========================================================================
# STARTUP COMMAND OPTIONS
# =========================================================================

# OPTION 1: Simple Uvicorn Engine (Active - perfect for Exercise 1.8)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# OPTION 2: Production Gunicorn Process Manager (Commented out)
# CMD ["gunicorn", "-c", "gunicorn_conf.py", "app:app"]
```
