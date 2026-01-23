from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user_achievement import UserAchievement
from app.models.achievement import Achievement

achievements_bp = Blueprint("achievements", __name__)

@achievements_bp.route("/my", methods=["GET"])
@jwt_required()
def my_achievements():
    user_id = int(get_jwt_identity())

    rows = (
        UserAchievement.query
        .filter_by(user_id=user_id)
        .order_by(UserAchievement.created_at.desc())
        .all()
    )

    result = []
    for ua in rows:
        ach = Achievement.query.get(ua.achievement_id)
        if not ach:
            continue

        result.append({
            "id": ach.id,
            "title": ach.title,
            "description": ach.description,
            "experience": ach.experience,
            "imageUrl": ach.image_url,
            "isAutomatic": ach.is_automatic,
            "receivedAt": ua.created_at.isoformat()
        })

    return jsonify(result)
