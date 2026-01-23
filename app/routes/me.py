from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app import db
from app.models.user import User
from app.models.registration import ActivityRegistration
from app.models.user_achievement import UserAchievement
from app.models.achievement import Achievement

me_bp = Blueprint("me", __name__)

@me_bp.route("", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    visited = (
        db.session.query(func.count(ActivityRegistration.id))
        .filter(
            ActivityRegistration.user_id == user_id,
            ActivityRegistration.status == "VISITED"
        )
        .scalar()
        or 0
    )

    missed = (
        db.session.query(func.count(ActivityRegistration.id))
        .filter(
            ActivityRegistration.user_id == user_id,
            ActivityRegistration.status == "MISSED"
        )
        .scalar()
        or 0
    )

    # achievements summary (как в примере ТЗ)
    uas = (
        UserAchievement.query
        .filter_by(user_id=user_id)
        .order_by(UserAchievement.created_at.desc())
        .all()
    )

    achievements = []
    for ua in uas:
        ach = Achievement.query.get(ua.achievement_id)
        if not ach:
            continue
        achievements.append({
            "id": ach.id,
            "title": ach.title,
            "imageUrl": ach.image_url
        })

    return jsonify({
        "id": user.id,
        "telegramId": user.telegram_id,
        "username": user.username,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "avatarUrl": user.avatar_url,
        "experience": user.experience,
        "level": user.level,
        "achievements": achievements,
        "stats": {
            "visited": visited,
            "missed": missed
        }
    })
