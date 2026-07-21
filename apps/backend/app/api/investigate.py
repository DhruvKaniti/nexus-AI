from flask import Blueprint, request, jsonify
from app.services.ai_service import analyze_crisis
import asyncio

bp = Blueprint('investigate', __name__)

@bp.route('/investigate', methods=['POST'])
def investigate_crisis():
    try:
        crisis = request.get_json()
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(analyze_crisis(crisis))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
