## How the APP Should work
- "Get a random picture from Lorem Picsum like https://picsum.photos/1200 and display it in the project. Find a way to store the image so it stays the same for 10 minutes."

- After 10 minutes have passed, you might give the old pic still one more time, and for the next request, there should be a new picture

#### The concept

- We are not saving the actual picture. Instead, we are saving a small note (a text file) that tells us which picture to show and when we picked it.

##### Steps
1. The Location (/data) Your Kubernetes setup has a special folder inside your app called /data,
This folder is magical because it is actually connected to the hard drive of the computer (Node) running Kubernetes, not just the temporary app container.

2. The Tool (os and json modules) Python has built-in tools (modules) to talk to the hard drive:
- `os module:` Helps you check if a file exists
- `json module:` Helps you write your "note" in a format the computer can read easily later. We will save a tiny text file like cache.json
3. The Logic (Read -> Check -> Write) Every time a user visits your website, your app does this:
- Read: "Is there a file at /data/cache.json?"
 * If NO: Create one! (Pick a random image, write the URL and current time to the file).
 * If YES: Open it and read the time.
- Check: "Is the time written in the file older than 10 minutes?"
 * If NO (It's fresh): Just use the URL in the file. (Don't change anything).
 * If YES (It's old): Pick a new random image, update the file with the new URL and new time, and use the new image. 

 `image_cache.json`
 ```
 {
  "url": "https://picsum.photos/1200/800?random=482",
  "timestamp": 1720281600.55
 }
 ```
 Programm
 ```
 from flask import Flask, render_template_string
import os
import json
import time
import random

app = Flask(__name__)

# Configuration
# This path MUST match the mountPath in your Kubernetes Pod spec
CACHE_FILE_PATH = '/data/image_cache.json'
CACHE_DURATION_SECONDS = 600  # 10 minutes

def get_cached_image_url():
    current_time = time.time()
    
    # 1. Check if the cache file exists on the Persistent Volume
    if os.path.exists(CACHE_FILE_PATH):
        try:
            # 2. Read the existing data
            with open(CACHE_FILE_PATH, 'r') as f:
                data = json.load(f)
            
            stored_timestamp = data.get('timestamp', 0)
            stored_url = data.get('url')
            
            # 3. Check if the cache is still valid (less than 10 mins old)
            if current_time - stored_timestamp <= CACHE_DURATION_SECONDS:
                print(f"Cache hit: Serving image from {CACHE_FILE_PATH}")
                return stored_url
            else:
                print("Cache expired: Generating new image.")
        except Exception as e:
            print(f"Error reading cache: {e}. Generating new image.")

    # 4. Generate a new random image URL (if file missing or expired)
    # We add a random number to the URL to ensure Picsum gives a new image
    new_url = f"https://picsum.photos/1200/800?random={random.randint(1, 100000)}"
    
    # 5. Save the new URL and current timestamp to the Persistent Volume
    new_data = {
        'url': new_url,
        'timestamp': current_time
    }
    
    try:
        # Ensure the directory exists (good practice, though PV should handle it)
        os.makedirs(os.path.dirname(CACHE_FILE_PATH), exist_ok=True)
        
        with open(CACHE_FILE_PATH, 'w') as f:
            json.dump(new_data, f)
        print(f"Cache updated: Saved new URL to {CACHE_FILE_PATH}")
    except Exception as e:
        print(f"Error writing cache: {e}")
        
    return new_url

@app.route('/')
def home():
    # Get the URL (either cached or new)
    image_url = get_cached_image_url()
    
    # Simple HTML template
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Persistent Image Cache</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            img { max-width: 100%; height: auto; border: 5px solid #333; }
        </style>
    </head>
    <body>
        <h1>Devops with Kubernetes</h1>
        <p>Image changes every 10 minutes (Persistent Storage)</p>
        <img src="{{ img_url }}" alt="Random Cached Image">
    </body>
    </html>
    """
    
    return render_template_string(html_content, img_url=image_url)

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible from outside the pod
    app.run(host='0.0.0.0', port=3000, debug=True)   
    ```   
