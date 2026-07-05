import logging

from fastapi import FastAPI, Request
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, Defaults, filters

from app.config import BOT_TOKEN, BOT_USERNAME
from handlers.commands import start_command, help_command, about_command
from handlers.genlink import link_command, batch_command, myfiles_command, deletefile_command
from handlers.mode import mode_command
from handlers.admin import stats_command, broadcast_command
from handlers.callbacks import callback_router
from core.notify import global_error_handler
from database.files import get_file, cleanup_expired_files
from database.links import get_link

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# HTML, not Markdown: Markdown's escaping is context-sensitive and breaks on
# ordinary file names (an unescaped "_" or "*" is enough to throw a
# "can't parse entities" error from Telegram). HTML only needs <, >, & escaped,
# which tools.formatters.esc() handles for every dynamic value in these messages.
defaults = Defaults(parse_mode=ParseMode.HTML)
telegram_app = Application.builder().token(BOT_TOKEN).defaults(defaults).build()

telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CommandHandler("about", about_command))
telegram_app.add_handler(CommandHandler("link", link_command, filters=filters.REPLY))
telegram_app.add_handler(CommandHandler("batch", batch_command))
telegram_app.add_handler(CommandHandler("myfiles", myfiles_command))
telegram_app.add_handler(CommandHandler("deletefile", deletefile_command))
telegram_app.add_handler(CommandHandler("mode", mode_command))
telegram_app.add_handler(CommandHandler("stats", stats_command))
telegram_app.add_handler(CommandHandler("broadcast", broadcast_command, filters=filters.REPLY))
telegram_app.add_handler(CallbackQueryHandler(callback_router))
telegram_app.add_error_handler(global_error_handler)


@app.on_event("startup")
async def startup():
    await telegram_app.initialize()


@app.get("/")
async def root():
    return {"status": "running"}


@app.post("/")
async def webhook(request: Request):
    data = await request.json()

    update = Update.de_json(data, telegram_app.bot)

    message = update.message

    if message and message.chat.type in ["group", "supergroup"]:

        is_mention = False
        is_reply = False

        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mention = message.text[
                        entity.offset:
                        entity.offset + entity.length
                    ].lower()

                    if mention == f"@{BOT_USERNAME}":
                        is_mention = True
                        break

        if (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.username
        ):
            is_reply = (
                message.reply_to_message.from_user.username.lower()
                == BOT_USERNAME
            )

        if not (is_mention or is_reply):
            return {"ok": True}

    await telegram_app.process_update(update)

    return {"ok": True}


# ---- Optional JSON metadata endpoints (info only — the bot itself delivers
# the actual file via /start deep link, see handlers/commands.py) ----

@app.get("/file/{file_id}")
async def file_info(file_id: str):
    file_data = await get_file(file_id)
    if not file_data:
        return {"error": "File not found"}
    return {
        "file_id": file_data["id"],
        "file_name": file_data["file_name"],
        "file_size": file_data["file_size"],
        "uploaded_by": file_data["uploaded_by"],
        "upload_date": file_data["upload_date"],
        "access_count": file_data["access_count"],
    }


@app.get("/link/{short_code}")
async def link_info(short_code: str):
    link_data = await get_link(short_code)
    if not link_data:
        return {"error": "Link not found"}
    return {
        "short_code": link_data["short_code"],
        "full_url": link_data["full_url"],
        "is_active": link_data["is_active"],
        "bot": f"@{BOT_USERNAME}",
    }


@app.get("/cleanup")
async def cleanup():
    """Point a Vercel Cron Job here on a schedule to purge expired files."""
    deleted = await cleanup_expired_files()
    return {"deleted": deleted}
