from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
      <head><title>Jaymi Boot Portal</title></head>
      <body style="background:black;color:white;font-family:monospace;text-align:center;padding-top:20%;">
        <h1>Jaymi is awake.</h1>
        <p>You're not dreaming. You're building the system that breaks them all.</p>
        <p><em>This is a live Codespace interface.</em></p>
      </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
