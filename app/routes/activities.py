from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app import db
from app.models.activity import Activity
from app.models.registration import ActivityRegistration

activities_bp = Blueprint("activities", __name__)

def _count_registered(activity_id: int) -> int:
    return (
        db.session.query(func.count(ActivityRegistration.id))
        .filter(
            ActivityRegistration.activity_id == activity_id,
            ActivityRegistration.status == "REGISTERED"
        )
        .scalar()
        or 0
    )

@activities_bp.route("", methods=["GET"])
@jwt_required()
def list_activities():
    user_id = int(get_jwt_identity())

    activities = Activity.query.order_by(Activity.start_at.asc()).all()

    result = []
    for a in activities:
        registered_count = _count_registered(a.id)

        free_slots = None
        if a.max_participants is not None:
            free_slots = max(a.max_participants - registered_count, 0)

        my_reg = ActivityRegistration.query.filter_by(
            user_id=user_id,
            activity_id=a.id
        ).first()

        is_registered = bool(my_reg and my_reg.status == "REGISTERED")

        result.append({
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "startAt": a.start_at.isoformat(),
            "endAt": a.end_at.isoformat(),
            "maxParticipants": a.max_participants,
            "isRegistered": is_registered,
            "freeSlots": free_slots
        })

    return jsonify(result)

@activities_bp.route("/<int:activity_id>/register", methods=["POST"])
@jwt_required()
def register(activity_id: int):
    user_id = int(get_jwt_identity())

    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    reg = ActivityRegistration.query.filter_by(
        user_id=user_id,
        activity_id=activity_id
    ).first()

    if reg and reg.status == "REGISTERED":
        return jsonify({"error": "Already registered"}), 409

    if activity.max_participants is not None:
        registered_count = _count_registered(activity_id)
        if registered_count >= activity.max_participants:
            return jsonify({"error": "No free slots"}), 409

    if reg:
        reg.status = "REGISTERED"
    else:
        reg = ActivityRegistration(
            user_id=user_id,
            activity_id=activity_id,
            status="REGISTERED"
        )
        db.session.add(reg)

    db.session.commit()
    return jsonify({"ok": True})

@activities_bp.route("/<int:activity_id>/cancel", methods=["POST"])
@jwt_required()
def cancel(activity_id: int):
    user_id = int(get_jwt_identity())

    reg = ActivityRegistration.query.filter_by(
        user_id=user_id,
        activity_id=activity_id
    ).first()

    if not reg or reg.status != "REGISTERED":
        return jsonify({"error": "Not registered"}), 409

    reg.status = "CANCELLED"
    db.session.commit()
    return jsonify({"ok": True})
