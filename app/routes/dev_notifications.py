from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required

from app.services.notifications import notify_24h

dev_notifications_bp = Blueprint("dev_notifications", __name__)

@dev_notifications_bp.route("/run-notify-24h", methods=["POST"])
@jwt_required()
def run_notify_24h():
    token = current_app.config.get("TELEGRAM_BOT_TOKEN")
    if not token:
        return jsonify({"error": "TELEGRAM_BOT_TOKEN is not set"}), 500
    res = notify_24h(token)
    return jsonify(res)
