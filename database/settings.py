# NomadShare - Settings Table
# Simple key/value store, currently used for the public/private mode.

import logging
from database.client import supabase

logger = logging.getLogger(__name__)


async def get_setting(key: str, default=None):
    try:
        response = supabase.table('bot_settings').select('*').eq('key', key).execute()
        if response.data:
            return response.data[0]['value']
        return default
    except Exception as e:
        logger.error(f"❌ Error getting setting '{key}': {e}")
        return default


async def set_setting(key: str, value: str) -> bool:
    try:
        supabase.table('bot_settings').upsert({'key': key, 'value': value}).execute()
        logger.info(f"✅ Setting updated: {key} = {value}")
        return True
    except Exception as e:
        logger.error(f"❌ Error setting '{key}': {e}")
        return False
