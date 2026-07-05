# NomadShare - Mode Command (admin-only)

import logging
from telegram import Update
from telegram.ext import ContextTypes

from core.permissions import is_admin
from core.mode import get_mode, set_mode
from core.views import mode_view
from core.notify import report_error

logger = logging.getLogger(__name__)


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/mode shows buttons to toggle; /mode public|private sets it directly."""
    if not is_admin(update.effective_user.id):
        return  # silently ignore non-admins

    try:
        if not context.args:
            current = await get_mode()
            text, keyboard = mode_view(current)
            await update.message.reply_text(text, reply_markup=keyboard)
            return

        new_mode = context.args[0].lower()
        if new_mode not in ("public", "private"):
            await update.message.reply_text("Usage: /mode public or /mode private")
            return

        ok = await set_mode(new_mode)
        if ok:
            text, keyboard = mode_view(new_mode)
            await update.message.reply_text(text, reply_markup=keyboard)
        else:
            await update.message.reply_text("Couldn't update the mode — check that bot_settings exists in Supabase.")
    except Exception as e:
        await report_error(context, update, e, where="mode_command")
        await update.message.reply_text("Something went wrong updating the mode.")
