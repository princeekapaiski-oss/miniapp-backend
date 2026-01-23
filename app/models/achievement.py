from app import db
from datetime import datetime

class Achievement(db.Model):
    __tablename__ = "achievement"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(512), nullable=True)
    experience = db.Column(db.Integer, nullable=False, default=0)
    is_automatic = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
