import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Config:
    # Секретный ключ для сессий и JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")

    # Строка подключения к базе данных
    # Для Render будет использоваться DATABASE_URL, а для локальной разработки SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "backend.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Переменные для Telegram бота и администратора
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")

    # Дополнительные настройки для работы с CORS, если нужно
    FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
