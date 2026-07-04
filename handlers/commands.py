# NomadShare - Core Commands
# /start also handles deep links: https://t.me/<bot>?start=<short_code>
# This is what actually delivers a file back to a viewer who opens a
# shared link — the old app.py only returned JSON, it never sent the file.

import logging
from telegram import Update
from telegram.ext import ContextTypes

from app.config import ADMINS, BOT_USERNAME
from app.constants import script
from database.users import get_user, add_user
from database.links import get_link
from database.files import get_file, increment_access_count

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
    telegram_file_id = file_data['file_id']
    category = file_data.get('category', 'document')
    caption = f"{file_data.get('file_name', '')}\n\n{script.CAPTION}"

    try:
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
        logger.error(f"Error delivering file: {e}")
        await update.message.reply_text(f"❌ Couldn't deliver that file: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user = update.effective_user
    existing = await get_user(user.id)
    if not existing:
        await add_user({
            'user_id': user.id,
            'username': user.username or "Anonymous",
            'first_name': user.first_name,
            'is_admin': user.id in ADMINS,
        })

    if context.args:
        await _deliver_file(update, context, context.args[0])
        return

    await update.message.reply_text(
        script.START_TXT.format(owner=f"@{BOT_USERNAME}" if BOT_USERNAME else "Admin"),
        disable_web_page_preview=True,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(script.HELP_TXT, disable_web_page_preview=True)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(script.ABOUT_TXT, disable_web_page_preview=True)
