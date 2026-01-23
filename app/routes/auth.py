from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
import json

from app import db
from app.models.user import User
from app.services.telegram_auth import verify_init_data

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/telegram", methods=["POST"])
def telegram_auth():
    init_data = request.json.get("initData")
    if not init_data:
        return jsonify({"error": "initData is required"}), 400

    data = verify_init_data(
        init_data,
        current_app.config["TELEGRAM_BOT_TOKEN"]
    )

    if not data:
        return jsonify({"error": "Invalid Telegram data"}), 401

    user_data = json.loads(data["user"])
    telegram_id = user_data["id"]

    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
        )
        db.session.add(user)
        db.session.commit()

    token = create_access_token(identity=str(user.id))


    return jsonify({
        "accessToken": token,
        "user": {
            "id": user.id,
            "telegramId": user.telegram_id,
            "username": user.username,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "experience": user.experience,
            "level": user.level
        }
    })

@auth_bp.route("/dev", methods=["POST"])
def dev_auth():
    """
    DEV ONLY: быстро получить JWT без Telegram initData.
    В проде удалить/закрыть.
    """
    user = User.query.filter_by(telegram_id=999999999).first()
    if not user:
        user = User(
            telegram_id=999999999,
            username="dev_user",
            first_name="Dev",
            last_name="User",
        )
        db.session.add(user)
        db.session.commit()

    token = create_access_token(identity=str(user.id))


    return jsonify({
        "accessToken": token,
        "user": {
            "id": user.id,
            "telegramId": user.telegram_id,
            "username": user.username,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "experience": user.experience,
            "level": user.level
        }
    })
