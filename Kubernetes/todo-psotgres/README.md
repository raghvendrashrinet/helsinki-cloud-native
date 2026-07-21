
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
