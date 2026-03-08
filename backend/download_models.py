import os
import gdown
from huggingface_hub import hf_hub_download

# --- Assets ---
MODEL_ID = "10GWSogJNKlPlTeWtJkDq_zc4roB1Vmnu" # Keras Face Emotion
CSV_ID   = "1bJ8C1BY0rvPNKuWcBgqiUtiSzHziZokH" # Medication CSV

# Llama-3-8B-Instruct GGUF (Quantized for CPU/RAM efficiency)
LLAMA_REPO = "MaziyarPanahi/Llama-3-8B-Instruct-v0.1-GGUF"
LLAMA_FILE = "Llama-3-8B-Instruct-v0.1.Q4_K_M.gguf"

# Destinations
ML_ASSETS = "app/ml_assets"
FACE_MODEL_PATH = os.path.join(ML_ASSETS, "emotion_model_trained.h5")
MEDS_CSV_PATH = os.path.join(ML_ASSETS, "MEDICATION.csv")
LLAMA_GGUF_PATH = os.path.join(ML_ASSETS, "llama-3-8b-instruct.Q4_K_M.gguf")

# HF Transformers (Downloaded via snapshot_download for full directory)
CRISIS_MODEL_REPO = "cross-encoder/nli-MiniLM2-L6-H768"
DISTILBERT_MODEL_REPO = "bhadresh-savani/distilbert-base-uncased-emotion"

CRISIS_MODEL_PATH = os.path.join(ML_ASSETS, "crisis_model")
DISTILBERT_MODEL_PATH = os.path.join(ML_ASSETS, "distilbert_model")

def download_drive_file(file_id, output_path):
    if not os.path.exists(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        url = f'https://drive.google.com/uc?id={file_id}'
        print(f"⬇️ Downloading Drive file to {output_path}...")
        gdown.download(url, output_path, quiet=False)
    else:
        print(f"✅ Found {output_path}, skipping.")

def download_hf_model(repo_id, filename, output_path):
    if not os.path.exists(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"⬇️ Downloading HF model: {filename} from {repo_id}...")
        hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=os.path.dirname(output_path),
            local_dir_use_symlinks=False
        )
        # Rename to match our config expectation
        downloaded_path = os.path.join(os.path.dirname(output_path), filename)
        if downloaded_path != output_path:
            os.rename(downloaded_path, output_path)
    else:
        print(f"✅ Found {output_path}, skipping.")

def download_hf_directory(repo_id, output_dir):
    from huggingface_hub import snapshot_download
    if not os.path.exists(output_dir) or not os.listdir(output_dir):
        print(f"⬇️ Downloading HF repo: {repo_id} to {output_dir}...")
        snapshot_download(
            repo_id=repo_id,
            local_dir=output_dir,
            local_dir_use_symlinks=False,
            ignore_patterns=["*.msgpack", "*.h5", "*.ot", "rust_model.ot"] # save space, only PyTorch/Safetensors needed
        )
    else:
        print(f"✅ Found {output_dir}, skipping.")

if __name__ == "__main__":
    print("🚀 Starting Production Model Sync...")
    
    # 1. Drive Files
    download_drive_file(MODEL_ID, FACE_MODEL_PATH)
    download_drive_file(CSV_ID, MEDS_CSV_PATH)
    
    # 2. HF Models (Llama 3)
    try:
        download_hf_model(LLAMA_REPO, LLAMA_FILE, LLAMA_GGUF_PATH)
    except Exception as e:
        print(f"⚠️ HF LLaMA Download failed (expected on local dev if no internet): {e}")

    # 3. HF Transformers Pipeline Models
    try:
        download_hf_directory(CRISIS_MODEL_REPO, CRISIS_MODEL_PATH)
        download_hf_directory(DISTILBERT_MODEL_REPO, DISTILBERT_MODEL_PATH)
    except Exception as e:
        print(f"⚠️ HF Transformers Download failed: {e}")
        
    print("✅ All models synchronized!")