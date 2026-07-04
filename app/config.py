# NomadShare - Configuration
# Only vars actually used by the webhook (python-telegram-bot) build.
# Pyrogram-only vars (API_ID/API_HASH/CLONE_MODE/STREAM_MODE/etc.) were
# dropped since they belonged to the old MTProto/polling setup.

import re
from os import environ

id_pattern = re.compile(r'^-?\d+$')


def is_enabled(value: str, default: bool) -> bool:
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    return default


# ============ Bot Information ============
BOT_TOKEN = environ.get("BOT_TOKEN", "")
BOT_USERNAME = environ.get("BOT_USERNAME", "").lower()

ADMINS = [int(a) for a in environ.get("ADMINS", "").split() if id_pattern.match(a)]

# ============ Supabase Configuration ============
SUPABASE_URL = environ.get("SUPABASE_URL", "")
SUPABASE_KEY = environ.get("SUPABASE_KEY", "")

# ============ Auto Delete Configuration ============
AUTO_DELETE_TIME = int(environ.get("AUTO_DELETE_TIME", "1800"))  # seconds

# ============ Channel Information ============
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "0") or 0)

# ============ URL Shortener Configuration ============
SHORTLINK_URL = environ.get("SHORTLINK_URL", "")
SHORTLINK_API = environ.get("SHORTLINK_API", "")

# ============ Public Base URL (for building file links) ============
# e.g. https://your-project.vercel.app
WEBSITE_URL = environ.get("WEBSITE_URL", "")

# ============ NomadShare Bot Info ============
BOT_NAME = "NomadShare"
BOT_VERSION = "2.0.0"
