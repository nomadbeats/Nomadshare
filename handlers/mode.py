# NomadShare - Mode Command (admin-only)

import logging
from telegram import Update
from telegram.ext import ContextTypes

from core.permissions import is_admin
from core.mode import get_mode, set_mode

logger = logging.getLogger(__name__)


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View or change bot mode. Usage: /mode | /mode public | /mode private"""
    if not is_admin(update.effective_user.id):
        return  # silently ignore non-admins

    if not context.args:
        current = await get_mode()
        await update.message.reply_text(
            f"⚙️ **Current Mode:** `{current.upper()}`\n\n"
            "**Usage:**\n"
            "`/mode public` — anyone can save files & generate links\n"
            "`/mode private` — only admin can (default)"
        )
        return

    new_mode = context.args[0].lower()
    if new_mode not in ("public", "private"):
        await update.message.reply_text("❌ Invalid mode. Use `/mode public` or `/mode private`.")
        return

    ok = await set_mode(new_mode)
    if ok:
        emoji = "🌍" if new_mode == "public" else "🔒"
        await update.message.reply_text(f"{emoji} Bot mode set to **{new_mode.upper()}**.")
        logger.info(f"Bot mode changed to {new_mode} by {update.effective_user.id}")
    else:
        await update.message.reply_text(
            "❌ Failed to update mode — check that the `bot_settings` table exists in Supabase."
        )
