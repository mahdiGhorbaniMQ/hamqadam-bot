# bot/localization.py
from typing import Optional

STRINGS = {
    "en": {
        "welcome": "Hello {user_mention}! Welcome to hamqadam-bot.",
        "welcome_registered": "Welcome back, {user_mention}! You are successfully connected to Hamqadam.",
        "help_text": "Use /start to login or register.\nUse /me to see your profile info.",
        "message_received": "Message received: {text}",
        "bot_started": "Bot started...",
        "login_failed": "Login failed. Please try again later. Details: {error_details}",
        "login_data_mismatch_error": "There was an issue processing your login data. Please try again.",
        "login_data_incomplete_error": "Login was successful, but some essential user data is missing. Please contact support or try again later.",
        "profile_fetch_error": "Could not fetch your full profile details at this moment.",
        "user_profile_info_title": "Your Hamqadam Profile:",
        "user_profile_info": "ID: {user_id}\nName: {full_name}\nTelegram: @{telegram_username}\nStatus: {account_status}",
        "not_logged_in": "You are not logged in. Please use /start first.",
    },
    "fa": {
        "welcome": "سلام {user_mention}! به بات همقدم خوش آمدید.",
        "welcome_registered": "خوش آمدید {user_mention}! شما با موفقیت به همقدم متصل شدید.",
        "help_text": "برای ورود یا ثبت‌نام از دستور /start استفاده کنید.\nبرای مشاهده اطلاعات پروفایل خود از دستور /me استفاده کنید.",
        "message_received": "پیام دریافت شد: {text}",
        "bot_started": "بات شروع به کار کرد...",
        "login_failed": "ورود ناموفق بود. لطفا بعدا تلاش کنید. جزئیات: {error_details}",
        "login_data_mismatch_error": "در پردازش اطلاعات ورود شما مشکلی پیش آمد. لطفا دوباره تلاش کنید.",
        "login_data_incomplete_error": "ورود موفقیت آمیز بود اما برخی اطلاعات ضروری کاربر موجود نیست. لطفا با پشتیبانی تماس بگیرید یا بعدا تلاش کنید.",
        "profile_fetch_error": "در حال حاضر امکان دریافت کامل جزئیات پروفایل شما وجود ندارد.",
        "user_profile_info_title": "پروفایل همقدم شما:",
        "user_profile_info": "شناسه: {user_id}\nنام: {full_name}\nتلگرام: @{telegram_username}\nوضعیت: {account_status}",
        "not_logged_in": "شما وارد نشده‌اید. لطفاً ابتدا از دستور /start استفاده کنید.",
    }
}

DEFAULT_LANG = "fa" # Or "en"

def get_string(key: str, lang: str = DEFAULT_LANG, default: Optional[str] = None, **kwargs) -> str:
    try:
        return STRINGS[lang][key].format(**kwargs)
    except KeyError:
        try:
            return STRINGS[DEFAULT_LANG][key].format(**kwargs)
        except KeyError:
            if default is not None:
                return default.format(**kwargs)
            return f"<{key}_NOT_FOUND>"