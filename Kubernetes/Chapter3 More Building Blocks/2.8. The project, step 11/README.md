
```
├── Frontend/
│   ├── frontend.py           # Unchanged (still talks to todo-backend via HTTP)
│   └── Dockerfile
└── manifests/
    ├── 01-Configmap.yaml     # ConfigMap containing POSTGRES_HOST, DB, USER, PORT, etc.
    ├── postgres-secret.yaml  # Credentials for Postgres (POSTGRES_PASSWORD)
    ├── postgres-db.yaml      # StatefulSet / Deployment + Service for Postgres
    ├── backend-deployment.yaml
    ├── backend-svc.yaml
    ├── frontend-deployment.yaml
    ├── frontend-svc.yaml
    └── ingress.yaml
```
Frontend-> Backend -> DB Flow 
```
Frontend -> Backend -> DB Flow

+-------------------+
|   User Request    |
|   (HTTP / API)    |
+-------------------+
          |
          v
+------------------------------------+
|   App Pod Logic                    |
|------------------------------------|
| 1. Read Env Variables:             |
|    - POSTGRES_HOST (postgres-svc)  |
|    - POSTGRES_DB (todo_db)         |
|    - POSTGRES_USER (todo_user)     |
|    - POSTGRES_PASSWORD (Secret)    |
|    - POSTGRES_PORT (5432)          |
| 2. init_db() on startup            |
|    Creates table if not exists     |
| 3. Connect directly via psycopg2   |
+------------------------------------+
          |
          v
+-------------------+
|   DB Service      |
|   ClusterIP:5432  |
+-------------------+
          |
          v
+-----------------------------+
|   DB Pod (PostgreSQL)       |
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
| 4. Process rows   |
| 5. Format JSON    |
| 6. Send response  |
+-------------------+
          |
          v
+-------------------+
|   User Response   |
+-------------------+
```



