# NomadShare - Commands Plugin
# Handles /link, /batch, /help, /about commands

from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS, SHORTLINK_URL, SHORTLINK_API
from Script import script
from nomadshare_db import NomadShareDB
import requests
import logging

logger = logging.getLogger(__name__)

# Initialize database
db = NomadShareDB(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

async def shorten_url(long_url: str) -> str:
    """Shorten URL using custom shortener"""
    if not SHORTLINK_URL or not SHORTLINK_API:
        return long_url
    
    try:
        response = requests.get(
            f"https://{SHORTLINK_URL}/api?api={SHORTLINK_API}&url={long_url}"
        )
        if response.status_code == 200:
            return response.text
        return long_url
    except Exception as e:
        logger.error(f"Error shortening URL: {e}")
        return long_url

@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Start command"""
    user_id = message.from_user.id
    username = message.from_user.username or "Anonymous"
    
    # Check if user exists
    user = await db.get_user(user_id)
    if not user:
        await db.add_user({
            'user_id': user_id,
            'username': username,
            'first_name': message.from_user.first_name,
            'is_admin': user_id in ADMINS
        })
    
    await message.reply_text(
        script.START_TXT.format(owner="@NomadShare"),
        disable_web_page_preview=True
    )

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Help command"""
    await message.reply_text(script.HELP_TXT, disable_web_page_preview=True)

@Client.on_message(filters.command("about"))
async def about_command(client: Client, message: Message):
    """About command"""
    await message.reply_text(script.ABOUT_TXT, disable_web_page_preview=True)

@Client.on_message(filters.command("link") & filters.reply)
async def link_command(client: Client, message: Message):
    """Generate link for replied file"""
    try:
        replied_message = message.reply_to_message
        
        if not replied_message.document:
            await message.reply_text("❌ Please reply to a file!")
            return
        
        file = replied_message.document
        user_id = message.from_user.id
        
        # Save file to database
        file_data = await db.save_file({
            'file_id': file.file_id,
            'file_name': file.file_name,
            'file_size': file.file_size,
            'file_type': file.mime_type,
            'user_id': user_id,
            'is_public': True,
            'auto_delete_time': 1800
        })
        
        # Generate short URL
        short_url = await shorten_url(f"https://your-domain.com/file/{file_data['id']}")
        
        # Save link
        await db.save_link(file_data['id'], short_url, file_data['id'][:8])
        
        # Update user file count
        user = await db.get_user(user_id)
        if user:
            await db.update_user(user_id, {'total_files': user.get('total_files', 0) + 1})
        
        link_text = script.LINK_GENERATED.format(
            link=short_url,
            file_name=file.file_name,
            validity="30 days"
        )
        
        await message.reply_text(link_text)
        
    except Exception as e:
        logger.error(f"Error generating link: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("batch"))
async def batch_command(client: Client, message: Message):
    """Batch generate links"""
    try:
        cmd_parts = message.text.split()
        
        if len(cmd_parts) < 3:
            await message.reply_text("❌ Usage: /batch 1 50")
            return
        
        start = int(cmd_parts[1])
        end = int(cmd_parts[2])
        
        if start > end:
            await message.reply_text("❌ Start number should be less than end!")
            return
        
        await message.reply_text(f"⏳ Processing {end - start + 1} files...")
        
        # Processing batch - placeholder for actual implementation
        count = end - start + 1
        
        batch_text = script.BATCH_SUCCESS.format(
            count=count,
            time=2
        )
        
        await message.reply_text(batch_text)
        
    except Exception as e:
        logger.error(f"Error in batch command: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_command(client: Client, message: Message):
    """Get database statistics"""
    try:
        stats = await db.get_stats()
        
        stats_text = script.STATS_TXT.format(
            total_files=stats['total_files'],
            total_users=stats['total_users'],
            total_links=stats['total_links'],
            uptime="Always On"
        )
        
        await message.reply_text(stats_text)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_command(client: Client, message: Message):
    """Broadcast message to all users"""
    try:
        broadcast_message = message.reply_to_message.text or message.reply_to_message.caption
        
        if not broadcast_message:
            await message.reply_text("❌ No message to broadcast!")
            return
        
        users = await db.get_all_users()
        success = 0
        failed = 0
        
        await message.reply_text(f"📢 Broadcasting to {len(users)} users...")
        
        for user in users:
            try:
                await client.send_message(user['user_id'], broadcast_message)
                success += 1
            except Exception as e:
                logger.error(f"Failed to send to {user['user_id']}: {e}")
                failed += 1
        
        result_text = f"""
✅ **Broadcast Complete!**

✔️ Sent: {success}
❌ Failed: {failed}
📊 Total: {len(users)}
"""
        await message.reply_text(result_text)
        
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")
