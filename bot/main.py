# bot/main.py

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
# For persistence (optional, but recommended for production)
# from telegram.ext import PicklePersistence

from . import config
from . import localization as loc
from .core_api_client import api_client

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Determine language (can be made more sophisticated later, e.g., per user)
CURRENT_LANG = getattr(config, 'DEFAULT_LANGUAGE', loc.DEFAULT_LANG)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    telegram_id = user.id
    telegram_username = user.username

    logger.info(f"User {telegram_id} (@{telegram_username}) started the bot.")

    api_login_response = await api_client.login_or_register_telegram_user(
        telegram_id=telegram_id,
        telegram_username=telegram_username
    )
    logger.info(f"RAW API Login Response: {api_login_response}")

    if isinstance(api_login_response, dict) and not api_login_response.get("_api_error"):
        token = api_login_response.get("accessToken")
        user_data_from_api = api_login_response.get("user")

        logger.debug(f"Extracted token: {token[:15]}... (partial)")
        logger.debug(f"Extracted user_data_from_api: {user_data_from_api}")

        if token and user_data_from_api and isinstance(user_data_from_api, dict) and user_data_from_api.get("userId"):
            context.user_data['auth_token'] = token
            context.user_data['user_info'] = user_data_from_api  # This is the 'user' object from login

            user_name_display = user.mention_html()
            full_name_obj = user_data_from_api.get("fullName")  # As per your example, this was None

            if isinstance(full_name_obj, str) and full_name_obj.strip():
                user_name_display = full_name_obj
            elif isinstance(full_name_obj, dict):  # If API changes to return i18n full_name
                user_name_display = full_name_obj.get(CURRENT_LANG) or user.first_name

            logger.info(f"User {telegram_id} logged/registered. UserID: {user_data_from_api.get('userId')}")

            await update.message.reply_html(
                loc.get_string("welcome_registered", lang=CURRENT_LANG, user_mention=user_name_display)
            )

            # Optionally, fetch full profile immediately after login
            # The 'user' object from login might be sufficient for 'user_info'
            # 'full_profile' can be used if /users/me returns more or different details.
            # For now, user_info from login is stored. /me command will explicitly fetch from /users/me.

        else:
            logger.error(
                f"Login API call seemed successful, but critical data missing. Token: {token}, UserData: {user_data_from_api}")
            await update.message.reply_text(
                loc.get_string("login_data_incomplete_error", lang=CURRENT_LANG)
            )
    else:  # API error or unexpected structure
        error_detail = "Invalid API response structure or API error."
        if isinstance(api_login_response, dict) and api_login_response.get("_api_error"):
            error_detail = api_login_response.get("message", "Unknown API error.")

        logger.error(f"Failed to login/register user {telegram_id}. API Response: {api_login_response}")
        await update.message.reply_text(
            loc.get_string("login_failed", lang=CURRENT_LANG, error_details=error_detail)
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(loc.get_string("help_text", lang=CURRENT_LANG))


async def me_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    auth_token = context.user_data.get('auth_token')
    if not auth_token:
        await update.message.reply_text(loc.get_string("not_logged_in", lang=CURRENT_LANG))
        return

    logger.info(f"User {update.effective_user.id} requested /me. Fetching profile.")
    profile_response = await api_client.get_my_profile(auth_token=auth_token)
    logger.info(f"RAW API Profile Response (/me): {profile_response}")

    if isinstance(profile_response, dict) and not profile_response.get("_api_error"):
        # Assuming the profile_response is the user object itself,
        # or if it's nested like {"user": {...}}, adjust accordingly.
        # Based on your login response, /users/me might directly return the user object.

        # Let's assume the API returns the user object directly as the response
        # or it's under a "user" key if it's part of a larger wrapper
        user_profile = profile_response.get("user") if "user" in profile_response else profile_response

        if user_profile and isinstance(user_profile, dict) and user_profile.get("userId"):
            context.user_data['full_profile'] = user_profile  # Store/update full profile

            user_id = user_profile.get("userId", "N/A")

            full_name = user_profile.get("fullName")  # This was None in your login example
            if isinstance(full_name, dict):  # If API returns i18n string for fullName
                full_name = full_name.get(CURRENT_LANG, "N/A")
            elif not full_name:  # If None or empty string
                full_name = update.effective_user.full_name  # Fallback to Telegram name

            telegram_username = user_profile.get("telegramUsername", "N/A")
            account_status = user_profile.get("accountStatus", "N/A")

            profile_text_title = loc.get_string("user_profile_info_title", lang=CURRENT_LANG)
            profile_text_details = loc.get_string(
                "user_profile_info",
                lang=CURRENT_LANG,
                user_id=user_id,
                full_name=full_name,
                telegram_username=telegram_username,
                account_status=account_status
            )
            await update.message.reply_text(f"{profile_text_title}\n{profile_text_details}")
        else:
            logger.error(f"Failed to parse profile data for /me. Response: {profile_response}")
            await update.message.reply_text(loc.get_string("profile_fetch_error", lang=CURRENT_LANG))
    else:
        error_detail = "Failed to fetch profile."
        if isinstance(profile_response, dict) and profile_response.get("_api_error"):
            error_detail = profile_response.get("message", error_detail)
        logger.error(f"API error fetching profile for /me. Details: {error_detail}")
        await update.message.reply_text(loc.get_string("profile_fetch_error", lang=CURRENT_LANG))


def main() -> None:
    # For persistence (data will be saved in 'bot_persistence.pickle')
    # persistence = PicklePersistence(filepath="bot_persistence.pickle")
    # application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).persistence(persistence).build()

    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("me", me_command))  # Add the /me command handler

    logger.info(loc.get_string("bot_started", lang=CURRENT_LANG))
    application.run_polling()


if __name__ == "__main__":
    main()