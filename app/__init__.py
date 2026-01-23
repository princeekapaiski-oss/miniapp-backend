from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from .routes.auth import auth_bp
    from .routes.me import me_bp
    from .routes.activities import activities_bp
    from .routes.achievements import achievements_bp
    from .routes.dev import dev_bp
    from .routes.admin import admin_bp
    from .routes.dev_notifications import dev_notifications_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(me_bp, url_prefix="/me")
    app.register_blueprint(activities_bp, url_prefix="/activities")
    app.register_blueprint(achievements_bp, url_prefix="/achievements")
    app.register_blueprint(dev_bp, url_prefix="/dev")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(dev_notifications_bp, url_prefix="/dev")

    from app.models.user import User
    from app.models.activity import Activity
    from app.models.registration import ActivityRegistration
    from app.models.achievement import Achievement
    from app.models.user_achievement import UserAchievement

    import os
    if os.getenv("ENABLE_SCHEDULER", "0") == "1":
        from app.scheduler import start_scheduler
        start_scheduler(app)
    return app
