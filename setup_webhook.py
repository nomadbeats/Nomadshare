import asyncio
import logging
import sys
from dotenv import load_dotenv
from pyrogram import Client
from config import BOT_TOKEN, WEBHOOK_URL

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_webhook():
    """Set up webhook for Telegram bot"""
    try:
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN not set!")
            sys.exit(1)
        
        if not WEBHOOK_URL:
            logger.error("❌ WEBHOOK_URL not set!")
            sys.exit(1)
        
        app = Client("nomadshare_setup", bot_token=BOT_TOKEN, in_memory=True)
        
        async with app:
            logger.info(f"Setting webhook to: {WEBHOOK_URL}")
            
            await app.set_webhook(WEBHOOK_URL)
            
            webhook_info = await app.get_webhook_info()
            logger.info(f"✅ Webhook set successfully!")
            logger.info(f"Webhook URL: {webhook_info.url if webhook_info else 'Not set'}")
            
            return True
    
    except Exception as e:
        logger.error(f"❌ Error setting webhook: {e}")
        return False

async def delete_webhook():
    """Delete webhook"""
    try:
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN not set!")
            sys.exit(1)
        
        app = Client("nomadshare_setup", bot_token=BOT_TOKEN, in_memory=True)
        
        async with app:
            logger.info("Deleting webhook...")
            await app.delete_webhook()
            logger.info("✅ Webhook deleted!")
            return True
    
    except Exception as e:
        logger.error(f"❌ Error deleting webhook: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "delete":
        asyncio.run(delete_webhook())
    else:
        success = asyncio.run(setup_webhook())
        sys.exit(0 if success else 1)
