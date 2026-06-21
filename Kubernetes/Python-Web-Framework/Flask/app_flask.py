from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # You can return plain text or raw HTML strings directly!
    return """
    <html>
        <head><title>Flask Demo</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>Hello from Flask! 🚀</h1>
            <p>This is a simple single-page web application.</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    # We can bind it to port 3005 just like your Kubernetes apps!
    app.run(host='0.0.0.0', port=3005)
