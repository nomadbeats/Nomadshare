# NomadShare - Error Reporting & Log Channel
# Two jobs: (1) give the user a clean message instead of silence when
# something breaks, (2) put the actual details in LOG_CHANNEL so Jack
# doesn't have to go digging through Vercel logs to find out why.

import html
import logging
import traceback

from telegram import Update

from app.config import LOG_CHANNEL

logger = logging.getLogger(__name__)

GENERIC_ERROR_TEXT = "Something went wrong processing that. Please try again in a moment."


async def log_event(context, text: str) -> None:
    """Post a one-line event to the log channel. Never raises — a failed
    log post should never take down the actual command."""
    if not LOG_CHANNEL:
        return
    try:
        await context.bot.send_message(chat_id=LOG_CHANNEL, text=text)
    except Exception as e:
        logger.error(f"Failed to post event to log channel: {e}")


async def report_error(context, update, error: Exception, where: str = "") -> None:
    """Log an error server-side and forward the traceback to LOG_CHANNEL."""
    logger.error(f"Error in {where}: {error}", exc_info=error)

    if not LOG_CHANNEL:
        return

    try:
        lines = [f"<b>Error — {html.escape(where or 'unknown')}</b>"]
        if update is not None and getattr(update, "effective_user", None):
            u = update.effective_user
            lines.append(f"User: {u.id} (@{html.escape(u.username or 'unknown')})")
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        lines.append(f"<pre>{html.escape(tb[-3000:])}</pre>")
        await context.bot.send_message(
            chat_id=LOG_CHANNEL,
            text="\n".join(lines),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Failed to post error to log channel: {e}")


async def global_error_handler(update, context) -> None:
    """Registered via Application.add_error_handler — the backstop for
    anything an individual handler's own try/except didn't catch."""
    upd = update if isinstance(update, Update) else None

    await report_error(context, upd, context.error, where="unhandled")

    if upd is not None and upd.effective_message:
        try:
            await upd.effective_message.reply_text(GENERIC_ERROR_TEXT)
        except Exception:
            pass
