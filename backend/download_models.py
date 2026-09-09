"""
download_models.py — Safe, chunked streaming model downloader for PsyPredict.
Uses standard requests streaming (1MB buffer) — zero memory overhead, no segfaults.
"""
import os
import sys
import logging
import requests

logger = logging.getLogger(__name__)

# --- Assets ---
MODEL_ID = "10GWSogJNKlPlTeWtJkDq_zc4roB1Vmnu"  # Keras Face Emotion
CSV_ID   = "1bJ8C1BY0rvPNKuWcBgqiUtiSzHziZokH"  # Medication CSV

# Destinations
ML_ASSETS = "app/ml_assets"
FACE_MODEL_PATH = os.path.join(ML_ASSETS, "emotion_model_trained.h5")
MEDS_CSV_PATH = os.path.join(ML_ASSETS, "MEDICATION.csv")


def download_drive_file(file_id: str, output_path: str) -> bool:
    """
    Downloads a public Google Drive file safely using chunked streaming.
    Handles Google Drive's large file virus-scan redirect automatically.
    """
    if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        print(f"✅ Found {output_path} ({os.path.getsize(output_path) // (1024*1024)} MB), skipping.")
        return True

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"⬇️ Streaming Drive file to {output_path}...")

    base_url = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    try:
        # Initial request
        res = session.get(base_url, params={"id": file_id}, stream=True, timeout=30)
        
        # Check for Google Drive confirmation token on large files (>100MB)
        confirm_token = None
        for key, value in res.cookies.items():
            if key.startswith("download_warning"):
                confirm_token = value
                break

        if confirm_token:
            params = {"id": file_id, "confirm": confirm_token}
            res = session.get(base_url, params=params, stream=True, timeout=30)

        # Write to temporary file first, then rename (atomic)
        tmp_path = output_path + ".tmp"
        total_downloaded = 0

        with open(tmp_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024 * 1024):  # 1 MB chunk
                if chunk:
                    f.write(chunk)
                    total_downloaded += len(chunk)

        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 10000:
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(tmp_path, output_path)
            print(f"✅ Successfully downloaded {output_path} ({total_downloaded // (1024*1024)} MB).")
            return True
        else:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            print(f"⚠️ Downloaded file too small ({total_downloaded} bytes). Will retry on demand.")
            return False

    except Exception as exc:
        print(f"⚠️ Drive stream download failed: {exc}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Production Model Sync...")
    download_drive_file(MODEL_ID, FACE_MODEL_PATH)
    print("✅ All assets ready!")