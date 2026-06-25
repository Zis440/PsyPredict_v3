import os
import glob
import shutil

source_dir = r"C:\Users\Saphalya\.gemini\antigravity-ide\brain\fb975322-313e-4327-866f-b7bc415ec849"
dest_dir = r"d:\PsyPredict\frontend\public\images\psychology"

os.makedirs(dest_dir, exist_ok=True)

images = glob.glob(os.path.join(source_dir, "*.png"))
for img in images:
    filename = os.path.basename(img)
    dest_path = os.path.join(dest_dir, filename)
    shutil.copy2(img, dest_path)
    print(f"Copied {filename} to {dest_dir}")

print("Done.")
