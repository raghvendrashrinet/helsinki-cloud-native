# 🐍 Python Web Servers: Uvicorn vs. Gunicorn

When deploying modern Python web frameworks like FastAPI, understanding the difference between **Uvicorn** and **Gunicorn** is essential for configuring your environment correctly.

---

## ⚡ 1. Uvicorn: The Application Server (ASGI)

Uvicorn is an **ASGI (Asynchronous Server Gateway Interface)** server. Its primary job is to translate raw network traffic into a format your Python application can execute.

* **What it does:** Natively interprets modern, asynchronous Python (`async`/`await`). It listens to a port, parses incoming HTTP/WebSocket data, passes it to FastAPI, and returns the response.
* **Key Strength:** Extremely fast performance, built using high-performance C-compiled components (`uvloop` and `httptools`).
* **Limitation:** It is a **single-process** worker. It can only utilize **one CPU core** at a time, leaving other cores on your server idle.

### 🐳 Solo Uvicorn Docker Configuration
When running Uvicorn solo, it acts as both the listener and the code executor.

* **The Startup Service:** `uvicorn`
* **Dockerfile Command:**
  ```dockerfile
  CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
