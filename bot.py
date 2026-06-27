# NomadShare - Permanent File Store Bot
# Main Bot Entry Point

import sys
import glob
import importlib
from pathlib import Path
from pyrogram import idle
import logging
import logging.config

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import LOG_CHANNEL, ON_HEROKU, CLONE_MODE, PORT
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script 
from datetime import date, datetime 
import pytz
from aiohttp import web

import asyncio
from pyrogram import idle
from TechVJ.bot import StreamBot
from TechVJ.utils.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)
StreamBot.start()
loop = asyncio.get_event_loop()

async def start():
    print('\n')
    print('╔════════════════════════════════════╗')
    print('║  🚀 Initializing NomadShare Bot 🚀  ║')
    print('╚════════════════════════════════════╝')
    
    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username
    await initialize_clients()
    
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print(f"✅ NomadShare Loaded => {plugin_name}")
    
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    
    me = await StreamBot.get_me()
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    
    print('╔════════════════════════════════════╗')
    print('║   ✅ NomadShare Bot Started ✅    ║')
    print('╚════════════════════════════════════╝')
    print(f"Bot: @{me.username}")
    print(f"Time: {time}")
    
    if LOG_CHANNEL:
        await StreamBot.send_message(
            chat_id=LOG_CHANNEL, 
            text=f"✅ **NomadShare Bot Started!**\n\n📅 {today}\n⏰ {time}\n👤 @{me.username}"
        )
    
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('🛑 NomadShare Service Stopped Bye 👋')
