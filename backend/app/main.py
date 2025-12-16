import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables (API Keys) from .env
load_dotenv()

# Import the 3 Endpoints
from app.api.endpoints.facial import facial_bp
from app.api.endpoints.remedies import remedies_bp
from app.api.endpoints.therapist import therapist_bp

def create_app():
    app = Flask(__name__)
    
    # Enable CORS so Frontend (port 5173) can talk to Backend (port 5000)
    CORS(app)

    # Register the Blueprints (The 3 features)
    app.register_blueprint(facial_bp, url_prefix='/api')
    app.register_blueprint(remedies_bp, url_prefix='/api')
    app.register_blueprint(therapist_bp, url_prefix='/api')

    return app

if __name__ == "__main__":
    app = create_app()

    print("🚀 PsyPredict Backend running on port 7860")
    print("   - /api/predict/emotion [POST]")
    print("   - /api/get_advice?condition=... [GET]")
    print("   - /api/chat [POST]")

    app.run(host="0.0.0.0", port=7860, debug=False)
