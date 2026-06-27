# NomadShare - Permanent File Store Bot
# Configuration File

import re
import os
from os import environ
from Script import script

id_pattern = re.compile(r'^.\d+$')

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# ============ Bot Information ============
API_ID = int(environ.get("API_ID", ""))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

PICS = (environ.get('PICS', 'https://graph.org/file/ce1723991756e48c35aa1.jpg')).split()
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]
BOT_USERNAME = environ.get("BOT_USERNAME", "")
PORT = environ.get("PORT", "8080")

# ============ Supabase Configuration ============
SUPABASE_URL = environ.get("SUPABASE_URL", "")
SUPABASE_KEY = environ.get("SUPABASE_KEY", "")

# ============ Clone Mode ============
CLONE_MODE = bool(environ.get('CLONE_MODE', False))
CLONE_SUPABASE_URL = environ.get("CLONE_SUPABASE_URL", "")
CLONE_SUPABASE_KEY = environ.get("CLONE_SUPABASE_KEY", "")

# ============ Auto Delete Configuration ============
AUTO_DELETE_MODE = bool(environ.get('AUTO_DELETE_MODE', True))
AUTO_DELETE = int(environ.get("AUTO_DELETE", "30"))  # Time in Minutes
AUTO_DELETE_TIME = int(environ.get("AUTO_DELETE_TIME", "1800"))  # Time in Seconds

# ============ Channel Information ============
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", ""))

# ============ File Caption Configuration ============
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)

# ============ Public File Store ============
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "True")), True)

# ============ URL Shortener Configuration ============
VERIFY_MODE = bool(environ.get('VERIFY_MODE', False))
SHORTLINK_URL = environ.get("SHORTLINK_URL", "")
SHORTLINK_API = environ.get("SHORTLINK_API", "")
VERIFY_TUTORIAL = environ.get("VERIFY_TUTORIAL", "")

# ============ Website URL Mode ============
WEBSITE_URL_MODE = bool(environ.get('WEBSITE_URL_MODE', False))
WEBSITE_URL = environ.get("WEBSITE_URL", "")

# ============ Stream Configuration ============
STREAM_MODE = bool(environ.get('STREAM_MODE', True))
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))

if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False

URL = environ.get("URL", "https://nomadshare-bot.herokuapp.com/")

# ============ NomadShare Bot Configuration ============
BOT_NAME = "NomadShare"
BOT_VERSION = "1.0.0"
