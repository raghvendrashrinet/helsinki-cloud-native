import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from sse_starlette.sse import EventSourceResponse
import os

app = FastAPI()

LOG_FILE = "log.txt"
COUNTER_FILE = "pingpong_count.txt"


def read_count() -> int:
    if not os.path.exists(COUNTER_FILE):
        return 0
    try:
        with open(COUNTER_FILE, "r") as f:
            return int(f.read().strip() or 0)
    except ValueError:
        return 0


def increment_count() -> int:
    count = read_count() + 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count))
    return count


async def log_generator(request: Request):
    """
    Asynchronously reads the last line of the file repeatedly.
    Yields new lines only when the file changes.
    """
    last_position = 0
    try:
        while True:
            if await request.is_disconnected():
                break
            
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    # Move to the last known position to avoid re-reading everything
                    f.seek(last_position)
                    new_lines = f.readlines()
                    last_position = f.tell()
                    
                    for line in new_lines:
                        # Yield each new line as an SSE event
                        yield {"data": line.strip()}
            
            # Check every 1 second for new content
            await asyncio.sleep(1)
    except Exception as e:
        yield {"data": f"Error: {str(e)}"}

@app.get("/stream")
async def stream_logs(request: Request):
    """Endpoint that streams log updates."""
    return EventSourceResponse(log_generator(request))


def read_last_log_line() -> str:
    if not os.path.exists(LOG_FILE):
        return ""
    try:
        with open(LOG_FILE, "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            return lines[-1] if lines else ""
    except Exception:
        return ""


@app.get("/pingpong")
async def pingpong():
    """Increments the ping/pong counter and returns the last log line + counter as plain text."""
    count = increment_count()
    last_line = read_last_log_line()
    if last_line:
        text = f"{last_line}\nPing / Pongs: {count}"
    else:
        text = f"Ping / Pongs: {count}"
    return PlainTextResponse(content=text, media_type="text/plain")

@app.get("/", response_class=HTMLResponse)
async def get_viewer():
    """Serves the HTML viewer page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Log Viewer</title>
        <style>
            body { font-family: monospace; background: #1e1e1e; color: #00ff00; padding: 20px; }
            #log-container { white-space: pre-wrap; border: 1px solid #333; padding: 10px; height: 75vh; overflow-y: auto; background: #000; }
            #status { margin-bottom: 10px; font-size: 1.1rem; }
        </style>
    </head>
    <body>
        <h1>Live Log Stream</h1>
        <div id="status">Loading...</div>
        <div id="log-container"></div>
        <script>
            const eventSource = new EventSource("/stream");
            const container = document.getElementById("log-container");
            const status = document.getElementById("status");

            // Fetch /pingpong on load to increment counter and display last log line
            fetch('/pingpong')
                .then(r => r.text())
                .then(t => { status.textContent = t; })
                .catch(err => { status.textContent = 'Ping / Pongs: ?'; console.error(err); });

            eventSource.onmessage = function(event) {
                const line = document.createElement("div");
                line.textContent = event.data;
                container.appendChild(line);
                // Auto-scroll to bottom
                container.scrollTop = container.scrollHeight;
            };

            eventSource.onerror = function(err) {
                console.error("EventSource failed:", err);
                eventSource.close();
            };
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    # Run on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)   