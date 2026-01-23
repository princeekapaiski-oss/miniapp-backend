from app import create_app, db
from app.models.achievement import Achievement

def seed():
    app = create_app()
    with app.app_context():
        count = Achievement.query.count()
        if count > 0:
            print(f"Achievements already exist: {count}. Seed skipped.")
            return

        items = [
            Achievement(
                title="Первое занятие",
                description="Посетил первое занятие",
                experience=50,
                image_url="",
                is_automatic=True
            ),
            Achievement(
                title="10 занятий",
                description="Посетил 10 занятий",
                experience=100,
                image_url="",
                is_automatic=True
            ),
            Achievement(
                title="Особое достижение",
                description="Выдано админом вручную",
                experience=200,
                image_url="",
                is_automatic=False
            ),
        ]

        db.session.add_all(items)
        db.session.commit()
        print(f"Seeded achievements: {len(items)}")

if __name__ == "__main__":
    seed()
