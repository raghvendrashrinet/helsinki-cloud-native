from flask import Flask, jsonify, request
import uuid
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
    # Return latest log + ping count
    return jsonify({
        "log": latest_log,
        "Ping / Pongs": ping_count
    })

@app.route("/pings", methods=["GET"])
def update_pings():
    global ping_count
    # Increment ping count when called by Ping Pong App
    ping_count += 1
    return jsonify({"message": "Ping count updated", "Ping / Pongs": ping_count})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
