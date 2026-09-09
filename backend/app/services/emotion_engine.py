import os
import cv2
import numpy as np
import logging
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

# Define the exact labels from your notebook
EMOTION_LABELS = ['happy', 'sad', 'angry', 'surprised', 'neutral', 'fear', 'disgust']

class EmotionDetector:
    def __init__(self):
        self.model = None
        self.face_cascade = None
        self.load_resources()

    def load_resources(self):
        """Loads the ML model and Haar Cascade from the assets folder."""
        # Dynamic path to ensure it works on any machine
        base_path = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(base_path, '..', 'ml_assets')

        model_path = os.path.join(assets_path, 'emotion_model_trained.h5')
        haar_path = os.path.join(assets_path, 'haarcascade_frontalface_default.xml')

        # Load Model
        try:
            if os.path.exists(model_path):
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
        Output: Dictionary with 'emotion' and 'confidence'
        """
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
        roi = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        # 6. Predict
        preds = self.model.predict(roi)[0]
        label_index = preds.argmax()
        label = EMOTION_LABELS[label_index]
        confidence = float(preds[label_index])

        return {
            "emotion": label,
            "confidence": round(confidence * 100, 2),
            "face_box": [int(x), int(y), int(w), int(h)]
        }

# Create a singleton instance to be imported elsewhere
emotion_detector = EmotionDetector()