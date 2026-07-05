# NomadShare - Core Commands
# /start also handles deep links: https://t.me/<bot>?start=<short_code>
# That's what actually delivers a file back to someone who opens a shared
# link — the old app.py only ever returned JSON, it never sent the file.

import logging
from telegram import Update
from telegram.ext import ContextTypes

from app.config import ADMINS, BOT_VERSION
from app.constants import script
from core.views import start_view, help_view
from core.notify import log_event, report_error
from database.users import get_user, add_user
from database.links import get_link
from database.files import get_file, increment_access_count
from tools.formatters import esc

logger = logging.getLogger(__name__)


async def _deliver_file(update: Update, context: ContextTypes.DEFAULT_TYPE, short_code: str):
    link_data = await get_link(short_code)
    if not link_data or not link_data.get('is_active', True):
        await update.message.reply_text(script.INVALID_LINK)
        return

    file_data = await get_file(link_data['file_id'])
    if not file_data:
        await update.message.reply_text(script.FILE_NOT_FOUND)
        return

    chat_id = update.effective_chat.id
    category = file_data.get('category', 'document')

    try:
        if category == 'text':
            # No Telegram file_id for saved text — send the stored content
            # verbatim, not parsed as HTML (arbitrary text could contain
            # "<3" or similar that Telegram's HTML parser would choke on).
            await context.bot.send_message(
                chat_id, file_data.get('text_content') or "", parse_mode=None
            )
        else:
            telegram_file_id = file_data['file_id']
            caption = esc(file_data.get('file_name', ''))
            if category == 'photo':
                await context.bot.send_photo(chat_id, telegram_file_id, caption=caption)
            elif category == 'video':
                await context.bot.send_video(chat_id, telegram_file_id, caption=caption)
            elif category == 'audio':
                await context.bot.send_audio(chat_id, telegram_file_id, caption=caption)
            else:
                await context.bot.send_document(chat_id, telegram_file_id, caption=caption)
        await increment_access_count(file_data['id'])
    except Exception as e:
        await report_error(context, update, e, where="deliver_file")
        await update.message.reply_text("Couldn't deliver that content. It may have been removed on Telegram's end.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user = update.effective_user
    existing = await get_user(user.id)
    if not existing:
        # Registration failure shouldn't block the greeting — log it and
        # move on, rather than leaving the user with no reply at all.
        try:
            await add_user({
                'user_id': user.id,
                'username': user.username or "",
                'first_name': user.first_name,
                'is_admin': user.id in ADMINS,
            })
            await log_event(context, f"New user — @{esc(user.username or 'unknown')} ({user.id})")
        except Exception as e:
            await report_error(context, update, e, where="add_user")

    if context.args:
        await _deliver_file(update, context, context.args[0])
        return

    text, keyboard = start_view()
    await update.message.reply_text(text, reply_markup=keyboard, disable_web_page_preview=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = help_view()
    await update.message.reply_text(text, reply_markup=keyboard, disable_web_page_preview=True)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(script.ABOUT_TXT.format(version=BOT_VERSION), disable_web_page_preview=True)
