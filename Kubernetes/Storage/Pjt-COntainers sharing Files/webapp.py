import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse
import os

app = FastAPI()

LOG_FILE = "log.txt"

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
            #log-container { white-space: pre-wrap; border: 1px solid #333; padding: 10px; height: 80vh; overflow-y: auto; background: #000; }
        </style>
    </head>
    <body>
        <h1>Live Log Stream</h1>
        <div id="log-container"></div>
        <script>
            const eventSource = new EventSource("/stream");
            const container = document.getElementById("log-container");

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
    # Run on port 5000
    uvicorn.run(app, host="0.0.0.0", port=5000)   
