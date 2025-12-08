import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (API Keys)
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("⚠️ Error: GOOGLE_API_KEY not found. Check your .env file!")
else:
    print("✅ Key loaded securely.")

class LLMEngine:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model = None
        self._setup_model()

    def _setup_model(self):
        """Configures the Gemini Model."""
        if not self.api_key:
            print("⚠️ WARNING: GOOGLE_API_KEY not found in .env file. Chat will function in 'Mock Mode'.")
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ LLM Engine: Gemini 2.0 Flash Connected")
        except Exception as e:
            print(f"❌ LLM Engine Error: {e}")

    def generate_response(self, user_text, emotion_context=None, history=[]):
        """
        Generates a therapeutic response.
        
        Args:
            user_text (str): The user's message.
            emotion_context (str): The emotion detected by the camera (e.g., 'sad', 'happy').
            history (list): Previous chat messages for context.
        """
        
        # 1. Fallback if no API Key (Mock Mode)
        if not self.model:
            return "I am currently running in offline mode. Please set your GOOGLE_API_KEY to chat with me fully! (Detected emotion: " + str(emotion_context) + ")"

        # 2. Construct the "System Prompt" (The Persona)
        system_instruction = (
            "You are PsyPredict, a compassionate, culturally grounded mental health assistant. "
            "Your goal is to provide supportive, non-prescriptive guidance combining modern psychology "
            "and wisdom from the Bhagavad Gita.\n\n"
            "GUIDELINES:\n"
            "1. Be empathetic and warm.\n"
            "2. If the user seems stressed or sad, offer a short, relevant quote or metaphor from the Bhagavad Gita.\n"
            "3. IMPORTANT: You are NOT a doctor. Do not diagnose or prescribe medication. If the user mentions self-harm, immediately provide emergency resources.\n"
            "4. Keep responses concise (under 100 words) unless asked for a story."
        )

        # 3. Add "Fusion" Context (Visual + Text)
        fusion_context = ""
        if emotion_context and emotion_context != "neutral":
            fusion_context = f"[SYSTEM NOTE: The user's facial expression currently shows '{emotion_context}'. Use this to adjust your tone.]\n"

        # 4. Build the Full Prompt
        # We combine history into a text block for simplicity (stateless request)
        conversation_log = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]]) # Keep last 5 turns
        
        final_prompt = f"{system_instruction}\n\nCONVERSATION HISTORY:\n{conversation_log}\n\n{fusion_context}User: {user_text}\nAssistant:"

        try:
            # 5. Call Gemini
            response = self.model.generate_content(final_prompt)
            return response.text.strip()
        except Exception as e:
            return f"I'm having trouble connecting to my thought engine right now. Error: {str(e)}"

# Singleton Instance
llm_therapist = LLMEngine()