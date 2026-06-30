import os
import logging
from dotenv import load_dotenv
from typing import Any
import asyncio
import json
from pyrogram import Client
from pyrogram.types import Update

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from config import BOT_TOKEN, SUPABASE_URL, SUPABASE_KEY, ADMINS
from Script import script
from nomadshare_db import NomadShareDB

db = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        db = NomadShareDB(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")

app = Client(
    "nomadshare_bot",
    bot_token=BOT_TOKEN,
    in_memory=True
)

async def handle_start(message):
    """Handle /start command"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Anonymous"
        
        if db:
            try:
                user = await db.get_user(user_id)
                if not user:
                    await db.add_user({
                        'user_id': user_id,
                        'username': username,
                        'first_name': message.from_user.first_name or "User",
                        'is_admin': user_id in ADMINS
                    })
            except Exception as e:
                logger.warning(f"User registration failed: {e}")
        
        await message.reply_text(
            script.START_TXT.format(owner="@NomadShare"),
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in start handler: {e}")

async def handle_help(message):
    """Handle /help command"""
    try:
        await message.reply_text(script.HELP_TXT, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error in help handler: {e}")

async def handle_about(message):
    """Handle /about command"""
    try:
        await message.reply_text(script.ABOUT_TXT, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error in about handler: {e}")

async def handle_ping(message):
    """Handle /ping command"""
    try:
        await message.reply_text("🏓 **Pong!** Bot is alive and responding!")
    except Exception as e:
        logger.error(f"Error in ping handler: {e}")

async def handle_link(message):
    """Handle /link command"""
    try:
        if not db:
            await message.reply_text("❌ Database is not configured")
            return
        
        replied = message.reply_to_message
        if not replied or not replied.document:
            await message.reply_text("❌ Please reply to a file!")
            return
        
        file_obj = replied.document
        user_id = message.from_user.id
        
        file_data = await db.save_file({
            'file_id': file_obj.file_id,
            'file_name': file_obj.file_name,
            'file_size': file_obj.file_size,
            'file_type': file_obj.mime_type,
            'user_id': user_id,
            'is_public': True,
            'auto_delete_time': 3600
        })
        
        short_url = f"https://nomadshare.link/file/{file_data['id']}"
        
        await db.save_link(file_data['id'], short_url, file_data['id'][:8])
        
        user = await db.get_user(user_id)
        if user:
            await db.update_user(user_id, {
                'total_files': user.get('total_files', 0) + 1
            })
        
        link_msg = f"""
✅ **Link Generated Successfully!**

🔗 **URL:** `{short_url}`
📁 **File:** {file_obj.file_name}
📊 **Size:** {file_obj.file_size / (1024*1024):.2f} MB
⏰ **Expires:** 24 hours

Share this link with anyone!
"""
        await message.reply_text(link_msg)
        logger.info(f"Link generated for {file_obj.file_name}")
    except Exception as e:
        logger.error(f"Error in link handler: {e}")

async def handle_stats(message):
    """Handle /stats command"""
    try:
        if message.from_user.id not in ADMINS:
            await message.reply_text("❌ **Permission Denied!** Only admins can use this command.")
            return
        
        if not db:
            await message.reply_text("❌ Database is not configured")
            return
        
        stats = await db.get_stats()
        
        stats_text = f"""
╔════════════════════════════════╗
║      📊 NomadShare Statistics   ║
╚════════════════════════════════╝

📁 Total Files: {stats.get('total_files', 0)}
👥 Total Users: {stats.get('total_users', 0)}
🔗 Generated Links: {stats.get('total_links', 0)}

✨ Bot is running smoothly!
"""
        await message.reply_text(stats_text)
    except Exception as e:
        logger.error(f"Error in stats handler: {e}")

async def handle_broadcast(message):
    """Handle /broadcast command"""
    try:
        if message.from_user.id not in ADMINS:
            await message.reply_text("❌ **Permission Denied!** Only admins can use this command.")
            return
        
        if not db or not message.reply_to_message:
            await message.reply_text("❌ Please reply to a message to broadcast!")
            return
        
        broadcast_message = message.reply_to_message.text or message.reply_to_message.caption
        
        if not broadcast_message:
            await message.reply_text("❌ No message content to broadcast!")
            return
        
        users = await db.get_all_users()
        success = 0
        failed = 0
        
        for user in users:
            try:
                await app.send_message(user['user_id'], broadcast_message)
                success += 1
            except Exception as e:
                logger.warning(f"Failed to send to {user['user_id']}: {e}")
                failed += 1
        
        result_text = f"""
✅ **Broadcast Complete!**

✔️ Sent: {success}
❌ Failed: {failed}
📊 Total: {len(users)}
"""
        await message.reply_text(result_text)
    except Exception as e:
        logger.error(f"Error in broadcast handler: {e}")

async def handle_myfiles(message):
    """Handle /myfiles command"""
    try:
        if not db:
            await message.reply_text("❌ Database is not configured")
            return
        
        user_id = message.from_user.id
        files = await db.get_user_files(user_id)
        
        if not files:
            await message.reply_text("❌ You haven't uploaded any files yet!")
            return
        
        response = "📁 **Your Files:**\n\n"
        
        for idx, file in enumerate(files[:10], 1):
            file_type = "📄"
            if 'image' in file.get('file_type', ''):
                file_type = "🖼️"
            elif 'video' in file.get('file_type', ''):
                file_type = "🎥"
            elif 'audio' in file.get('file_type', ''):
                file_type = "🎵"
            
            size = file.get('file_size', 0) / (1024*1024)
            response += f"{idx}. {file_type} {file['file_name']}\n"
            response += f"   📊 {size:.2f} MB | 🔗 {file.get('access_count', 0)} downloads\n\n"
        
        if len(files) > 10:
            response += f"\n... and {len(files) - 10} more files"
        
        await message.reply_text(response)
    except Exception as e:
        logger.error(f"Error in myfiles handler: {e}")

async def handle_deletefile(message):
    """Handle /deletefile command"""
    try:
        if not db:
            await message.reply_text("❌ Database is not configured")
            return
        
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text("Usage: /deletefile <file_id>")
            return
        
        file_id = parts[1]
        user_id = message.from_user.id
        
        file_data = await db.get_file(file_id)
        
        if not file_data:
            await message.reply_text("❌ File not found!")
            return
        
        if file_data['uploaded_by'] != user_id and user_id not in ADMINS:
            await message.reply_text("❌ You can only delete your own files!")
            return
        
        await db.delete_file(file_id)
        await message.reply_text(f"✅ File '{file_data['file_name']}' deleted successfully!")
        logger.info(f"File {file_id} deleted by user {user_id}")
    except Exception as e:
        logger.error(f"Error in deletefile handler: {e}")

async def process_message(message):
    """Process incoming messages"""
    try:
        text = message.text or message.caption or ""
        
        if message.text and message.text.startswith("/"):
            command = message.text.split()[0][1:]
            
            handlers = {
                'start': handle_start,
                'help': handle_help,
                'about': handle_about,
                'ping': handle_ping,
                'link': handle_link,
                'stats': handle_stats,
                'broadcast': handle_broadcast,
                'myfiles': handle_myfiles,
                'deletefile': handle_deletefile,
            }
            
            if command in handlers:
                await handlers[command](message)
            else:
                await message.reply_text(f"❓ Unknown command: /{command}\n\nType /help for available commands")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

async def handle_update(update_data: dict) -> dict:
    """Handle webhook update"""
    try:
        if "message" not in update_data:
            return {"ok": True}
        
        try:
            async with app:
                update = Update(update_data)
                if update.message:
                    await process_message(update.message)
        except Exception as e:
            logger.error(f"Message processing error: {e}")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Update handling error: {e}")
        return {"ok": True}

def handler(request):
    """Vercel serverless function handler"""
    try:
        if request.method == "POST":
            try:
                update = request.get_json()
                result = asyncio.run(handle_update(update))
                return result, 200
            except Exception as e:
                logger.error(f"Request handling error: {e}")
                return {"ok": False}, 500
        elif request.method == "GET":
            return {"status": "NomadShare Bot Running"}, 200
        else:
            return {"error": "Method not allowed"}, 405
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {"error": str(e)}, 500
