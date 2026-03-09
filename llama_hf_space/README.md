# Dedicated Llama 3 API Space

This folder contains all the files needed to create a dedicated Hugging Face Space for your Llama 3 model.

### 🚀 How to Deploy this to Hugging Face:

1. Go to Hugging Face and click **New Space**.
2. Name it something like: `PsyPredict-Llama-API`
3. Choose **Docker** as the Space SDK, then select **Blank**.
4. Choose the Hardware. *(Note: Llama 8B requires at least 16GB RAM. If you are using the Free Tier and it still crashes, edit `main.py` and change the `MODEL_URL` to a smaller quantized model like `Q2_K_M` or a 3B parameter model like Phi-3)*.
5. Create the Space.
6. Upload the following files from this folder directly to your new Space:
   - `main.py`
   - `Dockerfile`

### 🔗 How to Connect PsyPredict to this new Space:

Because we wrote `main.py` to perfectly mimic Ollama's API (`/api/generate`), you do **not** need to change any Python code in your PsyPredict backend!

Simply go to your original **PsyPredict Backend** Hugging Face Space, click **Settings**, go to **Variables and secrets**, and update/add these variables:

- `OLLAMA_BASE_URL`: `https://your-username-psypredict-llama-api.hf.space`
- `USE_EMBEDDED_LLM`: `False` (very important!)

Restart your PsyPredict Space, and it will now forward all chat requests seamlessly to this dedicated Llama server! You can reuse that exact same `OLLAMA_BASE_URL` in your next project too!
