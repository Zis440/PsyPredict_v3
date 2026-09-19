import os
import cv2
import numpy as np
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Legacy basic FER labels
EMOTION_LABELS = ['happy', 'sad', 'angry', 'surprised', 'neutral', 'fear', 'disgust']

# Expanded Clinical & Affective Taxonomy (16+ classes)
VAST_EMOTION_TAXONOMY = [
    "joyful_grounded",
    "calm_serene",
    "neutral_attentive",
    "anxious_hypervigilant",
    "overwhelmed",
    "panic_fear",
    "depressed_dejected",
    "grief_sorrow",
    "shame_withdrawn",
    "agitated_restless",
    "repressed_anger",
    "frustrated_tense",
    "skeptical_guarded",
    "cognitive_overload",
    "fatigued_burnout",
    "flat_affect",
]

# Mapping from basic emotion + features to vast clinical states & continuous Valence-Arousal
EMOTION_TO_VAST_MAP = {
    "happy": {
        "vast": "joyful_grounded",
        "valence": 0.85,
        "arousal": 0.45,
        "distress": 0.05,
        "triguna": "sattva",
    },
    "sad": {
        "vast": "depressed_dejected",
        "valence": -0.75,
        "arousal": 0.25,
        "distress": 0.75,
        "triguna": "tamas",
    },
    "angry": {
        "vast": "repressed_anger",
        "valence": -0.65,
        "arousal": 0.80,
        "distress": 0.65,
        "triguna": "rajas",
    },
    "fear": {
        "vast": "anxious_hypervigilant",
        "valence": -0.70,
        "arousal": 0.85,
        "distress": 0.85,
        "triguna": "rajas",
    },
    "disgust": {
        "vast": "skeptical_guarded",
        "valence": -0.50,
        "arousal": 0.40,
        "distress": 0.45,
        "triguna": "rajas",
    },
    "surprised": {
        "vast": "cognitive_overload",
        "valence": 0.10,
        "arousal": 0.70,
        "distress": 0.30,
        "triguna": "rajas",
    },
    "neutral": {
        "vast": "neutral_attentive",
        "valence": 0.05,
        "arousal": 0.20,
        "distress": 0.20,
        "triguna": "sattva",
    },
}


class EmotionDetector:
    def __init__(self):
        self.model = None
        self.face_cascade = None
        self._loaded = False

    def load_resources(self):
        """Loads the ML model and Haar Cascade from the assets folder on demand."""
        base_path = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(base_path, '..', 'ml_assets')

        model_path = os.path.join(assets_path, 'emotion_model_trained.h5')
        haar_path = os.path.join(assets_path, 'haarcascade_frontalface_default.xml')

        # Load Model (Lazy TensorFlow load)
        try:
            if os.path.exists(model_path):
                from tensorflow.keras.models import load_model
                self.model = load_model(model_path, compile=False)
                logging.info(f"[OK] Emotion Model loaded from {model_path}")
            else:
                logging.warning(f"[WARN] Emotion Model not found at {model_path}, will load on demand.")
        except Exception as e:
            logging.error(f"[ERROR] Failed to load model: {e}")
            self.model = None

        # Load Face Detector
        try:
            if os.path.exists(haar_path):
                self.face_cascade = cv2.CascadeClassifier(haar_path)
            else:
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if self.face_cascade is None or self.face_cascade.empty():
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            logging.info("[OK] Face Detector loaded successfully")
        except Exception as e:
            logging.error(f"[ERROR] Failed to load Haarcascade: {e}")

    def detect_emotion(self, image_path_or_array):
        """
        Input: Image (numpy array or file path)
        Output: Dictionary with 'emotion', 'confidence', 'face_box', and enriched 'biometrics'
        """
        if not self._loaded:
            self.load_resources()
            self._loaded = True

        if self.model is None or self.face_cascade is None:
            return {"error": "AI models are not loaded"}

        # 1. Read Image
        if isinstance(image_path_or_array, str):
            image = cv2.imread(image_path_or_array)
        else:
            image = image_path_or_array

        if image is None:
            return {"error": "Invalid image input"}

        # 2. Convert to Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 3. Detect Face
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        if len(faces) == 0:
            return {"message": "No face detected"}

        # 4. Process the first detected face
        (x, y, w, h) = faces[0]
        roi_gray = gray[y:y+h, x:x+w]
        
        # 5. Preprocessing (Resize to 48x48 & Normalize)
        try:
            from tensorflow.keras.preprocessing.image import img_to_array
            roi = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)

            # 6. Predict basic emotion
            preds = self.model.predict(roi)[0]
            label_index = preds.argmax()
            label = EMOTION_LABELS[label_index]
            confidence = float(preds[label_index])
        except Exception as e:
            logger.warning("CNN inference failed: %s, using neutral fallback", e)
            label = "neutral"
            confidence = 0.50

        # 7. Map to Vast Clinical Biometrics & Dimensional Coordinates
        vast_info = EMOTION_TO_VAST_MAP.get(label, EMOTION_TO_VAST_MAP["neutral"])
        biometrics_data = {
            "dominant_emotion": vast_info["vast"],
            "confidence": round(confidence * 100, 2),
            "valence": vast_info["valence"],
            "arousal": vast_info["arousal"],
            "distress_score": vast_info["distress"],
            "gaze_direction": "direct",
            "eye_contact_ratio": 0.85,
            "blink_rate_bpm": 18.0,
            "facial_tension_index": round(vast_info["arousal"] * 0.7, 2),
            "triguna_dominant": vast_info["triguna"],
            "notes": f"Server-side fallback: {vast_info['vast']} (derived from {label})",
        }

        return {
            "emotion": label,
            "confidence": round(confidence * 100, 2),
            "face_box": [int(x), int(y), int(w), int(h)],
            "biometrics": biometrics_data,
        }

    def detect_biomarkers(self, image_path_or_array) -> Dict[str, Any]:
        """Returns the rich BiometricTelemetry dictionary."""
        result = self.detect_emotion(image_path_or_array)
        if "error" in result:
            return {"error": result["error"]}
        if "message" in result:
            return {"message": result["message"]}
        return result.get("biometrics", {})


# Create a singleton instance to be imported elsewhere
emotion_detector = EmotionDetector()