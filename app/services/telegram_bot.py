import requests

def send_message(bot_token: str, chat_id: int, text: str) -> bool:
    """
    chat_id для Telegram пользователя = его telegram_id.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    }
    r = requests.post(url, json=payload, timeout=10)
    return r.status_code == 200
