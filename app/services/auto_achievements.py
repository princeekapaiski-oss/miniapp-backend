from sqlalchemy import func

from app import db
from app.models.registration import ActivityRegistration
from app.models.achievement import Achievement
from app.models.user_achievement import UserAchievement
from app.services.award_achievement import award_achievement

def _visited_count(user_id: int) -> int:
    return (
        db.session.query(func.count(ActivityRegistration.id))
        .filter(
            ActivityRegistration.user_id == user_id,
            ActivityRegistration.status == "VISITED"
        )
        .scalar()
        or 0
    )

def _has_achievement(user_id: int, achievement_id: int) -> bool:
    return (
        UserAchievement.query
        .filter_by(user_id=user_id, achievement_id=achievement_id)
        .first()
        is not None
    )

def check_automatic_achievements(user_id: int) -> list[int]:
    """
    Проверяет условия и выдаёт недостающие автодостижения.
    Возвращает список achievement_id, которые были выданы.
    """

    awarded: list[int] = []
    visited = _visited_count(user_id)

    # 1) Первое занятие
    if visited >= 1:
        ach = Achievement.query.filter_by(title="Первое занятие", is_automatic=True).first()
        if ach and not _has_achievement(user_id, ach.id):
            if award_achievement(user_id, ach.id):
                awarded.append(ach.id)

    # 2) 10 занятий
    if visited >= 10:
        ach = Achievement.query.filter_by(title="10 занятий", is_automatic=True).first()
        if ach and not _has_achievement(user_id, ach.id):
            if award_achievement(user_id, ach.id):
                awarded.append(ach.id)

    return awarded
