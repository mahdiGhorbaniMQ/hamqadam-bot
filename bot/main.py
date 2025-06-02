# bot/main.py

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from bot.config import DEFAULT_LANGUAGE
from . import config
from . import localization as loc
from .core_api_client import api_client  # Import the global api_client instance

# Enable logging (ensure it's configured as before)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

CURRENT_LANG = DEFAULT_LANGUAGE  # Or "en", or get from user preferences / context.user_data


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command: registers/logs in the user and welcomes them."""
    user = update.effective_user
    telegram_id = user.id
    telegram_username = user.username

    logger.info(f"User {telegram_id} ({telegram_username}) started the bot.")

    # Call the Core API to login or register the user
    api_response = await api_client.login_or_register_telegram_user(
        telegram_id=telegram_id,
        telegram_username=telegram_username
    )

    if api_response and api_response.get("status") == "success":
        user_data_from_api = api_response.get("data", {}).get("user", {})
        token = api_response.get("data", {}).get("token")

        # Store token and user info in context.user_data for this user's session
        context.user_data['auth_token'] = token
        context.user_data['user_info'] = user_data_from_api  # Store basic user info
        # You might want to set user's preferred language from user_data_from_api if available
        # For now, we'll keep CURRENT_LANG global or manually set

        user_name_display = user.mention_html()
        if user_data_from_api.get("full_name"):
            # Assuming full_name is an I18nString like {"en": "Name", "fa": "نام"}
            user_name_display = user_data_from_api["full_name"].get(CURRENT_LANG, user.first_name)

        logger.info(f"User {telegram_id} logged in/registered successfully. Token stored in user_data.")

        welcome_message_key = "welcome_registered"  # Potentially a different welcome
        welcome_message = loc.get_string(
            welcome_message_key,
            lang=CURRENT_LANG,
            user_mention=user_name_display
        )
        # If you don't have 'welcome_registered', fallback or use 'welcome'
        if welcome_message == f"<{welcome_message_key}_NOT_FOUND>":
            welcome_message = loc.get_string(
                "welcome",
                lang=CURRENT_LANG,
                user_mention=user_name_display
            )
        await update.message.reply_html(welcome_message)

        # Optionally, try to fetch full profile after login
        if token:
            profile_response = await api_client.get_my_profile(auth_token=token)
            if profile_response and profile_response.get("status") == "success":
                full_profile_data = profile_response.get("data", {})
                context.user_data['full_profile'] = full_profile_data  # Update/store more details
                logger.info(
                    f"Successfully fetched full profile for user {telegram_id}: {full_profile_data.get('user_id')}")
                # You could send another message here with more profile info if desired
            else:
                logger.warning(f"Could not fetch full profile for user {telegram_id} after login.")
                await update.message.reply_text(
                    loc.get_string("profile_fetch_error", lang=CURRENT_LANG,
                                   default="Could not fetch your full profile details right now.")
                )

    else:
        logger.error(f"Failed to login/register user {telegram_id}. API Response: {api_response}")
        error_message_key = "login_failed"
        error_detail = api_response.get("message", "Unknown error.")
        # Consider if you want to show error_detail to the user, might be too technical

        error_message = loc.get_string(
            error_message_key,
            lang=CURRENT_LANG,
            error_details=error_detail  # Add error_details to your localization if needed
        )
        if error_message == f"<{error_message_key}_NOT_FOUND>":
            error_message = f"Login failed. Please try again later. ({error_detail})"

        await update.message.reply_text(error_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the /help command is issued."""
    help_text = loc.get_string("help_text", lang=CURRENT_LANG)
    await update.message.reply_text(help_text)


# (echo function can remain as is or be removed if not needed for now)

def main() -> None:
    """Start the bot."""
    # Ensure persistence for user_data if you want it to survive bot restarts
    # from telegram.ext import PicklePersistence
    # persistence = PicklePersistence(filepath="bot_data/user_persistence") # Example path
    # application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).persistence(persistence).build()

    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    logger.info(loc.get_string("bot_started", lang=CURRENT_LANG))
    application.run_polling()


if __name__ == "__main__":
    main()