import hashlib
import hmac
from urllib.parse import parse_qsl

def verify_init_data(init_data: str, bot_token: str) -> dict | None:
    data = dict(parse_qsl(init_data))
    received_hash = data.pop("hash", None)

    check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()

    calculated_hash = hmac.new(
        secret_key,
        check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if calculated_hash != received_hash:
        return None

    return data
