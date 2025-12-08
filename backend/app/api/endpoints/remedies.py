from flask import Blueprint, request, jsonify
from app.services.remedy_engine import remedy_engine

remedies_bp = Blueprint('remedies', __name__)

@remedies_bp.route('/get_advice', methods=['GET'])
def get_advice():
    """
    Query Param: ?condition=Depression
    Returns: JSON with meds, treatments, and Gita story.
    """
    condition = request.args.get('condition')
    
    if not condition:
        return jsonify({"error": "Missing 'condition' parameter"}), 400

    result = remedy_engine.get_remedy(condition)

    if result:
        return jsonify(result)
    else:
        return jsonify({"message": "No specific remedy found for this condition."}), 404