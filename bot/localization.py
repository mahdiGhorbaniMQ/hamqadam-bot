# bot/localization.py
from typing import Optional

STRINGS = {
    "en": {
        "welcome": "Hello {user_mention}! Welcome to hamqadam-bot.",
        "welcome_registered": "Welcome back, {user_mention}! You are successfully connected to Hamqadam.",
        "help_text": "Help: No specific help command available yet.",
        "message_received": "Message received: {text}",
        "bot_started": "Bot started...",
        "login_failed": "Login failed. Please try again later. Details: {error_details}",
        "profile_fetch_error": "Could not fetch your full profile details at this moment.",
    },
    "fa": {
        "welcome": "سلام {user_mention}! به hamqadam-bot خوش آمدید.",
        "welcome_registered": "خوش آمدید {user_mention}! شما با موفقیت به همقدم متصل شدید.",
        "help_text": "راهنما: فعلا دستور خاصی برای کمک وجود ندارد.",
        "message_received": "پیام دریافت شد: {text}",
        "bot_started": "بات شروع به کار کرد...",
        "login_failed": "ورود ناموفق بود. لطفا بعدا تلاش کنید. جزئیات: {error_details}",
        "profile_fetch_error": "در حال حاضر امکان دریافت کامل جزئیات پروفایل شما وجود ندارد.",
    }
}
# ... (get_string function remains the same) ...
DEFAULT_LANG = "en" # Or "fa"

def get_string(key: str, lang: str = DEFAULT_LANG, default: Optional[str] = None, **kwargs) -> str:
    """
    Retrieves a localized string.
    Falls back to the default language if the key is not found in the specified language.
    Uses provided 'default' if key is not found anywhere.
    """
    try:
        return STRINGS[lang][key].format(**kwargs)
    except KeyError:
        try:
            return STRINGS[DEFAULT_LANG][key].format(**kwargs)
        except KeyError:
            if default is not None:
                return default.format(**kwargs) # Ensure default can also be formatted
            return f"<{key}_NOT_FOUND>"