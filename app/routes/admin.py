from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import func
from app.models.achievement import Achievement
from app.services.award_achievement import award_achievement


from app import db
from app.models.activity import Activity
from app.models.user import User
from app.models.registration import ActivityRegistration
from app.services.auto_achievements import check_automatic_achievements

admin_bp = Blueprint("admin", __name__)

def _require_admin():
    api_key = request.headers.get("X-Admin-Key", "")
    if not current_app.config.get("ADMIN_API_KEY"):
        return False
    return api_key == current_app.config["ADMIN_API_KEY"]

@admin_bp.before_request
def guard():
    if not _require_admin():
        return jsonify({"error": "Unauthorized"}), 401

@admin_bp.route("/activities", methods=["GET"])
def admin_list_activities():
    activities = Activity.query.order_by(Activity.start_at.asc()).all()
    return jsonify([{
        "id": a.id,
        "title": a.title,
        "startAt": a.start_at.isoformat(),
        "endAt": a.end_at.isoformat(),
        "maxParticipants": a.max_participants
    } for a in activities])

@admin_bp.route("/activities/<int:activity_id>/registrations", methods=["GET"])
def admin_activity_registrations(activity_id: int):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    regs = ActivityRegistration.query.filter_by(activity_id=activity_id).all()

    result = []
    for r in regs:
        u = User.query.get(r.user_id)
        result.append({
            "registrationId": r.id,
            "userId": r.user_id,
            "username": u.username if u else None,
            "firstName": u.first_name if u else None,
            "lastName": u.last_name if u else None,
            "status": r.status,
            "createdAt": r.created_at.isoformat() if r.created_at else None
        })

    return jsonify({
        "activity": {
            "id": activity.id,
            "title": activity.title,
            "startAt": activity.start_at.isoformat(),
        },
        "registrations": result
    })

@admin_bp.route("/activities/<int:activity_id>/attendance", methods=["POST"])
def admin_mark_attendance(activity_id: int):
    """
    Body:
    {
      "userId": 123,
      "status": "VISITED" | "MISSED" | "REGISTERED" | "CANCELLED"
    }
    """
    body = request.get_json(silent=True) or {}
    user_id = body.get("userId")
    status = body.get("status")

    if not user_id or not status:
        return jsonify({"error": "userId and status are required"}), 400

    status = str(status).upper()
    if status not in {"REGISTERED", "CANCELLED", "VISITED", "MISSED"}:
        return jsonify({"error": "Invalid status"}), 400

    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    reg = ActivityRegistration.query.filter_by(
        user_id=int(user_id),
        activity_id=activity_id
    ).first()

    if not reg:
        # если записи не было — создаём (это удобно для админа/бота)
        reg = ActivityRegistration(user_id=int(user_id), activity_id=activity_id, status=status)
        db.session.add(reg)
    else:
        reg.status = status

    db.session.commit()

    awarded_ids = []
    # автодостижения только когда отмечаем VISITED
    if status == "VISITED":
        awarded_ids = check_automatic_achievements(int(user_id))

    return jsonify({
        "ok": True,
        "activityId": activity_id,
        "userId": int(user_id),
        "status": status,
        "awardedAchievementIds": awarded_ids
    })
from datetime import datetime

def _parse_iso(dt_str: str) -> datetime:
    # ожидаем ISO формат "2026-01-31T18:00:00"
    return datetime.fromisoformat(dt_str)

@admin_bp.route("/activities", methods=["POST"])
def admin_create_activity():
    """
    Body:
    {
      "title": "...",
      "description": "...",
      "startAt": "2026-02-01T18:00:00",
      "endAt": "2026-02-01T20:00:00",
      "maxParticipants": 10
    }
    """
    body = request.get_json(silent=True) or {}
    title = body.get("title")
    start_at = body.get("startAt")
    end_at = body.get("endAt")

    if not title or not start_at or not end_at:
        return jsonify({"error": "title, startAt, endAt are required"}), 400

    a = Activity(
        title=str(title),
        description=body.get("description"),
        start_at=_parse_iso(str(start_at)),
        end_at=_parse_iso(str(end_at)),
        max_participants=body.get("maxParticipants"),
    )
    db.session.add(a)
    db.session.commit()
    return jsonify({"ok": True, "id": a.id})

@admin_bp.route("/activities/<int:activity_id>", methods=["PATCH"])
def admin_update_activity(activity_id: int):
    body = request.get_json(silent=True) or {}
    a = Activity.query.get(activity_id)
    if not a:
        return jsonify({"error": "Activity not found"}), 404

    if "title" in body: a.title = body["title"]
    if "description" in body: a.description = body["description"]
    if "startAt" in body: a.start_at = _parse_iso(str(body["startAt"]))
    if "endAt" in body: a.end_at = _parse_iso(str(body["endAt"]))
    if "maxParticipants" in body: a.max_participants = body["maxParticipants"]

    db.session.commit()
    return jsonify({"ok": True})

@admin_bp.route("/activities/<int:activity_id>", methods=["DELETE"])
def admin_delete_activity(activity_id: int):
    a = Activity.query.get(activity_id)
    if not a:
        return jsonify({"error": "Activity not found"}), 404
    db.session.delete(a)
    db.session.commit()
    return jsonify({"ok": True})

@admin_bp.route("/achievements", methods=["GET"])
def admin_list_achievements():
    items = Achievement.query.order_by(Achievement.id.asc()).all()
    return jsonify([{
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "experience": a.experience,
        "isAutomatic": a.is_automatic
    } for a in items])

@admin_bp.route("/users/<int:user_id>/award-achievement", methods=["POST"])
def admin_award_achievement(user_id: int):
    body = request.get_json(silent=True) or {}
    achievement_id = body.get("achievementId")
    if not achievement_id:
        return jsonify({"error": "achievementId is required"}), 400

    ok = award_achievement(int(user_id), int(achievement_id))
    return jsonify({"ok": ok})

