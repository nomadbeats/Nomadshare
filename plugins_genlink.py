# NomadShare - Generate Link Plugin
# Handle link generation and shortening

from pyrogram import Client, filters
from pyrogram.types import Message
import os
from nomadshare_db import NomadShareDB
from utils import URLShortener, FileFormatter, TimeFormatter
from config import SUPABASE_URL, SUPABASE_KEY, AUTO_DELETE_TIME
from Script import script
import logging

logger = logging.getLogger(__name__)

db = NomadShareDB(SUPABASE_URL, SUPABASE_KEY)

@Client.on_message(filters.command("link") & filters.reply)
async def generate_link(client: Client, message: Message):
    """Generate shareable link for file"""
    try:
        replied = message.reply_to_message
        user_id = message.from_user.id
        
        # Check if replied message has a file
        if not (replied.document or replied.photo or replied.video or replied.audio):
            await message.reply_text("❌ Please reply to a file/media!")
            return
        
        # Get file information
        if replied.document:
            file_obj = replied.document
            file_name = file_obj.file_name or "file"
            file_size = file_obj.file_size
            mime_type = file_obj.mime_type
            file_id = replied.document.file_id
        elif replied.photo:
            file_obj = replied.photo
            file_name = f"photo_{file_obj.file_unique_id}.jpg"
            file_size = file_obj.file_size
            mime_type = "image/jpeg"
            file_id = replied.photo.file_id
        elif replied.video:
            file_obj = replied.video
            file_name = file_obj.file_name or f"video_{file_obj.file_unique_id}.mp4"
            file_size = file_obj.file_size
            mime_type = file_obj.mime_type
            file_id = replied.video.file_id
        elif replied.audio:
            file_obj = replied.audio
            file_name = file_obj.file_name or f"audio_{file_obj.file_unique_id}.mp3"
            file_size = file_obj.file_size
            mime_type = file_obj.mime_type
            file_id = replied.audio.file_id
        else:
            await message.reply_text("❌ Unsupported file type!")
            return
        
        # Processing message
        status_msg = await message.reply_text("⏳ Processing your file...")
        
        # Save to database
        file_data = await db.save_file({
            'file_id': file_id,
            'file_name': file_name,
            'file_size': file_size,
            'file_type': mime_type,
            'user_id': user_id,
            'is_public': True,
            'auto_delete_time': AUTO_DELETE_TIME
        })
        
        # Generate shortened URL
        long_url = f"https://your-domain.com/file/{file_data['id']}"
        short_url = await URLShortener.shorten(long_url)
        short_code = file_data['id'][:8]
        
        # Save link
        await db.save_link(file_data['id'], short_url, short_code)
        
        # Update user stats
        user = await db.get_user(user_id)
        if user:
            await db.update_user(user_id, {
                'total_files': user.get('total_files', 0) + 1
            })
        
        # Format response
        file_type_emoji = FileFormatter.get_file_type(mime_type)
        file_size_text = FileFormatter.format_size(file_size)
        
        response_text = f"""
✅ **Link Generated Successfully!**

🔗 **Shortened URL:** `{short_url}`
📁 **File:** {file_type_emoji} {file_name}
📊 **Size:** {file_size_text}
⏰ **Valid for:** {TimeFormatter.get_expiry_text(AUTO_DELETE_TIME)}

👥 **Share with:** Anyone!
🔄 **Auto-delete:** Enabled

Click the link to download!
"""
        
        await status_msg.delete()
        await message.reply_text(response_text)
        
        logger.info(f"Link generated for {file_name} by user {user_id}")
        
    except Exception as e:
        logger.error(f"Error generating link: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("myfiles"))
async def my_files(client: Client, message: Message):
    """Show user's uploaded files"""
    try:
        user_id = message.from_user.id
        
        files = await db.get_user_files(user_id)
        
        if not files:
            await message.reply_text("❌ You haven't uploaded any files yet!")
            return
        
        response = "📁 **Your Files:**\n\n"
        
        for idx, file in enumerate(files, 1):
            file_type = FileFormatter.get_file_type(file.get('file_type', ''))
            size = FileFormatter.format_size(file.get('file_size', 0))
            
            response += f"{idx}. {file_type} {file['file_name']}\n"
            response += f"   📊 {size} | 🔗 {file.get('access_count', 0)} downloads\n"
            response += f"   🔗 `{file.get('short_url', 'N/A')}`\n\n"
        
        await message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error fetching user files: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("deletefile"))
async def delete_file(client: Client, message: Message):
    """Delete a file"""
    try:
        if len(message.text.split()) < 2:
            await message.reply_text("Usage: /deletefile <file_id>")
            return
        
        file_id = message.text.split()[1]
        user_id = message.from_user.id
        
        file_data = await db.get_file(file_id)
        
        if not file_data:
            await message.reply_text("❌ File not found!")
            return
        
        if file_data['uploaded_by'] != user_id:
            await message.reply_text("❌ You can only delete your own files!")
            return
        
        await db.delete_file(file_id)
        
        await message.reply_text(f"✅ File '{file_data['file_name']}' deleted successfully!")
        logger.info(f"File {file_id} deleted by user {user_id}")
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")
