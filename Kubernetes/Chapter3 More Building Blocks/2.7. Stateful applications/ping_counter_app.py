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
