import os
import gdown # We will install this library

# 👇 PASTE YOUR GOOGLE DRIVE IDs HERE
MODEL_ID = "10GWSogJNKlPlTeWtJkDq_zc4roB1Vmnu"
CSV_ID   = "1bJ8C1BY0rvPNKuWcBgqiUtiSzHziZokH"

# Define where they should go
model_path = "app/ml_assets/emotion_model_trained.h5"
csv_path   = "app/ml_assets/MEDICATION.csv"

def download_file(file_id, output_path):
    if not os.path.exists(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        url = f'https://drive.google.com/uc?id={file_id}'
        print(f"⬇️ Downloading {output_path}...")
        gdown.download(url, output_path, quiet=False)
    else:
        print(f"✅ Found {output_path}, skipping download.")

if __name__ == "__main__":
    print("🚀 Starting Model Download...")
    download_file(MODEL_ID, model_path)
    download_file(CSV_ID, csv_path)
    print("✅ All models ready!")