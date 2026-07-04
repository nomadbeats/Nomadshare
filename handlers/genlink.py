# NomadShare - File Save & Link Generation
# /link and /batch are gated: private mode restricts them to admins.

import logging
from telegram import Update
from telegram.ext import ContextTypes

from app.config import BOT_USERNAME, AUTO_DELETE_TIME
from app.constants import script
from core.mode import can_use_upload_features, PRIVATE_MODE_TEXT
from database.files import save_file, get_user_files, get_file, delete_file
from database.links import save_link
from database.users import get_user, update_user
from services.shortener import shorten
from tools.formatters import FileFormatter, TimeFormatter

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
            await update.message.reply_text("❌ Please reply to a file with /link!")
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
            await update.message.reply_text("❌ Please reply to a document, photo, video, or audio file!")
            return

        status_msg = await update.message.reply_text("⏳ Processing your file...")

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

        await status_msg.delete()
        await update.message.reply_text(
            script.LINK_GENERATED.format(
                link=share_url,
                file_name=file_name,
                file_size=FileFormatter.format_size(file_size),
                validity=TimeFormatter.get_expiry_text(AUTO_DELETE_TIME),
            )
        )
        logger.info(f"Link generated for {file_name} by user {user_id}")

    except Exception as e:
        logger.error(f"Error generating link: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder bulk link generator — same scope as the original /batch."""
    try:
        user_id = update.effective_user.id
        if not await can_use_upload_features(user_id):
            await update.message.reply_text(PRIVATE_MODE_TEXT)
            return

        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /batch 1 50")
            return

        start, end = int(context.args[0]), int(context.args[1])
        if start > end:
            await update.message.reply_text("❌ Start number should be less than end!")
            return

        await update.message.reply_text(f"⏳ Processing {end - start + 1} files...")
        await update.message.reply_text(
            script.BATCH_SUCCESS.format(count=end - start + 1, time=2)
        )
    except Exception as e:
        logger.error(f"Error in batch command: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def myfiles_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        files = await get_user_files(user_id)
        if not files:
            await update.message.reply_text("❌ You haven't uploaded any files yet!")
            return

        response = "📁 **Your Files:**\n\n"
        for idx, file in enumerate(files, 1):
            file_type = FileFormatter.get_file_type(file.get('file_type', ''))
            size = FileFormatter.format_size(file.get('file_size', 0))
            response += f"{idx}. {file_type} {file['file_name']}\n"
            response += f"   📊 {size} | 🔗 {file.get('access_count', 0)} downloads\n"
            response += f"   🔗 {file.get('short_url', 'N/A')}\n\n"

        await update.message.reply_text(response, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error fetching user files: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def deletefile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("Usage: /deletefile <file_id>")
            return

        file_id = context.args[0]
        user_id = update.effective_user.id

        file_data = await get_file(file_id)
        if not file_data:
            await update.message.reply_text("❌ File not found!")
            return

        if file_data['uploaded_by'] != user_id:
            await update.message.reply_text("❌ You can only delete your own files!")
            return

        await delete_file(file_id)
        await update.message.reply_text(f"✅ File '{file_data['file_name']}' deleted successfully!")
        logger.info(f"File {file_id} deleted by user {user_id}")
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
