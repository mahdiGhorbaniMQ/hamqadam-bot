# bot/main.py

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from bot.config import DEFAULT_LANGUAGE
# Corrected import for config and added localization
from . import config  # Assumes you run with "python -m bot.main" from parent dir
from . import localization as loc # Import our localization module

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Language Selection (Example: could be per-user later) ---
# For now, let's use a global variable or a simple context-based selection.
# A more robust solution would store user language preference in context.user_data
CURRENT_LANG = DEFAULT_LANGUAGE # Or "en", or get from user preferences

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the /start command is issued."""
    user = update.effective_user
    welcome_message = loc.get_string(
        "welcome",
        lang=CURRENT_LANG, # You'd ideally get this from user data
        user_mention=user.mention_html()
    )
    await update.message.reply_html(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the /help command is issued."""
    help_text = loc.get_string("help_text", lang=CURRENT_LANG)
    await update.message.reply_text(help_text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message if it's not a command."""
    if update.message.text and not update.message.text.startswith('/'):
        # This is just for testing the bot responds.
        # We will replace this with actual command parsing for 'hq' prefix later.
        reply_text = loc.get_string(
            "message_received",
            lang=CURRENT_LANG,
            text=update.message.text
        )
        await update.message.reply_text(reply_text)


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # To enable echo for testing (optional)
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info(loc.get_string("bot_started", lang=CURRENT_LANG)) # Using localized string
    application.run_polling()

if __name__ == "__main__":
    main()