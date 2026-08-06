from flask import Flask, jsonify
import requests

app = Flask(__name__)

pong_count = 0

# Internal ClusterIP Service for Log Output App
LOG_OUTPUT_URL = "http://logoutput-svc:2345/pings"

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "Welcome to Ping Pong App",
        "hint": "Use /pingpong to trigger pings",
        "current_pongs": pong_count
    })

@app.route("/pingpong", methods=["GET"])
def pingpong():
    global pong_count
    pong_count += 1

    try:
        requests.get(LOG_OUTPUT_URL)
    except Exception as e:
        return jsonify({"error": f"Failed to notify Log Output App: {e}"}), 500

    return jsonify({
        "message": "Pong incremented",
        "current_pongs": pong_count
    })

if __name__ == "__main__":
    # Flask app listens on container port 5000
    app.run(host="0.0.0.0", port=5000)
