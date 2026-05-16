# server/app/utils/telegram.py
import hashlib
import hmac
import urllib.parse
import time
import os
from typing import Optional, Dict

def validate_telegram_init_data(init_data: str, bot_token: str, max_age_sec: int = 86400) -> Optional[Dict]:
    """Валидация initData от Telegram Mini App (HMAC-SHA256)"""
    
    # 🔧 DEV MODE: пропускаем валидацию для локальной разработки
    if os.getenv("APP_ENV") == "development" and not init_data:
        return {"user": '{"id": "test_123", "username": "DevUser"}', "auth_date": str(int(time.time()))}
    
    if not init_data:
        return None

    parsed = dict(urllib.parse.parse_qsl(init_data))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    data_check_arr = sorted([f"{k}={v}" for k, v in parsed.items()])
    data_check_string = "\n".join(data_check_arr)

    secret_key = hmac.new(
        b"WebAppData", 
        bot_token.encode("utf-8"), 
        hashlib.sha256
    ).digest()

    expected_hash = hmac.new(
        secret_key, 
        data_check_string.encode("utf-8"), 
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        return None

    auth_date = int(parsed.get("auth_date", 0))
    if time.time() - auth_date > max_age_sec:
        return None

    return parsed