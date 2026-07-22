## Postgres Implementation

#### Key Steps
1. - Create Headless Service (clusterIP: None):
   - Registers postgres-svc in your cluster’s internal DNS.
   -  Your Python application will be able to connect via host address: `postgres-svc:5432 (or postgres-ss-0.postgres-svc:5432).`
2. Database Auto-Initialization:
   - Setting `POSTGRES_DB: "pingpong_db"` automatically creates the database when the container boots for the first time.
3. Dynamic Volume Provisioning:
   - volumeClaimTemplates automatically creates and binds a PersistentVolumeClaim named postgres-data-postgres-ss-0 using local-path.
   - Data will persist even if the pod restarts or is deleted.

---

#### PostgreSQL Manifest (postgres-db.yaml)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-svc
  labels:
    app: postgres
spec:
  ports:
    - port: 5432
      name: postgres
  clusterIP: None
  selector:
    app: postgres
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres-ss
spec:
  serviceName: postgres-svc
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
        - name: postgres
          image: postgres:16
          ports:
            - containerPort: 5432
              name: postgres
          env:
            - name: POSTGRES_DB
              value: "pingpong_db"
            - name: POSTGRES_USER
              value: "postgres"
            - name: POSTGRES_PASSWORD
              value: "postgres" # Update or move to Secrets for production
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: postgres-data
      spec:
        accessModes: [ "ReadWriteOnce" ]
        storageClassName: local-path
        resources:
          requests:
            storage: 100Mi
```

#### Steps to Deploy & Verify
1. Apply the Manifest
```Bash
kubectl apply -f postgres-db.yaml
```
2. Verify Pod and PVC
Check if the StatefulSet pod is up and the storage PVC is bound:

```Bash
kubectl get statefulset,pods,pvc
```
3. Test Database Connection
As suggested in the course hints, you can quickly spin up an interactive debugging pod to verify PostgreSQL is accepting connections:

```Bash
kubectl run -it --rm --restart=Never --image postgres psql-debug -- psql postgres://postgres:postgres@postgres-svc:5432/pingpong_db
```
If it successfully connects and opens the pingpong_db=> prompt, your database infrastructure is fully ready!
