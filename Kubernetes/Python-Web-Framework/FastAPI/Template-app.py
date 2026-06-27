import time
from fastapi import FastAPI, Response, HTTPException

# 1. Initialize the Application
app = FastAPI(
    title="Production-Ready-API",
    description="A template for high-concurrency DevOps deployments",
    version="1.0.0"
)

# Mock state for metrics tracking
REQUEST_COUNT = 0


# 2. Your Application Routes (Fill your business logic here)
@app.get("/")
def read_root():
    """
    Main landing route. Replace or add more domain-specific routes below.
    """
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    return {"status": "success", "data": "Welcome to your FastAPI microservice!"}


# 🚀 3. DevOps Endpoint: Kubernetes Health Probes
@app.get("/healthz", status_code=200)
def health_check():
    """
    Used by Kubernetes Liveness/Readiness probes.
    Returns 200 if the app is healthy.
    """
    try:
        # Optional: Add database/cache ping logic here
        return {"status": "healthy", "timestamp": time.time()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unhealthy: {str(e)}")


# 📊 4. DevOps Endpoint: Prometheus Telemetry Scrape Target
@app.get("/metrics")
def metrics():
    """
    Exposes raw application metrics in Prometheus exposition format.
    """
    global REQUEST_COUNT
    prometheus_data = (
        f'# HELP http_requests_total Total number of HTTP requests.\n'
        f'# TYPE http_requests_total counter\n'
        f'http_requests_total{{endpoint="/"}} {REQUEST_COUNT}\n'
    )
    return Response(content=prometheus_data, media_type="text/plain")
