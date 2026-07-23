# README

## 1. Code Changes (Backend App)

Update the application execution block at the bottom of the backend app so it dynamically reads the `PORT` from environment variables instead of hardcoding `3000`.

Add `import os` at the top of the file, then replace the `if __name__ == '__main__':` block with the following:

```python
if __name__ == '__main__':
    # Dynamically read the application port from the environment
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
```

> This ensures the app can use the port provided by Kubernetes through environment variables.

---

## 2. Configuration

Pass configuration values to pods as environment variables defined either in a `ConfigMap` or directly in deployment manifests. In this example, a `ConfigMap` is used.

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-app-config
data:
  FRONTEND_PORT: "3000"
  BACKEND_PORT: "2345"
  BACKEND_URL: "http://todo-backend-svc:2345/todos"
```

### Frontend deployment environment variables

```yaml
env:
  - name: PORT
    valueFrom:
      configMapKeyRef:
        name: todo-app-config
        key: FRONTEND_PORT
  - name: BACKEND_URL
    valueFrom:
      configMapKeyRef:
        name: todo-app-config
        key: BACKEND_URL
```

### Backend deployment environment variables

```yaml
env:
  - name: PORT
    valueFrom:
      configMapKeyRef:
        name: todo-app-config
        key: BACKEND_PORT
```

---

## 3. Frontend App Code Changes

Update the frontend code to read `BACKEND_URL` from the environment and fall back to a default if needed.

```python
# --- BEFORE ---
# BACKEND_URL = "http://todo-backend-svc:2345/todos"

# --- AFTER ---
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://todo-backend-svc:2345/todos')
```

Then update the app execution block:

```python
# --- BEFORE ---
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=3000, debug=True)

# --- AFTER ---
if __name__ == '__main__':
    # Dynamically read the application port from the environment
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
```

---

## 4. Backend App Code Changes

Add `import os` at the top of the backend application file.

```python
import os  # <-- Make sure this import is added at the top of your file
```

Then update the startup block:

```python
if __name__ == '__main__':
    # Dynamically read the application port from the environment, fallback to 3000
    port = int(os.environ.get('PORT', 3000))

    # host='0.0.0.0' allows external traffic to connect.
    app.run(host='0.0.0.0', port=port)
```
	