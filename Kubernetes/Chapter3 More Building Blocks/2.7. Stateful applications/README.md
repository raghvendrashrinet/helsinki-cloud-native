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
import os
import psycopg2
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Internal ClusterIP Service for Log Output App
LOG_OUTPUT_URL = "http://logoutput-svc:2345/pings"

# Database Connection Info from Environment Variables
DB_HOST = os.getenv("POSTGRES_HOST", "postgres-svc")
DB_NAME = os.getenv("POSTGRES_DB", "pingpong_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def init_db():
    """Ensure counter table exists and seed initial row if empty."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS counter_table (
            id INT PRIMARY KEY,
            counter INT NOT NULL
        );
    """)
    cur.execute("""
        INSERT INTO counter_table (id, counter)
        VALUES (1, 0)
        ON CONFLICT (id) DO NOTHING;
    """)
    conn.commit()
    cur.close()
    conn.close()

# Initialize database on app startup
init_db()

def get_current_count():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT counter FROM counter_table WHERE id = 1;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

@app.route("/", methods=["GET"])
def root():
    pong_count = get_current_count()
    return jsonify({
        "message": "Welcome to Ping Pong App",
        "hint": "Use /pingpong to trigger pings",
        "current_pongs": pong_count
    })

@app.route("/pingpong", methods=["GET"])
def pingpong():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Atomically increment counter in Postgres
    cur.execute("""
        UPDATE counter_table
        SET counter = counter + 1
        WHERE id = 1
        RETURNING counter;
    """)
    pong_count = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    try:
        requests.get(LOG_OUTPUT_URL)
    except Exception as e:
        return jsonify({"error": f"Failed to notify Log Output App: {e}"}), 500

    return jsonify({
        "message": "Pong incremented",
        "current_pongs": pong_count
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
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



---
### If you want all manifest to run at once with single command `apply -f /manifest` 
### Then add Init-Container in Ping-Deployemnt app ,as this will ensure the postgress pod up and runing before app pods are intialized
```yaml
 # --- THIS IS THE CRITICAL PART ---
      initContainers:
      - name: wait-for-db
        image: busybox:1.36
        command: ['sh', '-c', 'until nc -z postgres-svc 5432; do echo waiting for postgres; sleep 2; done']
      # ---------------------------------
```
---
1. Updated Python Logic (app.py)
Here is how you can update app.py using psycopg2 (or psycopg2-binary). It will:
- Connect to PostgreSQL using environment variables.
- Ensure the required table (counter_table) exists on startup.
- Read and increment the counter in the DB every time /pingpong is requested.

```python
import os
import psycopg2
from flask import Flask

app = Flask(__name__)

# Retrieve database connection settings from Environment Variables
DB_HOST = os.getenv("POSTGRES_HOST", "postgres-svc")
DB_NAME = os.getenv("POSTGRES_DB", "pingpong_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def init_db():
    """Create table if it doesn't exist and initialize counter to 0."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS counter_table (
            id INT PRIMARY KEY,
            counter INT NOT NULL
        );
    """)
    # Insert initial counter row if table is completely empty
    cur.execute("""
        INSERT INTO counter_table (id, counter)
        VALUES (1, 0)
        ON CONFLICT (id) DO NOTHING;
    """)
    conn.commit()
    cur.close()
    conn.close()

# Initialize DB on start
init_db()

@app.route("/")
def hello():
    return "Ping-pong App is running"

@app.route("/pingpong")
def pingpong():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Increment counter directly in PostgreSQL
    cur.execute("""
        UPDATE counter_table
        SET counter = counter + 1
        WHERE id = 1
        RETURNING counter;
    """)
    new_count = cur.fetchone()[0]
    conn.commit()
    
    cur.close()
    conn.close()
    
    return f"pong {new_count}"

# Optional route to view current count without incrementing
@app.route("/count")
def get_count():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT counter FROM counter_table WHERE id = 1;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return str(count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```
---
#### 2. Dependencies (requirements.txt)
Make sure psycopg2-binary is included in your project dependencies so Python can communicate with PostgreSQL:
```
flask
psycopg2-binary
requests
```




#### Get PostgreSQL pod and login
`kubectl get pods -l app=postgres ` 
`kubectl exec -it <pod-name> -- psql -U postgres -d pingpong_db   ` 
#### List all tables: \dt

* List all databases: `\l`
* Connect to a specific database: `\c database_name`
* Query table data: `SELECT * FROM table_name LIMIT 10;`
* Exit psql: `\q`

