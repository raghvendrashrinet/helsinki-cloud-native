from flask import Flask, render_template_string, make_response
import os
import json
import time
import random

app = Flask(__name__)

# Configuration
CACHE_FILE_PATH = '/data/image_cache.json'
CACHE_DURATION_SECONDS = 600  # 10 minutes

def get_cached_image():
    current_time = time.time()
    
    # 1. Check Persistent Volume for existing cache
    if os.path.exists(CACHE_FILE_PATH):
        try:
            with open(CACHE_FILE_PATH, 'r') as f:
                data = json.load(f)
            
            stored_timestamp = data.get('timestamp', 0)
            stored_seed = data.get('seed')
            
            # 2. Check if cache is valid (<= 10 mins)
            if current_time - stored_timestamp <= CACHE_DURATION_SECONDS:
                # flush=True ensures logs appear immediately in Docker/K8s
                print(f"✓ CACHE HIT: Serving seed '{stored_seed}'", flush=True)
                return f"https://picsum.photos/seed/{stored_seed}/1200/800", stored_timestamp
            else:
                print("✗ CACHE EXPIRED: Generating new seed.", flush=True)
        except Exception as e:
            print(f"Error reading cache: {e}", flush=True)

    # 3. Generate NEW seed (only happens once every 10 mins)
    new_seed = f"cache_{random.randint(1, 100000)}_{int(current_time)}"
    new_url = f"https://picsum.photos/seed/{new_seed}/1200/800"
    
    # 4. Save to Persistent Volume
    new_data = {
        'seed': new_seed,
        'url': new_url,
        'timestamp': current_time
    }
    
    try:
        os.makedirs(os.path.dirname(CACHE_FILE_PATH), exist_ok=True)
        with open(CACHE_FILE_PATH, 'w') as f:
            json.dump(new_data, f)
        print(f"✓ CACHE SAVED: New seed '{new_seed}' written to PV", flush=True)
    except Exception as e:
        print(f"Error writing cache: {e}", flush=True)
        
    return new_url, current_time

@app.route('/')
def home():
    image_url, timestamp = get_cached_image()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kubernetes Persistent Cache</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f4f4f4; }
            .container { background: white; padding: 20px; border-radius: 8px; display: inline-block; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            img { max-width: 100%; height: auto; border: 5px solid #333; border-radius: 4px; }
            .meta { margin-top: 15px; color: #666; font-size: 0.9em; }
            .input-section { margin-top: 30px; display: flex; gap: 10px; }
            .input-section input { 
                flex: 1;
                padding: 10px; 
                font-size: 14px; 
                border: 2px solid #ddd; 
                border-radius: 4px;
                box-sizing: border-box;
            }
            .input-section button { 
                background-color: #4CAF50; 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 14px;
                font-weight: bold;
                white-space: nowrap;
            }
            .input-section button:hover { background-color: #45a049; }
            .todos-section { margin-top: 30px; text-align: left; display: inline-block; }
            .todos-section h3 { margin-bottom: 15px; color: #333; }
            .todo-item { 
                background-color: #f9f9f9; 
                padding: 12px; 
                margin: 8px 0; 
                border-left: 4px solid #4CAF50; 
                border-radius: 4px;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Todo App</h1>
            <p>Image persists for 10 minutes even if container restarts.</p>
            <img src="{{ img_url }}" alt="Cached Image">
            
            <div class="input-section">
                <input type="text" placeholder="Enter a new todo ( max 140 characters)">
                <button>Send</button>
            </div>
            
            <div class="todos-section">
                <h3>Todos</h3>
                <div class="todo-item">✓ Learning Kubernetes</div>
                <div class="todo-item">✓ Deployment application to cluster</div>
                <div class="todo-item">✓ Configure persistent volume</div>
            </div>
            
            
        </div>
    </body>
    </html>
    """
    
    response = make_response(render_template_string(
        html_content, 
        img_url=image_url,
        timestamp=timestamp,
        current_time=time.time()
    ))
    
    # Prevent HTML caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

if __name__ == '__main__':
    # debug=True is fine for testing, but remember to rebuild image after changes
    app.run(host='0.0.0.0', port=3000, debug=True)   