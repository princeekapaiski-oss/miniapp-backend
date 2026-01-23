from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.award_achievement import award_achievement

dev_bp = Blueprint("dev", __name__)

@dev_bp.route("/award-achievement", methods=["POST"])
@jwt_required()
def dev_award_achievement():
    """
    DEV ONLY:
    Выдать достижение текущему пользователю.
    Body: { "achievementId": 1 }
    """
    user_id = int(get_jwt_identity())
    achievement_id = request.json.get("achievementId")

    if not achievement_id:
        return jsonify({"error": "achievementId is required"}), 400

    ok = award_achievement(user_id, int(achievement_id))
    return jsonify({"ok": ok})
