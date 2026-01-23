from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

from app import db
from app.models.activity import Activity
from app.models.registration import ActivityRegistration
from app.models.user import User
from app.services.telegram_bot import send_message

def notify_24h(bot_token: str) -> dict:
    """
    Ищем занятия, которые начнутся примерно через 24 часа,
    берём REGISTERED у кого notified_24h_at is NULL,
    отправляем сообщение, отмечаем notified_24h_at.
    """
    now = datetime.utcnow()

    # окно вокруг 24 часов (± 30 минут) — чтобы job раз в 10 минут не промахнулся
    window_from = now + timedelta(hours=23, minutes=30)
    window_to   = now + timedelta(hours=24, minutes=30)

    # registrations + activity + user
    regs = (
        ActivityRegistration.query
        .filter(ActivityRegistration.status == "REGISTERED")
        .filter(ActivityRegistration.notified_24h_at.is_(None))
        .all()
    )

    sent = 0
    skipped = 0
    failed = 0

    for r in regs:
        activity = Activity.query.get(r.activity_id)
        if not activity:
            skipped += 1
            continue

        # проверяем попадание в окно
        if not (window_from <= activity.start_at <= window_to):
            continue

        user = User.query.get(r.user_id)
        if not user or not user.telegram_id:
            skipped += 1
            continue

        text = (
            f"Напоминание: завтра занятие «{activity.title}»\n"
            f"Начало: {activity.start_at.isoformat(timespec='minutes')} (UTC)\n"
            f"Если планы изменились — отмени запись в MiniApp."
        )

        ok = send_message(bot_token, int(user.telegram_id), text)
        if ok:
            r.notified_24h_at = now
            db.session.commit()
            sent += 1
        else:
            failed += 1

    return {"sent": sent, "skipped": skipped, "failed": failed}
