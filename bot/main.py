# bot/main.py

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, \
    ContextTypes  # Removed MessageHandler, filters if not used directly here
# For persistence (optional, but recommended for production)
# from telegram.ext import PicklePersistence

from . import config
from . import localization as loc
from .core_api_client import api_client
# Import the list of handlers from post_handlers.py
from .handlers.post_handlers import handlers_to_add as post_handlers_list

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

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

        logger.debug(f"Extracted token (first 15 chars): {str(token)[:15]}...")
        logger.debug(f"Extracted user_data_from_api: {user_data_from_api}")

        if token and user_data_from_api and isinstance(user_data_from_api, dict) and user_data_from_api.get("userId"):
            context.user_data['auth_token'] = token
            context.user_data['user_info'] = user_data_from_api

            user_name_display = user.mention_html()
            full_name_value = user_data_from_api.get("fullName")

            if isinstance(full_name_value, str) and full_name_value.strip():
                user_name_display = full_name_value
            elif isinstance(full_name_value, dict):
                user_name_display = full_name_value.get(CURRENT_LANG) or user.first_name

            logger.info(f"User {telegram_id} logged/registered. UserID: {user_data_from_api.get('userId')}")

            await update.message.reply_html(
                loc.get_string("welcome_registered", lang=CURRENT_LANG, user_mention=user_name_display)
            )
        else:
            logger.error(
                f"Login API call success, but critical data missing. Token: {token}, UserData: {user_data_from_api}")
            await update.message.reply_text(loc.get_string("login_data_incomplete_error", lang=CURRENT_LANG))
    else:
        error_detail = "Invalid API response or API error."
        if isinstance(api_login_response, dict) and api_login_response.get("_api_error"):
            error_detail = api_login_response.get("message", "Unknown API error.")

        logger.error(f"Failed to login/register user {telegram_id}. API Response: {api_login_response}")
        await update.message.reply_text(loc.get_string("login_failed", lang=CURRENT_LANG, error_details=error_detail))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(loc.get_string("help_text", lang=CURRENT_LANG))


async def me_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    auth_token = context.user_data.get('auth_token')
    if not auth_token:
        await update.message.reply_text(loc.get_string("not_logged_in", lang=CURRENT_LANG))
        return

    logger.info(f"User {update.effective_user.id} requested /me. Fetching profile.")
    profile_api_response = await api_client.get_my_profile(auth_token=auth_token)
    logger.info(f"RAW API Profile Response (/me): {profile_api_response}")

    if isinstance(profile_api_response, dict) and not profile_api_response.get("_api_error"):
        user_profile_data = {}
        if "user" in profile_api_response and isinstance(profile_api_response["user"], dict):
            user_profile_data = profile_api_response["user"]
        elif "data" in profile_api_response and isinstance(profile_api_response["data"], dict):
            user_profile_data = profile_api_response["data"].get("user", profile_api_response["data"])
        elif "userId" in profile_api_response:  # If the response IS the user object directly
            user_profile_data = profile_api_response

        if user_profile_data and user_profile_data.get("userId"):
            context.user_data['full_profile'] = user_profile_data

            user_id = user_profile_data.get("userId", "N/A")
            full_name = user_profile_data.get("fullName")
            if isinstance(full_name, dict):
                full_name = full_name.get(CURRENT_LANG, "N/A")
            elif not full_name:  # Handles None or empty string
                full_name = update.effective_user.full_name

            telegram_username = user_profile_data.get("telegramUsername", "N/A")
            account_status = user_profile_data.get("accountStatus", "N/A")

            profile_text_title = loc.get_string("user_profile_info_title", lang=CURRENT_LANG)
            profile_text_details = loc.get_string(
                "user_profile_info",
                lang=CURRENT_LANG,
                userId=user_id,
                fullName=full_name,
                telegramUsername=telegram_username,
                accountStatus=account_status
            )
            await update.message.reply_text(f"{profile_text_title}\n{profile_text_details}")
        else:
            logger.error(f"Failed to parse profile data for /me. Response: {profile_api_response}")
            await update.message.reply_text(loc.get_string("profile_fetch_error", lang=CURRENT_LANG))
    else:
        error_detail = "Failed to fetch profile."
        if isinstance(profile_api_response, dict) and profile_api_response.get("_api_error"):
            error_detail = profile_api_response.get("message", error_detail)
        logger.error(f"API error fetching profile for /me. Details: {error_detail}")
        await update.message.reply_text(loc.get_string("profile_fetch_error", lang=CURRENT_LANG))


def main() -> None:
    # For persistence (uncomment and configure if needed):
    # persistence = PicklePersistence(filepath="bot_persistence.pickle")
    # application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).persistence(persistence).build()

    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add core command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("me", me_command))

    # Add handlers from post_handlers.py
    for handler in post_handlers_list:
        application.add_handler(handler)

    logger.info(loc.get_string("bot_started", lang=CURRENT_LANG))
    application.run_polling()


if __name__ == "__main__":
    main()