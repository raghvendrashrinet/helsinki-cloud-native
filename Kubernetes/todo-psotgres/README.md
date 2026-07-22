
```
├── Backend/
│   ├── backend.py            # Updated to connect to Postgres using SQLAlchemy/Psycopg2
│   ├── alembic/               # Alembic migration files
│   ├── alembic.ini
│   └── Dockerfile
├── Frontend/
│   ├── frontend.py           # Unchanged (still talks to todo-backend via HTTP)
│   └── Dockerfile
└── manifests/           
    ├── postgres-secret.yaml  # Credentials for Postgres
    ├── postgres-db.yaml      # StatefulSet + Headless Service for Postgres
    ├── db-migration-job.yaml # Kubernetes Job to build tables
    ├── backend-deployment.yaml
    ├── backend-svc.yaml
    ├── frontend-deployment.yaml
    ├── frontend-svc.yaml
    └── ingress.yaml

```
Frontend-> Backend -> DB Flow 
```
+-------------------+
|   User Request    |
|   (HTTP / API)    |
+-------------------+
          |
          v
+-----------------------------+
|   App Pod Logic             |
|-----------------------------|
|1.Load DB Connection string  |
|   "postgresql://.../todo_db"|
| 2. Parse into components:   |
|    - user: todo_user        |
|    - password: todo_password|
|    - host: postgres-svc     |
|    - port: 5432             |
|    - db: todo_db            |
| 3. Open connection          |
|-----------------------------|
| 1. Receive request          |
| 2. Extract "id" (string)    |
|    e.g. id = "123"          |
| 3. Build query string:      |
|    "SELECT * FROM users     |
|     WHERE id = '123';"      |
| 4. Send query to DB Service |
+-----------------------------+
          |
          v
+-------------------+
|   DB Service      |
|   ClusterIP:5432  |
+-------------------+
          |
          v
+-----------------------------+
|   DB Pod (PostgreSQL/MySQL) |
|-----------------------------|
| 1. Parse SQL string         |
| 2. Execute query            |
| 3. Return result set        |
+-----------------------------+
          |
          v
+-------------------+
|   App Pod Logic   |
|-------------------|
| 5. Process rows   |
| 6. Format JSON    |
| 7. Send response  |
+-------------------+
          |
          v
+-------------------+
|   User Response   |
+-------------------+
```

### Step 1: Add Database Secrets & StatefulSet
Create `manifests/postgres-db.yaml` to deploy PostgreSQL with persistent storage.
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
stringData:
  POSTGRES_USER: todo_user
  POSTGRES_PASSWORD: todo_password
  POSTGRES_DB: todo_db
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-svc
spec:
  clusterIP: None  # Headless Service for StatefulSet
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: "postgres-svc"
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgresql
          image: postgres:15-alpine
          ports:
            - containerPort: 5432
          envFrom:
            - secretRef:
                name: postgres-secret
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
              subPath: postgres
  volumeClaimTemplates:
    - metadata:
        name: postgres-data
      spec:
        accessModes: [ "ReadWriteOnce" ]
        resources:
          requests:
            storage: 2Gi
```
---
### Step 2: Set Up Database Migration (Job)
Rather than having backend.py create tables at runtime, use a Kubernetes Job to create the tables before deploying the backend pods.

Create manifests/db-migration-job.yaml:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: postgres-migration-job
spec:
  ttlSecondsAfterFinished: 120
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: db-migrator
          image: <your-docker-hub-username>/todo-backend:v2 # Your built backend image
          command: ["alembic", "upgrade", "head"]
          env:
            - name: DATABASE_URL
              value: "postgresql://todo_user:todo_password@postgres-svc:5432/todo_db"
```
---
### Step 3: Update Backend/backend.py
Modify your Flask backend to fetch and store todos in PostgreSQL via SQLAlchemy instead of using an in-memory todos = [...] array.
```yaml
import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Fetch database URL from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://todo_user:todo_password@postgres-svc:5432/todo_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Todo Model
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)

@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([todo.content for todo in todos]), 200

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json() or request.form
    new_content = data.get("content")
    
    if new_content:
        new_todo = Todo(content=new_content)
        db.session.add(new_todo)
        db.session.commit()
        
        todos = Todo.query.all()
        return jsonify([todo.content for todo in todos]), 201
    
    return jsonify({"error": "Content required"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
```
---

### Step 4: Add initContainers to backend-deployment.yaml
To ensure the todo-backend pods do not crash if Postgres or the migration takes a few seconds to boot, add an initContainer to manifests/backend-deployment.yaml:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      initContainers:
        # Wait for Postgres port to respond before starting Flask backend
        - name: wait-for-postgres
          image: busybox:1.36
          command:
            - sh
            - -c
            - "until nc -z postgres-svc 5432; do echo 'Waiting for Postgres...'; sleep 2; done;"
      containers:
        - name: backend
          image: <your-docker-hub-username>/todo-backend:v2
          ports:
            - containerPort: 3000
          env:
            - name: DATABASE_URL
              value: "postgresql://todo_user:todo_password@postgres-svc:5432/todo_db"
```
---
### Step 5: Order of Deployment
When applying the changes, execute them in this specific order:
```bash
# 1. Deploy PostgreSQL (StatefulSet & Service)
kubectl apply -f manifests/postgres-db.yaml

# 2. Wait until PostgreSQL is ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=60s

# 3. Run the Database Migration Job
kubectl apply -f manifests/db-migration-job.yaml

# 4. Wait for the Migration Job to finish successfully
kubectl wait --for=condition=complete job/postgres-migration-job --timeout=60s

# 5. Apply remaining Frontend, Backend, Services, and Ingress
kubectl apply -f manifests/backend-deployment.yaml
kubectl apply -f manifests/backend-svc.yaml
kubectl apply -f manifests/frontend-deployment.yaml
kubectl apply -f manifests/frontend-svc.yaml
kubectl apply -f manifests/ingress.yaml
```
