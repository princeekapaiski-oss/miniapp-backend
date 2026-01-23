import os
import requests
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
BOT_ADMIN_IDS = {int(x.strip()) for x in os.getenv("BOT_ADMIN_IDS", "").split(",") if x.strip()}

def _is_admin(user_id: int) -> bool:
    return user_id in BOT_ADMIN_IDS

def _headers():
    return {"X-Admin-Key": ADMIN_API_KEY}

def _fmt_activity(a: dict) -> str:
    return (
        f"#{a['id']} — {a['title']}\n"
        f"start: {a['startAt']}\n"
        f"end:   {a['endAt']}\n"
        f"max:   {a.get('maxParticipants')}\n"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not _is_admin(uid):
        await update.message.reply_text("Нет доступа.")
        return

    await update.message.reply_text(
        "Админ-бот готов.\n\n"
        "Команды:\n"
        "/activities — список занятий\n"
        "/create <title> | <startIso> | <endIso> | <max> | <desc>\n"
        "/regs <activityId> — кто записан\n"
        "/visit <activityId> <userId> — отметить VISITED\n"
        "/miss <activityId> <userId> — отметить MISSED\n"
        "/achievements — список достижений\n"
        "/award <userId> <achievementId> — выдать достижение\n\n"
        "Пример create:\n"
        "/create 3D Печать | 2026-02-01T18:00:00 | 2026-02-01T20:00:00 | 10 | вводное занятие"
    )

async def activities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("Нет доступа.")
        return

    r = requests.get(f"{BACKEND_BASE_URL}/admin/activities", headers=_headers(), timeout=10)
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка: {r.status_code} {r.text}")
        return

    items = r.json()
    if not items:
        await update.message.reply_text("Занятий нет.")
        return

    text = "\n".join(_fmt_activity(a) for a in items)
    await update.message.reply_text(text)

async def create_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("Нет доступа.")
        return

    raw = " ".join(context.args).strip()
    if "|" not in raw:
        await update.message.reply_text("Формат: /create <title> | <startIso> | <endIso> | <max> | <desc>")
        return

    parts = [p.strip() for p in raw.split("|")]
    # title | start | end | max | desc
    title = parts[0] if len(parts) > 0 else None
    start = parts[1] if len(parts) > 1 else None
    end = parts[2] if len(parts) > 2 else None
    maxp = parts[3] if len(parts) > 3 else None
    desc = parts[4] if len(parts) > 4 else None

    if not title or not start or not end:
        await update.message.reply_text("Нужно минимум: title | startIso | endIso")
        return

    body = {
        "title": title,
        "description": desc,
        "startAt": start,
        "endAt": end,
    }
    if maxp:
        try:
            body["maxParticipants"] = int(maxp)
        except:
            pass

    r = requests.post(f"{BACKEND_BASE_URL}/admin/activities", json=body, headers=_headers(), timeout=10)
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка: {r.status_code} {r.text}")
        return

    await update.message.reply_text(f"Создано. id={r.json().get('id')}")

async def regs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("Нет доступа.")
        return

    if not context.args:
        await update.message.reply_text("Формат: /regs <activityId>")
        return

    aid = context.args[0]
    r = requests.get(f"{BACKEND_BASE_URL}/admin/activities/{aid}/registrations", headers=_headers(), timeout=10)
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка: {r.status_code} {r.text}")
        return

    data = r.json()
    regs = data.get("registrations", [])
    if not regs:
        await update.message.reply_text("Записей нет.")
        return

    lines = []
    for x in regs:
        lines.append(f"userId={x['userId']} @{x.get('username')} status={x['status']}")
    await update.message.reply_text("\n".join(lines))

async def _mark(update: Update, context: ContextTypes.DEFAULT_TYPE, status: str):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("Нет доступа.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(f"Формат: /{status.lower()} <activityId> <userId>")
        return

    aid = int(context.args[0])
    uid = int(context.args[1])

    body = {"userId": uid, "status": status}
    r = requests.post(f"{BACKEND_BASE_URL}/admin/activities/{aid}/attendance", json=body, headers=_headers(), timeout=10)
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка: {r.status_code} {r.text}")
        return

    resp = r.json()
    awarded = resp.get("awardedAchievementIds", [])
    await update.message.reply_text(f"OK. status={status}. awarded={awarded}")

async def visit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _mark(update, context, "VISITED")

async def miss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _mark(update, context, "MISSED")

async def achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("Нет доступа.")
        return

    r = requests.get(f"{BACKEND_BASE_URL}/admin/achievements", headers=_headers(), timeout=10)
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка: {r.status_code} {r.text}")
        return

    items = r.json()
    if not items:
        await update.message.reply_text("Достижений нет.")
        return

    lines = [f"#{a['id']} {a['title']} (+{a['experience']}xp) auto={a['isAutomatic']}" for a in items]
    await update.message.reply_text("\n".join(lines))

async def award(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("Нет доступа.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Формат: /award <userId> <achievementId>")
        return

    user_id = int(context.args[0])
    ach_id = int(context.args[1])

    r = requests.post(
        f"{BACKEND_BASE_URL}/admin/users/{user_id}/award-achievement",
        json={"achievementId": ach_id},
        headers=_headers(),
        timeout=10
    )
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка: {r.status_code} {r.text}")
        return

    await update.message.reply_text(f"award ok={r.json().get('ok')}")

def main():
    token = os.getenv("ADMIN_BOT_TOKEN", "")
    if not token:
        raise RuntimeError("ADMIN_BOT_TOKEN is not set")
    if not ADMIN_API_KEY:
        raise RuntimeError("ADMIN_API_KEY is not set")
    if not BOT_ADMIN_IDS:
        raise RuntimeError("BOT_ADMIN_IDS is not set")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("activities", activities))
    app.add_handler(CommandHandler("create", create_activity))
    app.add_handler(CommandHandler("regs", regs))
    app.add_handler(CommandHandler("visit", visit))
    app.add_handler(CommandHandler("miss", miss))
    app.add_handler(CommandHandler("achievements", achievements))
    app.add_handler(CommandHandler("award", award))

    app.run_polling()

if __name__ == "__main__":
    main()
