import hashlib
import hmac
import json
import os
from urllib.parse import parse_qsl

BOT_TOKEN = os.environ["BOT_TOKEN"].strip()


def validate_init_data(init_data: str):
    """Telegram WebApp initData'ni tekshiradi va (user, xato_sababi) qaytaradi."""
    if not init_data:
        return None, "initData bo'sh keldi"
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=False, keep_blank_values=True))
        parsed.pop("signature", None)
        received_hash = parsed.pop("hash", None)
        if not received_hash:
            return None, f"hash topilmadi. kalitlar: {list(parsed.keys())}"

        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if computed_hash != received_hash:
            return None, f"hash mos kelmadi. token_len={len(BOT_TOKEN)}"

        user = json.loads(parsed.get("user", "{}"))
        return user, None
    except Exception as e:
        return None, f"xato: {e!r}"
