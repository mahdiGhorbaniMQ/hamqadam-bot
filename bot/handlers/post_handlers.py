# bot/handlers/post_handlers.py
import logging
from typing import Any, Union, Coroutine

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler
)

from .. import localization as loc
from ..core_api_client import api_client
from ..config import DEFAULT_LANGUAGE  # Assuming DEFAULT_LANGUAGE is in your config

logger = logging.getLogger(__name__)
# CURRENT_LANG can be dynamically set per user later, e.g., from context.user_data.get('lang', DEFAULT_LANGUAGE)
CURRENT_LANG = DEFAULT_LANGUAGE

# States for the conversation using characters for better log readability if needed
POST_SELECT_TYPE, POST_TYPING_TITLE, POST_TYPING_CONTENT = map(chr, range(3))

# Predefined post types - align with your Core API's expectations
POST_TYPES = {
    "idea": {"en": "Idea", "fa": "ایده"},
    "article": {"en": "Article", "fa": "مقاله"},
    "proposal": {"en": "Proposal", "fa": "پیشنهاد"},
    "question": {"en": "Question", "fa": "پرسش"},
}


async def create_post_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Starts the conversation to create a new post."""
    auth_token = context.user_data.get('auth_token')
    if not auth_token:
        await update.message.reply_text(loc.get_string("not_logged_in", lang=CURRENT_LANG))
        return ConversationHandler.END

    context.user_data['new_post_data'] = {}  # Initialize a dict to store post details
    logger.info(f"User {update.effective_user.id} starting post creation. current_lang: {CURRENT_LANG}")

    keyboard = [
        [InlineKeyboardButton(details[CURRENT_LANG], callback_data=f"post_type_{key}")]
        for key, details in POST_TYPES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        loc.get_string("select_post_type_prompt", lang=CURRENT_LANG, default="Please select the type of your post:"),
        reply_markup=reply_markup
    )
    return POST_SELECT_TYPE


async def received_post_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handles post type selection from inline keyboard."""
    query = update.callback_query
    await query.answer()

    selected_type_key = query.data.split("post_type_")[1]

    if selected_type_key not in POST_TYPES:
        await query.edit_message_text(
            loc.get_string("invalid_option", lang=CURRENT_LANG, default="Invalid option selected. Please try again."))
        return ConversationHandler.END

        # Store canonical type, e.g., IDEA, ARTICLE
    context.user_data['new_post_data']['postType'] = selected_type_key.upper()

    type_display_name = POST_TYPES[selected_type_key][CURRENT_LANG]
    await query.edit_message_text(
        text=loc.get_string("post_type_selected_prompt_title", lang=CURRENT_LANG,
                            default="You selected: {type_name}.\nNow, please enter the title for your post:").format(
            type_name=type_display_name)
    )
    return POST_TYPING_TITLE


async def received_post_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handles title input."""
    title_text = update.message.text
    if not title_text or len(title_text.strip()) < 3:  # Basic validation
        await update.message.reply_text(loc.get_string("post_title_too_short", lang=CURRENT_LANG,
                                                       default="Title is too short. Please enter a more descriptive title:"))
        return POST_TYPING_TITLE  # Stay in the same state

    # Store title as an I18nString object for the current language
    context.user_data['new_post_data']['title'] = {CURRENT_LANG: title_text.strip()}

    await update.message.reply_text(
        loc.get_string("post_title_received_prompt_content", lang=CURRENT_LANG,
                       default="Great! Now please provide the main content for your post:")
    )
    return POST_TYPING_CONTENT


async def received_post_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """Handles content input and creates the draft post via API."""
    content_text = update.message.text
    auth_token = context.user_data.get('auth_token')
    user_info = context.user_data.get('user_info')

    if not user_info or not user_info.get('userId'):
        logger.error(f"User info or userId not found in context for user {update.effective_user.id}")
        await update.message.reply_text(loc.get_string("error_missing_user_info_for_post", lang=CURRENT_LANG,
                                                       default="Your user information is missing. Please /start again."))
        if 'new_post_data' in context.user_data:
            del context.user_data['new_post_data']
        return ConversationHandler.END

    if not content_text or len(content_text.strip()) < 10:
        await update.message.reply_text(loc.get_string("post_content_too_short", lang=CURRENT_LANG,
                                                       default="Content is too short. Please provide more details:"))
        return POST_TYPING_CONTENT

    context.user_data['new_post_data']['contentBody'] = {CURRENT_LANG: content_text.strip()}

    author_info_payload = {
        "authorId": user_info.get("userId"),
        "authorType": "USER"
    }

    post_payload = {
        "postType": context.user_data['new_post_data']['postType'],
        "title": context.user_data['new_post_data']['title'],
        "contentBody": context.user_data['new_post_data']['contentBody'],
        # Change "TEXT" to one of the accepted values, e.g., "MARKDOWN"
        "contentBodyType": "MARKDOWN",  # <<< --- MODIFIED HERE
        "authorInfo": author_info_payload,
    }

    logger.info(f"Attempting to create post with payload: {post_payload}")
    await update.message.reply_text(loc.get_string("creating_post_draft_wait", lang=CURRENT_LANG,
                                                   default="Creating your draft post, please wait..."))

    api_response = await api_client.create_post_draft(auth_token=auth_token, post_data=post_payload)

    if api_response and not api_response.get("_api_error") and api_response.get("postId"):
        post_id = api_response.get("postId")
        logger.info(f"Draft post created successfully by user {update.effective_user.id}. Post ID from API: {post_id}")
        await update.message.reply_text(
            loc.get_string("post_draft_created_success", lang=CURRENT_LANG,
                           default="Your draft post has been created successfully! Post ID: {post_id}").format(
                post_id=post_id)
        )
    else:
        logger.error(f"Failed to create post draft for user {update.effective_user.id}. API Response: {api_response}")
        error_detail = api_response.get("message", "Unknown error") if isinstance(api_response,
                                                                                  dict) else "Creation failed"
        await update.message.reply_text(
            loc.get_string("post_draft_created_fail", lang=CURRENT_LANG,
                           default="Failed to create draft: {error}").format(error=error_detail)
        )

    if 'new_post_data' in context.user_data:
        del context.user_data['new_post_data']
    return ConversationHandler.END

async def cancel_post_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the post creation conversation."""
    if 'new_post_data' in context.user_data:
        del context.user_data['new_post_data']

    message_text = loc.get_string("post_creation_cancelled", lang=CURRENT_LANG, default="Post creation cancelled.")
    if update.callback_query:
        await update.callback_query.edit_message_text(text=message_text)
    else:
        await update.message.reply_text(text=message_text)
    return ConversationHandler.END


async def my_drafts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays a list of the user's draft posts with action buttons."""
    auth_token = context.user_data.get('auth_token')
    user_lang = context.user_data.get('lang', CURRENT_LANG)  # Get user's preferred language if stored

    if not auth_token:
        await update.message.reply_text(loc.get_string("not_logged_in", lang=user_lang))
        return

    await update.message.reply_text(
        loc.get_string("fetching_drafts", lang=user_lang, default="Fetching your drafts..."))

    drafts_response = await api_client.get_my_posts(auth_token=auth_token, filters={"status": "DRAFT"})
    logger.info(f"RAW API Response for /mydrafts: {drafts_response}")  # Log the raw response

    if drafts_response and not drafts_response.get("_api_error"):
        posts_list = []
        if isinstance(drafts_response, list):
            posts_list = drafts_response
        elif isinstance(drafts_response, dict):
            if "data" in drafts_response and isinstance(drafts_response["data"], list):
                posts_list = drafts_response["data"]
            elif "content" in drafts_response and isinstance(drafts_response["content"], list):
                posts_list = drafts_response["content"]
            else:  # If API returns the list directly but wrapped in an object with other pagination info etc.
                # This part needs adjustment if your list is nested differently and not caught above.
                # For now, if not 'data' or 'content', we assume it might be a direct list if no other known wrapper.
                logger.warning(
                    f"Drafts response is a dict but 'data' or 'content' key not found or not a list. Keys: {drafts_response.keys()}")

        if not posts_list:
            await update.message.reply_text(
                loc.get_string("no_drafts_found", lang=user_lang, default="You have no draft posts."))
            return

        await update.message.reply_text(
            loc.get_string("your_draft_posts_title", lang=user_lang, default="Your Draft Posts:"))

        for post in posts_list[:5]:  # Display up to 5 drafts to avoid message too long error
            post_id = post.get("postId", "N/A")
            title_obj = post.get("title", {"en": "Untitled", "fa": "بدون عنوان"})

            title_display = "Untitled"
            if isinstance(title_obj, dict):
                title_display = title_obj.get(user_lang, title_obj.get("en", "Untitled"))
            elif isinstance(title_obj, str):
                title_display = title_obj

            post_status = post.get("status", "UNKNOWN")  # Get post status if available

            message_text = f"📝 *{title_display}*\n"
            message_text += f"   ID: `{post_id}`\n"
            message_text += f"   Status: `{post_status}`"

            # Define callback data strings
            # Format: action:entity_type:entity_id
            # Example: edit:post_draft:123ab_or_publish:post_draft:123ab
            edit_callback = f"postaction_edit_draft_{post_id}"
            publish_callback = f"postaction_publish_draft_{post_id}"
            delete_callback = f"postaction_delete_draft_{post_id}"

            keyboard = [
                [
                    InlineKeyboardButton(loc.get_string("edit_button", lang=user_lang, default="Edit"),
                                         callback_data=edit_callback),
                    InlineKeyboardButton(loc.get_string("publish_button", lang=user_lang, default="Publish"),
                                         callback_data=publish_callback),
                ],
                [
                    InlineKeyboardButton(loc.get_string("delete_button", lang=user_lang, default="Delete"),
                                         callback_data=delete_callback)
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send each post as a separate message with its own keyboard
            await update.message.reply_text(text=message_text, reply_markup=reply_markup, parse_mode='Markdown')

        if len(posts_list) > 5:
            await update.message.reply_text(loc.get_string("more_drafts_available", lang=user_lang,
                                                           default="More drafts are available. Displaying first 5."))

    else:
        logger.error(f"Failed to fetch drafts for user {update.effective_user.id}. API Response: {drafts_response}")
        error_detail = drafts_response.get("message", "Unknown error") if isinstance(drafts_response,
                                                                                     dict) else "Failed to fetch"
        await update.message.reply_text(
            loc.get_string("fetch_drafts_fail", lang=user_lang, default="Could not fetch your drafts: {error}").format(
                error=error_detail)
        )

# Fallback handlers for the conversation
FALLBACK_HANDLERS = [
    CommandHandler('cancelpost', cancel_post_creation),
    # Example for cancelling with a keyword, ensure 'cancel_keyword' is in localization.py
    # MessageHandler(filters.Regex(f'^({loc.get_string("cancel_keyword", lang=CURRENT_LANG, default="cancel")})$'), cancel_post_creation),
]

create_post_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('createpost', create_post_start)],
    states={
        POST_SELECT_TYPE: [CallbackQueryHandler(received_post_type_callback, pattern='^post_type_.*$')],
        POST_TYPING_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_post_title)],
        POST_TYPING_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_post_content)],
    },
    fallbacks=FALLBACK_HANDLERS,
    # For persistence across bot restarts (requires Application persistence setup)
    # name="create_post_conversation",
    # persistent=True,
)

# List of handlers to be imported and added in main.py
handlers_to_add = [
    create_post_conv_handler,
    CommandHandler('mydrafts', my_drafts_command),
]