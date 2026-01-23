from app import db
from datetime import datetime
from sqlalchemy import UniqueConstraint

class ActivityRegistration(db.Model):

    __tablename__ = "activity_registration"
    from datetime import datetime

    notified_24h_at = db.Column(db.DateTime, nullable=True)

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("activity.id"), nullable=False)

    # REGISTERED / CANCELLED / VISITED / MISSED
    status = db.Column(db.String(20), nullable=False, default="REGISTERED")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        # запретить дублирующую активную запись на одно занятие
        UniqueConstraint("user_id", "activity_id", name="uq_user_activity"),
    )
