# NomadShare - Admin Commands

import logging
from telegram import Update
from telegram.ext import ContextTypes

from core.permissions import is_admin
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
        await update.message.reply_text(
            script.STATS_TXT.format(
                total_files=total_files,
                total_users=total_users,
                total_links=total_links,
            )
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        replied = update.message.reply_to_message
        if not replied:
            await update.message.reply_text("❌ Reply to a message to broadcast it!")
            return

        broadcast_message = replied.text or replied.caption
        if not broadcast_message:
            await update.message.reply_text("❌ No message to broadcast!")
            return

        users = await get_all_users()
        success, failed = 0, 0
        await update.message.reply_text(f"📢 Broadcasting to {len(users)} users...")

        for user in users:
            try:
                await context.bot.send_message(user['user_id'], broadcast_message)
                success += 1
            except Exception as e:
                logger.error(f"Failed to send to {user['user_id']}: {e}")
                failed += 1

        await update.message.reply_text(
            f"✅ **Broadcast Complete!**\n\n"
            f"✔️ Sent: {success}\n❌ Failed: {failed}\n📊 Total: {len(users)}"
        )
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
