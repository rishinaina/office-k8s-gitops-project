from flask import Flask
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "message": "Python Flask app is running successfully in Kubernetes",
        "environment": os.getenv("APP_ENV", "local"),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
