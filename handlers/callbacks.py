# NomadShare - Callback Query Router
# Every inline button in the bot funnels through here, dispatched on
# the callback_data prefix. Each branch re-checks permissions itself —
# a message with buttons can sit in a chat for a while, so we don't
# trust that "this button exists" means "this tap is authorized."

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.permissions import is_admin
from core.mode import set_mode
from core.views import start_view, help_view, mode_view
from core.notify import report_error
from database.files import get_file, delete_file, get_file_count
from database.users import get_user_count
from database.links import get_link_count
from app.constants import script
from tools.formatters import esc

logger = logging.getLogger(__name__)


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""

    try:
        if data == "show_start":
            await query.answer()
            text, keyboard = start_view()
            await query.edit_message_text(text, reply_markup=keyboard, disable_web_page_preview=True)
            return

        if data == "show_help":
            await query.answer()
            text, keyboard = help_view()
            await query.edit_message_text(text, reply_markup=keyboard, disable_web_page_preview=True)
            return

        if data.startswith("mode_set:"):
            if not is_admin(query.from_user.id):
                await query.answer("Admins only.", show_alert=True)
                return
            new_mode = data.split(":", 1)[1]
            await set_mode(new_mode)
            await query.answer(f"Mode set to {new_mode}.")
            text, keyboard = mode_view(new_mode)
            await query.edit_message_text(text, reply_markup=keyboard)
            return

        if data.startswith("delete:"):
            file_id = data.split(":", 1)[1]
            file_data = await get_file(file_id)
            if not file_data:
                await query.answer("File not found.", show_alert=True)
                return
            if file_data['uploaded_by'] != query.from_user.id and not is_admin(query.from_user.id):
                await query.answer("You can only delete your own files.", show_alert=True)
                return
            await query.answer()
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("Confirm", callback_data=f"confirm_delete:{file_id}"),
                InlineKeyboardButton("Cancel", callback_data=f"cancel_delete:{file_id}"),
            ]])
            await query.edit_message_text(
                f"Delete {esc(file_data['file_name'])}? This can't be undone.",
                reply_markup=keyboard,
            )
            return

        if data.startswith("confirm_delete:"):
            file_id = data.split(":", 1)[1]
            file_data = await get_file(file_id)
            if not file_data:
                await query.answer("Already deleted.", show_alert=True)
                return
            if file_data['uploaded_by'] != query.from_user.id and not is_admin(query.from_user.id):
                await query.answer("You can only delete your own files.", show_alert=True)
                return
            await delete_file(file_id)
            await query.answer("Deleted.")
            await query.edit_message_text(f"{esc(file_data['file_name'])} has been deleted.")
            return

        if data.startswith("cancel_delete:"):
            await query.answer("Cancelled.")
            await query.edit_message_text("Deletion cancelled.")
            return

        if data == "stats_refresh":
            total_files = await get_file_count()
            total_users = await get_user_count()
            total_links = await get_link_count()
            await query.answer("Refreshed.")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="stats_refresh")]])
            await query.edit_message_text(
                script.STATS_TXT.format(
                    total_files=total_files, total_users=total_users, total_links=total_links
                ),
                reply_markup=keyboard,
            )
            return

        await query.answer()

    except Exception as e:
        await report_error(context, update, e, where=f"callback:{data}")
        try:
            await query.answer("Something went wrong.", show_alert=True)
        except Exception:
            pass
