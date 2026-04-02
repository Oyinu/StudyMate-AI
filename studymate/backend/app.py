from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "studymate-dev-secret")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB max upload

CORS(app, origins=[
    "https://oyinu.github.io",
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
])

# Register blueprints
from routes.auth import auth_bp
from routes.quiz import quiz_bp
from routes.upload import upload_bp
from routes.results import results_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(quiz_bp, url_prefix="/api/quiz")
app.register_blueprint(upload_bp, url_prefix="/api/upload")
app.register_blueprint(results_bp, url_prefix="/api/results")

@app.route("/api/health")
def health():
    return {"status": "ok", "message": "StudyMate AI backend is running"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)