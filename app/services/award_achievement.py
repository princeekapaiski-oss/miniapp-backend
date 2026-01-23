from app import db
from app.models.user import User
from app.models.achievement import Achievement
from app.models.user_achievement import UserAchievement
from app.services.levels import calc_level

def award_achievement(user_id: int, achievement_id: int) -> bool:
    """
    Выдаёт достижение, если его ещё нет.
    Начисляет XP и пересчитывает level.
    Возвращает True если выдали, False если уже было/не найдено.
    """
    user = User.query.get(user_id)
    if not user:
        return False

    ach = Achievement.query.get(achievement_id)
    if not ach:
        return False

    existing = UserAchievement.query.filter_by(
        user_id=user_id,
        achievement_id=achievement_id
    ).first()

    if existing:
        return False

    ua = UserAchievement(user_id=user_id, achievement_id=achievement_id)
    db.session.add(ua)

    user.experience = (user.experience or 0) + (ach.experience or 0)
    user.level = calc_level(user.experience)

    db.session.commit()
    return True
