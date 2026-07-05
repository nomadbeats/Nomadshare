# NomadShare - File Save & Link Generation
# /link and /batch are gated: private mode restricts them to admins.

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from app.config import BOT_USERNAME, AUTO_DELETE_TIME
from app.constants import script
from core.mode import can_use_upload_features, PRIVATE_MODE_TEXT
from core.notify import report_error, log_event
from database.files import save_file, get_user_files, get_file, delete_file
from database.links import save_link
from database.users import get_user, update_user
from services.shortener import shorten
from tools.formatters import FileFormatter, TimeFormatter, esc

logger = logging.getLogger(__name__)


async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply to a file with /link to save it and generate a shareable link."""
    try:
        user_id = update.effective_user.id

        if not await can_use_upload_features(user_id):
            await update.message.reply_text(PRIVATE_MODE_TEXT)
            return

        replied = update.message.reply_to_message
        if not replied:
            await update.message.reply_text("Reply to a file with /link to generate a share link.")
            return

        if replied.document:
            f = replied.document
            file_name, file_size, mime_type, file_id, category = (
                f.file_name or "file", f.file_size, f.mime_type, f.file_id, "document",
            )
        elif replied.photo:
            p = replied.photo[-1]
            file_name, file_size, mime_type, file_id, category = (
                f"photo_{p.file_unique_id}.jpg", p.file_size, "image/jpeg", p.file_id, "photo",
            )
        elif replied.video:
            f = replied.video
            file_name, file_size, mime_type, file_id, category = (
                f.file_name or f"video_{f.file_unique_id}.mp4", f.file_size, f.mime_type or "video/mp4", f.file_id, "video",
            )
        elif replied.audio:
            f = replied.audio
            file_name, file_size, mime_type, file_id, category = (
                f.file_name or f"audio_{f.file_unique_id}.mp3", f.file_size, f.mime_type or "audio/mpeg", f.file_id, "audio",
            )
        else:
            await update.message.reply_text("That file type isn't supported yet — try a document, photo, video, or audio file.")
            return

        status_msg = await update.message.reply_text("Processing...")

        file_data = await save_file({
            'file_id': file_id,
            'file_name': file_name,
            'file_size': file_size,
            'file_type': mime_type,
            'category': category,
            'user_id': user_id,
            'auto_delete_time': AUTO_DELETE_TIME,
        })

        short_code = file_data['id'][:8]
        deep_link = f"https://t.me/{BOT_USERNAME}?start={short_code}"
        share_url = await shorten(deep_link)

        await save_link(file_data['id'], share_url, short_code)

        user = await get_user(user_id)
        if user:
            await update_user(user_id, {'total_files': user.get('total_files', 0) + 1})

        await log_event(context, f"New file — {esc(file_name)} ({FileFormatter.format_size(file_size)}) by {user_id}")

        await status_msg.delete()
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Open link", url=share_url)]])
        await update.message.reply_text(
            script.LINK_GENERATED.format(
                link=esc(share_url),
                file_name=esc(file_name),
                file_size=FileFormatter.format_size(file_size),
                validity=TimeFormatter.get_expiry_text(AUTO_DELETE_TIME),
            ),
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
        logger.info(f"Link generated for {file_name} by user {user_id}")

    except Exception as e:
        await report_error(context, update, e, where="link_command")
        await update.message.reply_text("Couldn't generate a link for that file. Please try again.")


async def batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder bulk link generator — same scope as the original /batch."""
    try:
        user_id = update.effective_user.id
        if not await can_use_upload_features(user_id):
            await update.message.reply_text(PRIVATE_MODE_TEXT)
            return

        if len(context.args) < 2:
            await update.message.reply_text("Usage: /batch 1 50")
            return

        start, end = int(context.args[0]), int(context.args[1])
        if start > end:
            await update.message.reply_text("The start number should be less than the end number.")
            return

        await update.message.reply_text(f"Processing {end - start + 1} files...")
        await update.message.reply_text(script.BATCH_SUCCESS.format(count=end - start + 1, time=2))
    except Exception as e:
        await report_error(context, update, e, where="batch_command")
        await update.message.reply_text("Batch processing failed. Please try again.")


async def myfiles_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        files = await get_user_files(user_id)
        if not files:
            await update.message.reply_text("You haven't saved any files yet. Reply to a file with /link to get started.")
            return

        lines = ["<b>Your files</b>", ""]
        buttons = []
        for idx, file in enumerate(files[:20], 1):
            size = FileFormatter.format_size(file.get('file_size', 0))
            lines.append(f"{idx}. {esc(file['file_name'])} — {size} — {file.get('access_count', 0)} views")
            buttons.append([InlineKeyboardButton(f"Delete {idx}", callback_data=f"delete:{file['id']}")])

        await update.message.reply_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await report_error(context, update, e, where="myfiles_command")
        await update.message.reply_text("Couldn't load your files. Please try again.")


async def deletefile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("Usage: /deletefile <id> — or use the Delete button under /myfiles.")
            return

        file_id = context.args[0]
        user_id = update.effective_user.id

        file_data = await get_file(file_id)
        if not file_data:
            await update.message.reply_text("File not found.")
            return

        if file_data['uploaded_by'] != user_id:
            await update.message.reply_text("You can only delete your own files.")
            return

        await delete_file(file_id)
        await update.message.reply_text(f"{esc(file_data['file_name'])} has been deleted.")
    except Exception as e:
        await report_error(context, update, e, where="deletefile_command")
        await update.message.reply_text("Couldn't delete that file. Please try again.")
