from flask import Blueprint, request, jsonify
import cv2
import numpy as np
from app.services.emotion_engine import emotion_detector

# Create a Blueprint (a group of routes)
facial_bp = Blueprint('facial', __name__)

@facial_bp.route('/predict/emotion', methods=['POST'])
def predict_emotion():
    """
    Endpoint to receive an image file and return the detected emotion.
    Expects 'form-data' with a key named 'file'.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Convert the uploaded file directly to a numpy array (OpenCV format)
        # This avoids saving the file to disk, which is faster and cleaner.
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Pass the image to our AI engine
        result = emotion_detector.detect_emotion(image)
        
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500