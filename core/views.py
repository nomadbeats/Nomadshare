# NomadShare - View Builders
# One place that builds (text, keyboard) pairs, reused by both the
# command handlers and the callback router so start/help/mode always
# render identically whether reached by command or by button.

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.config import COMMUNITY_CHANNEL, UPDATES_CHANNEL
from app.constants import script


def start_view():
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Community", url=f"https://t.me/{COMMUNITY_CHANNEL}"),
            InlineKeyboardButton("Updates", url=f"https://t.me/{UPDATES_CHANNEL}"),
        ],
        [InlineKeyboardButton("Commands", callback_data="show_help")],
    ])
    return script.START_TXT, keyboard


def help_view():
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="show_start")]])
    return script.HELP_TXT, keyboard


def mode_view(current: str):
    private_label = "Private (current)" if current == "private" else "Private"
    public_label = "Public (current)" if current == "public" else "Public"
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(private_label, callback_data="mode_set:private"),
        InlineKeyboardButton(public_label, callback_data="mode_set:public"),
    ]])
    text = script.MODE_TXT.format(current=current.capitalize())
    return text, keyboard
