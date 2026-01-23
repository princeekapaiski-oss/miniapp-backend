def calc_level(experience: int) -> int:
    """
    Простая формула уровней на старте:
    level 1: 0+
    level 2: 100+
    level 3: 250+
    level 4: 450+
    ...
    Можем потом заменить на любую таблицу.
    """
    if experience < 0:
        experience = 0

    thresholds = [0, 100, 250, 450, 700, 1000, 1350, 1750, 2200, 2700]
    level = 1
    for i, t in enumerate(thresholds, start=1):
        if experience >= t:
            level = i
    return level
