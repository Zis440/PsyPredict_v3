from flask import Blueprint, request, jsonify
from app.services.llm_engine import llm_therapist

therapist_bp = Blueprint('therapist', __name__)

@therapist_bp.route('/chat', methods=['POST'])
def chat():
    """
    Expects JSON:
    {
        "message": "I feel anxious",
        "emotion": "fear",
        "history": [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"}
        ]
    }
    """
    data = request.get_json()
    
    user_message = data.get('message', '')
    current_emotion = data.get('emotion', None)
    history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Generate response
    response_text = llm_therapist.generate_response(user_message, current_emotion, history)

    return jsonify({
        "response": response_text
    })