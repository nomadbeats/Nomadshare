# NomadShare - Admin Commands

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.permissions import is_admin
from core.notify import report_error, log_event
from app.constants import script
from database.files import get_file_count
from database.users import get_user_count, get_all_users
from database.links import get_link_count

logger = logging.getLogger(__name__)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        total_files = await get_file_count()
        total_users = await get_user_count()
        total_links = await get_link_count()
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="stats_refresh")]])
        await update.message.reply_text(
            script.STATS_TXT.format(
                total_files=total_files, total_users=total_users, total_links=total_links
            ),
            reply_markup=keyboard,
        )
    except Exception as e:
        await report_error(context, update, e, where="stats_command")
        await update.message.reply_text("Couldn't load statistics.")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        replied = update.message.reply_to_message
        if not replied:
            await update.message.reply_text("Reply to a message with /broadcast to send it to all users.")
            return

        broadcast_message = replied.text or replied.caption
        if not broadcast_message:
            await update.message.reply_text("That message has no text to broadcast.")
            return

        users = await get_all_users()
        success, failed = 0, 0
        status = await update.message.reply_text(f"Broadcasting to {len(users)} users...")

        for user in users:
            try:
                # Sent as plain text (parse_mode=None) regardless of the bot's
                # HTML default — this is the admin's own freeform message, so
                # any <, >, or & they typed should go out exactly as written
                # rather than being treated as markup.
                await context.bot.send_message(user['user_id'], broadcast_message, parse_mode=None)
                success += 1
            except Exception as e:
                logger.error(f"Failed to send to {user['user_id']}: {e}")
                failed += 1

        await status.edit_text(
            f"Broadcast complete.\n\nDelivered: {success}\nFailed: {failed}\nTotal: {len(users)}"
        )
        await log_event(context, f"Broadcast by {update.effective_user.id} — delivered {success}, failed {failed}")
    except Exception as e:
        await report_error(context, update, e, where="broadcast_command")
        await update.message.reply_text("Broadcast failed. Please try again.")
