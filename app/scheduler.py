from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app

from app.services.notifications import notify_24h

scheduler = BackgroundScheduler()

def start_scheduler(app):
    """
    Важно: в debug Flask перезапускается, поэтому стартуем только если включено.
    """
    with app.app_context():
        bot_token = current_app.config.get("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            print("Scheduler: TELEGRAM_BOT_TOKEN is not set. Notifications disabled.")
            return

        def job():
            with app.app_context():
                res = notify_24h(bot_token)
                print("Scheduler notify_24h:", res)

        # раз в 10 минут
        scheduler.add_job(job, "interval", minutes=10, id="notify_24h", replace_existing=True)
        scheduler.start()
        print("Scheduler started (notify_24h every 10 min)")
