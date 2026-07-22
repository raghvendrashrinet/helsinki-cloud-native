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
