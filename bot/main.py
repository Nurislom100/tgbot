import hashlib
import hmac
import json
import os
from urllib.parse import parse_qsl

BOT_TOKEN = os.environ["BOT_TOKEN"]


def validate_init_data(init_data: str):
    """Telegram WebApp initData'ni tekshiradi va foydalanuvchi ma'lumotini qaytaradi.
    Soxta so'rovlarning oldini olish uchun HAR BIR so'rovda ishlatiladi."""
    try:
        if not init_data:
            print("DEBUG: init_data bo'sh keldi")
            return None

        parsed = dict(parse_qsl(init_data, strict_parsing=True))
        parsed.pop("signature", None)
        received_hash = parsed.pop("hash", None)
        if not received_hash:
            print("DEBUG: hash topilmadi, kelgan kalitlar:", list(parsed.keys()))
            return None

        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if computed_hash != received_hash:
            print("DEBUG: hash mos kelmadi")
            print("DEBUG: BOT_TOKEN uzunligi:", len(BOT_TOKEN))
            print("DEBUG: computed:", computed_hash)
            print("DEBUG: received:", received_hash)
            return None

        user = json.loads(parsed.get("user", "{}"))
        return user
    except Exception as e:
        print("DEBUG: exception:", repr(e))
        return None
