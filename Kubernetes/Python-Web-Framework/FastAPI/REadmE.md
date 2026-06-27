# High-Concurrency FastAPI Web Server

A production-ready, cloud-native FastAPI application structured with a robust ASGI/WSGI server process model. This setup is designed specifically for high-concurrency microservice architectures, containerized environments (Docker), and Kubernetes orchestration.

## 🚀 Key DevOps Features

*   **Asynchronous Engine:** Built on ASGI with FastAPI for high-performance, asynchronous request handling (ideal for I/O bound tasks and AI/ML model serving).
*   **Production Process Management:** Utilizes **Gunicorn** as a process monitor overseeing clustered **Uvicorn** worker processes.
*   **Kubernetes Native:** Includes a dedicated `/healthz` endpoint ready for Liveness and Readiness probes.
*   **Observability-Ready:** Features a mock `/metrics` endpoint structured in the native Prometheus exposition format for automated metric scraping.
*   **Container Security:** Optimized for multi-stage Docker builds running under non-root permissions.

---


## 🛠️ Architecture Overview

In production, Python apps should not run directly via development servers. This project implements a master-worker architecture:

```text
       ┌─────────────────────────────────────────────────────────┐
       │                    GUNICORN (Master)                    │
       │  • Manages process lifecycle   • Monitors system health │
       │  • Spawns/kills workers        • Re-spawns dead workers │
       └────────────────────────────┬────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │ (Controls)            │ (Controls)            │ (Controls)
            ▼                       ▼                       ▼
┌───────────────────────┐┌───────────────────────┐┌───────────────────────┐
│ Uvicorn Worker 1      ││ Uvicorn Worker 2      ││ Uvicorn Worker 3      │
│ (ASGI Engine)         ││ (ASGI Engine)         ││ (ASGI Engine)         │
│                       ││                       ││                       │
│  ┌─────────────────┐  ││  ┌─────────────────┐  ││  ┌─────────────────┐  │
│  │   FastAPI App   │  ││  │   FastAPI App   │  ││  │   FastAPI App   │  │
│  └─────────────────┘  ││  └─────────────────┘  ││  └─────────────────┘  │
└───────────────────────┘└───────────────────────┘└───────────────────────┘
```



The number of workers is mathematically tuned based on system resources:
$$\text{Workers} = (2 \times \text{CPU Cores}) + 1$$

---

## 💻 Local Development Setup

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Installation
Clone the repository and install the required production dependencies:
```bash
pip install fastapi uvicorn gunicorn
```
### 3. Running the Server
For Development (With Hot-Reload):
```
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
For Production Simulation (Gunicorn + Uvicorn Workers):
```
gunicorn -c gunicorn_conf.py app:app
```

| Endpoint | Method | Purpose | Target Audience |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Root Welcome Application Data | End User / Frontend |
| `/healthz` | `GET` | Cluster Liveness & Readiness Check | Kubernetes Kubelet |
| `/metrics` | `GET` | Prometheus Exposition Format Scrape Target | Prometheus Server |

#### Example Metrics Output
Navigating to http://localhost:8000/metrics exposes your app telemetry:
```
# HELP http_requests_total Total number of HTTP requests.
# TYPE http_requests_total counter
http_requests_total{endpoint="/"} 12
```

---
### 🐳 Containerization & Deployment Best Practices  
When moving this application to production, ensure you follow these strict cloud-native patterns:

- Multi-Stage Dockerfile: Use a build stage for compiling dependencies (if needed) and a minimal python:3.11-slim run stage to keep image footprints small and lower vulnerability attack surfaces.

- Non-Root Execution: Create a system user inside the Dockerfile (e.g., RUN useradd -u 1001 appuser) and drop privileges using USER 1001.

- Kubernetes Probes Configuration: Map your deployment manifest to look at the health endpoint with an initial delay to allow the Uvicorn workers to boot up completely:
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```






In production, Python apps should not run directly via development servers. This project implements a master-worker architecture:
