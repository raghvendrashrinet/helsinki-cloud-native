
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
