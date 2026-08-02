import os
import sys  # FIXED: Required for sys.stderr logging
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

# Database Connection Info from Environment Variables
DB_HOST = os.getenv("POSTGRES_HOST", "postgres-svc")
DB_NAME = os.getenv("POSTGRES_DB", "todo_db")
DB_USER = os.getenv("POSTGRES_USER", "todo_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "todo_password")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=int(DB_PORT),
    )


def init_db():
    """Ensure todos table exists on app startup."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            content VARCHAR(255) NOT NULL
        );
    """
    )
    conn.commit()
    cur.close()
    conn.close()


# Initialize database table on startup
init_db()


@app.route("/todos", methods=["GET"])
def get_todos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT content FROM todos;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Extract single text string from each tuple row
    todos = [row[0] for row in rows]
    return jsonify(todos), 200


# FIXED: Removed duplicate decorator and function definition
@app.route("/todos", methods=["POST"])
def add_todo():
    data = request.get_json() or request.form
    new_content = data.get("content") if data else None

    # 1. REQUEST LOGGING: Log every incoming todo request
    print(f"[INFO] Incoming todo request: '{new_content}'", flush=True)

    if not new_content:
        print("[WARNING] Todo request rejected: Content is missing or empty.", file=sys.stderr, flush=True)
        return jsonify({"error": "Content required"}), 400

    # 2. 140-CHARACTER LIMIT CHECK: Reject and log if exceeded
    if len(new_content) > 140:
        print(
            f"[REJECTED] Todo exceeds 140 character limit ({len(new_content)} chars): '{new_content}'",
            file=sys.stderr,
            flush=True,
        )
        return jsonify({"error": "Todo message must be 140 characters or fewer."}), 400

    # 3. DATABASE INSERTION: Executes only if validation passes
    conn = get_db_connection()
    cur = conn.cursor()

    # Insert new todo item
    cur.execute(
        "INSERT INTO todos (content) VALUES (%s);",
        (new_content,)
    )
    conn.commit()

    # Fetch updated list of todos
    cur.execute("SELECT content FROM todos;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    todos = [row[0] for row in rows]
    return jsonify(todos), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)