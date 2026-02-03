from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
import os

# Инициализация объектов
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    # Настройки приложения
    app.config.from_object("app.config.Config")

    # Указываем разрешённые источники для CORS
    frontend_url = os.getenv("FRONTEND_URL", "*")  # Используем переменную окружения FRONTEND_URL
    CORS(app, resources={r"/*": {"origins": frontend_url}})

    # Добавляем базовый маршрут для главной страницы
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to the backend API!"})

    # Инициализация базы данных, JWT и миграций
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Подключение Blueprints (маршруты)
    from .routes.auth import auth_bp
    from .routes.me import me_bp
    from .routes.activities import activities_bp
    from .routes.achievements import achievements_bp
    from .routes.dev import dev_bp
    from .routes.admin import admin_bp
    from .routes.dev_notifications import dev_notifications_bp
    from .routes.health import health_bp

    # Регистрируем Blueprints с префиксами
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(me_bp, url_prefix="/me")
    app.register_blueprint(activities_bp, url_prefix="/activities")
    app.register_blueprint(achievements_bp, url_prefix="/achievements")
    app.register_blueprint(dev_bp, url_prefix="/dev")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(dev_notifications_bp, url_prefix="/dev")
    app.register_blueprint(health_bp, url_prefix="/health")

    # Импорт моделей для работы с базой данных
    from app.models.user import User
    from app.models.activity import Activity
    from app.models.registration import ActivityRegistration
    from app.models.achievement import Achievement
    from app.models.user_achievement import UserAchievement

    # Проверяем, включен ли планировщик задач
    if os.getenv("ENABLE_SCHEDULER", "0") == "1":
        from app.scheduler import start_scheduler
        start_scheduler(app)

    return app
