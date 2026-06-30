import os
from os import environ

BOT_TOKEN = environ.get("BOT_TOKEN", "")
BOT_USERNAME = environ.get("BOT_USERNAME", "").lstrip("@")
SUPABASE_URL = environ.get("SUPABASE_URL", "")
SUPABASE_KEY = environ.get("SUPABASE_KEY", "")

ADMINS = []
if environ.get("ADMINS"):
    try:
        ADMINS = [int(x.strip()) for x in environ.get("ADMINS", "").split() if x.strip().isdigit()]
    except:
        ADMINS = []

LOG_CHANNEL = None
if environ.get("LOG_CHANNEL"):
    try:
        LOG_CHANNEL = int(environ.get("LOG_CHANNEL"))
    except:
        LOG_CHANNEL = None

WEBHOOK_URL = environ.get("WEBHOOK_URL", "")
VERCEL_URL = environ.get("VERCEL_URL", "")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required!")

AUTO_DELETE_HOURS = int(environ.get("AUTO_DELETE_HOURS", "24"))
AUTO_DELETE_SECONDS = AUTO_DELETE_HOURS * 3600

ENABLE_DATABASE = bool(SUPABASE_URL and SUPABASE_KEY)

BOT_NAME = "NomadShare"
BOT_VERSION = "1.0.0"
