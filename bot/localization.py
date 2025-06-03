# bot/localization.py
import logging
from typing import Optional

STRINGS = {
    "en": {
        # General & Main anp.py
        "welcome": "Hello {user_mention}! Welcome to hamqadam-bot.",
        "welcome_registered": "Welcome back, {user_mention}! You are successfully connected to Hamqadam.",
        "help_text": "Use /start to login or register.\nUse /me to see your profile info.\nUse /createpost to create a new post.\nUse /mydrafts to see your drafts.",
        "bot_started": "Bot started...",
        "login_failed": "Login failed. Please try again later. Details: {error_details}",
        "login_data_incomplete_error": "Login was successful, but some essential user data is missing. Please contact support or try again later.",
        "profile_fetch_error": "Could not fetch your full profile details at this moment.",
        "user_profile_info_title": "Your Hamqadam Profile:",
        "user_profile_info": "ID: {userId}\nName: {fullName}\nTelegram: @{telegramUsername}\nStatus: {accountStatus}",
        "not_logged_in": "You are not logged in. Please use /start first.",

        # Post Handlers (post_handlers.py)
        "select_post_type_prompt": "Please select the type of your post:",
        "invalid_option": "Invalid option selected. Please try again or use /cancelpost to cancel.",
        "post_type_selected_prompt_title": "You selected: {type_name}.\nNow, please enter the title for your post:",
        "post_title_too_short": "Title is too short (minimum 3 characters). Please enter a more descriptive title:",
        "post_title_received_prompt_content": "Great! Now please provide the main content for your post:",
        "post_content_too_short": "Content is too short (minimum 10 characters). Please provide more details:",
        "creating_post_draft_wait": "Creating your draft post, please wait...",
        "post_draft_created_success": "Your draft post has been created successfully! Post ID: {post_id}",
        "post_draft_created_fail": "Failed to create draft: {error}",
        "post_creation_cancelled": "Post creation cancelled.",

        "fetching_drafts": "Fetching your drafts...",
        "no_drafts_found": "You have no draft posts.",
        "your_draft_posts_title": "Your Draft Posts:",
        "fetch_drafts_fail": "Could not fetch your drafts: {error}",

        "edit_button": "Edit",  # For future use with inline keyboards on drafts list
        "publish_button": "Publish",  # For future use
        "delete_button": "Delete",  # For future use

        "cancel_keyword": "cancel",  # Optional, for regex based cancel
    },
    "fa": {
        # عمومی و main.py
        "welcome": "سلام {user_mention}! به بات همقدم خوش آمدید.",
        "welcome_registered": "خوش آمدید {user_mention}! شما با موفقیت به همقدم متصل شدید.",
        "help_text": "برای ورود یا ثبت‌نام از دستور /start استفاده کنید.\nبرای مشاهده اطلاعات پروفایل خود از دستور /me استفاده کنید.\nبرای ایجاد پست جدید از دستور /createpost استفاده کنید.\nبرای مشاهده پیش‌نویس‌های خود از دستور /mydrafts استفاده کنید.",
        "bot_started": "بات شروع به کار کرد...",
        "login_failed": "ورود ناموفق بود. لطفا بعدا تلاش کنید. جزئیات: {error_details}",
        "login_data_incomplete_error": "ورود موفقیت آمیز بود اما برخی اطلاعات ضروری کاربر موجود نیست. لطفا با پشتیبانی تماس بگیرید یا بعدا تلاش کنید.",
        "profile_fetch_error": "در حال حاضر امکان دریافت کامل جزئیات پروفایل شما وجود ندارد.",
        "user_profile_info_title": "پروفایل همقدم شما:",
        "user_profile_info": "شناسه: {userId}\nنام: {fullName}\nتلگرام: @{telegramUsername}\nوضعیت: {accountStatus}",
        "not_logged_in": "شما وارد نشده‌اید. لطفاً ابتدا از دستور /start استفاده کنید.",

        # مربوط به پست‌ها (post_handlers.py)
        "select_post_type_prompt": "لطفا نوع پست خود را انتخاب کنید:",
        "invalid_option": "گزینه نامعتبر است. لطفا دوباره تلاش کنید یا برای لغو از دستور /cancelpost استفاده کنید.",
        "post_type_selected_prompt_title": "شما انتخاب کردید: {type_name}.\nحالا لطفا عنوان پست خود را وارد کنید:",
        "post_title_too_short": "عنوان بسیار کوتاه است (حداقل ۳ کاراکتر). لطفا عنوان توصیفی‌تری وارد کنید:",
        "post_title_received_prompt_content": "عالی! حالا لطفا محتوای اصلی پست خود را وارد کنید:",
        "post_content_too_short": "محتوا بسیار کوتاه است (حداقل ۱۰ کاراکتر). لطفا جزئیات بیشتری ارائه دهید:",
        "creating_post_draft_wait": "در حال ایجاد پیش‌نویس پست شما، لطفا صبر کنید...",
        "post_draft_created_success": "پیش‌نویس پست شما با موفقیت ایجاد شد! شناسه پست: {post_id}",
        "post_draft_created_fail": "ایجاد پیش‌نویس ناموفق بود: {error}",
        "post_creation_cancelled": "ایجاد پست لغو شد.",

        "fetching_drafts": "در حال دریافت پیش‌نویس‌های شما...",
        "no_drafts_found": "شما هیچ پیش‌نویس فعالی ندارید.",
        "your_draft_posts_title": "پیش‌نویس‌های شما:",
        "fetch_drafts_fail": "خطا در دریافت پیش‌نویس‌ها: {error}",

        "edit_button": "ویرایش",  # برای استفاده آینده با دکمه‌های لیست پیش‌نویس‌ها
        "publish_button": "انتشار",  # برای استفاده آینده
        "delete_button": "حذف",  # برای استفاده آینده

        "cancel_keyword": "لغو",  # اختیاری، برای لغو مکالمه با کلمه کلیدی
    }
}

# زبان پیش‌فرض را می‌توانید از فایل config.py هم بخوانید اگر آنجا تعریف کرده باشید
# from ..config import DEFAULT_LANGUAGE
# DEFAULT_LANG = DEFAULT_LANGUAGE
DEFAULT_LANG = "fa"  # یا "en"


def get_string(key: str, lang: str = DEFAULT_LANG, default: Optional[str] = None, **kwargs) -> str:
    """
    Retrieves a localized string.
    Falls back to the default language if the key is not found in the specified language.
    Uses provided 'default' if key is not found anywhere.
    If a default is provided and formatting fails, it returns the unformatted default.
    """
    try:
        return STRINGS[lang][key].format(**kwargs)
    except KeyError:
        try:
            return STRINGS[DEFAULT_LANG][key].format(**kwargs)
        except KeyError:
            if default is not None:
                try:
                    return default.format(**kwargs)
                except KeyError:  # If default itself has placeholders that are not provided in kwargs
                    return default  # Return unformatted default
            return f"<{key}_NOT_FOUND_IN_{lang}_OR_{DEFAULT_LANG}>"  # More specific fallback
    except KeyError as e:  # Handles missing keys in kwargs during .format()
        # This case might happen if a placeholder like {post_id} is in the string,
        # but post_id is not provided in kwargs.
        logger = logging.getLogger(__name__)  # Local logger import to avoid top-level if not always needed
        logger.warning(f"Missing key '{e}' in kwargs for string '{key}' in lang '{lang}'. Kwargs: {kwargs}")
        # Fallback to returning the unformatted string from the selected language or default language
        try:
            return STRINGS[lang][key]
        except KeyError:
            try:
                return STRINGS[DEFAULT_LANG][key]
            except KeyError:
                if default is not None:
                    return default
                return f"<{key}_FORMAT_ERROR_AND_NOT_FOUND>"

# It's good practice to have a logger instance if get_string does logging
# but if this file is imported by others that already set up logging, it might be okay.
# Consider passing a logger instance or using logging.getLogger(__name__) inside the function if needed.