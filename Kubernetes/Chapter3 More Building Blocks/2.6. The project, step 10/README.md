
## Exercise 2.4 The project step 9 - separate 


## Objective
The goal of this exercise is to organize and isolate cluster workloads using Kubernetes **Namespaces**. Instead of deploying everything into the `default` namespace, the applications created in Exercise 2.1 (Log Output and Ping Pong) are migrated into a dedicated namespace named `project`.

## Architecture and Networking
Follow the Excercise 2.2 for application architecture and detail working , the excercise 2.12 section below


---

## How to Deploy

There are two valid ways to handle the namespace migration for this exercise:

### Method 1: Updating the Manifests 
You explicitly add the namespace to the `metadata` block of every YAML file (`00-namespace.yaml`(00 prefix it makes first to fire), deployments, services, and ingress).

**Example:**
```yaml
metadata:
  
  namespace: project
```

Apply : `kubectl apply -f manifests/`

### Method 2: Using the CLI Flag (Imperative Approach)
If you prefer not to touch or modify your existing manifest files from Exercise 2.1, you can leave the YAML files exactly as they are. You must create the namespace first, and then explicitly force the resources into the namespace using the command line flag.
```bash
kubectl create namespace project
kubectl apply -f manifests/ -n project
```

### Verify 
```bash
kubectl get pods -n project
kubectl get svc -n project
kubectl get ingress -n project
```

--- 






--- 
#### Todo App Step-8

- In Step 7, you have a single monolith app (todo-app) 
that handles the UI, downloads/caches the daily image via a Persistent Volume, and displays a hardcoded list of todos.

**For Step 8, the exercise wants you to split the data management out into a separate microservice called `todo-backend`**

You are going from 1 App to 2 Apps communicating via HTTP:

- `todo-app (Your existing Frontend):` 
  It no longer keeps the list of todos. Instead, it makes internal HTTP requests to the new backend to fetch or save them.
- `todo-backend (The New Backend):`
  - A brand new, lightweight server app (e.g., written in Python/Flask or Node.js) running in its own container.
  - Keeps the list of todo items in an in-memory list or array.
  - Exposes two HTTP endpoints: GET /todos and POST /todos.

#### 2. The Port Strategy (
  - todo-app (Frontend)	3000	   --> 2345 svc(todo-frontend-svc)
  - todo-backend (Backend)	3000 --> 2345 svc(todo-backend-svc)

##### Folder Structure
```
├── Backend/
│   ├── backend.py
│   └── Dockerfile
├── Frontend/
│   ├── frontend.py
│   └── Dockerfile
└── manifests/           
    ├── backend-deployment.yaml
    ├── backend-svc.yaml
    ├── frontend-deployment.yaml
    └── frontend-svc.yaml
    └── ingress.yaml
```
#### 3. Step-by-Step Implementation Guide
#####  Step A: Build the new todo-backend applicatio
```python
# main.py (for the todo-backend)
from flask import Flask, jsonify, request

app = Flask(__name__)

# Simple in-memory storage for this step
todos = ["Learn JavaScript", "Learn React", "Build a project"]

@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(todos), 200

@app.route('/todos', methods=['POST'])
def add_todo():
    # Expecting JSON or Form data depending on how your frontend sends it
    data = request.get_json() or request.form
    new_todo = data.get("content")
    if new_todo:
        todos.append(new_todo)
    return jsonify(todos), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
```
- Dockerize this backend application and push it to your Docker Hub registry.

##### Step B: Update your todo-app (Frontend) code
Modify your existing frontend server logic so that when a user loads the page:
1. The frontend uses a library like requests (Python) or axios (Node.js) to send an internal cluster request to http://todo-backend-svc:2345/todos.

2. It takes that array of todos and injects it into your HTML template.

3. When a user submits a new todo via the form, the frontend catches the POST, passes it along to http://todo-backend-svc:2345/todos, and re-renders the page.

##### Step C: Add the Kubernetes Manifests and deploy
 `/manifest/'
```bash
kubectl apply -f manifests/
```
---
#### Verify app running
**Method A** : Verification via Port-Forwarding
```
 kubectl port-forward service/todo-frontend-svc 82:2345
```
Access the UI : Open Browser and navigate : `http://localhost:82`

**Method B**: Verification via Ingress (Traefik)
The project includes an ingress.yaml configuration to route traffic using Traefik.

Access the Frontend UI: Navigate to your local Traefik router endpoint:
```
 http://localhost:8081/
```
##### ⚠️ Note on Backend Exposure (Demo Only):
In a production architecture, the backend service (todo-backend-svc) remains an internal ClusterIP and is never exposed via Ingress. However, for the sake of this demo,the Ingress manifest explicitly exposes the backend routing rule:

```yaml
- backend:
    service:
      name: todo-backend-svc
      port:
        number: 2345
  path: /todos
  pathType: Exact
```
Test : `http://localhost:8081/todos`


