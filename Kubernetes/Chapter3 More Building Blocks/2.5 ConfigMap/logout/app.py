from flask import Flask, jsonify, request, Response
import uuid
import os
import datetime
import threading
import time

app = Flask(__name__)

# Shared state
latest_log = None
ping_count = 0

def generate_logs():
    global latest_log
    while True:
        # Generate a new log entry every 5 seconds
        latest_log = f"{datetime.datetime.utcnow().isoformat()}Z: {uuid.uuid4()}"
        time.sleep(5)

# Background thread for log generation
threading.Thread(target=generate_logs, daemon=True).start()

@app.route("/", methods=["GET"])
def get_logs():
     # Read env var
    message = os.environ.get("MESSAGE", "No message")

    # Read file from container
    file_path = "/data/information.txt"
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
    except FileNotFoundError:
        file_content = "File not found"
    except UnicodeDecodeError:
        file_content = "Could not decode file"

    print("MESSAGE:", message)
    print("FILE CONTENT:", file_content)
    # Return plain text for every field with proper newlines
    text = (
        f"message: {message}\n"
        f"file_content: {file_content}\n"
        f"log: {latest_log}\n"
        f"ping_count: {ping_count}\n"
    )
    return Response(text, mimetype="text/plain")

@app.route("/pings", methods=["GET"])
def update_pings():
    global ping_count
    # Increment ping count when called by Ping Pong App
    ping_count += 1
    return jsonify({"message": "Ping count updated", "Ping / Pongs": ping_count})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
