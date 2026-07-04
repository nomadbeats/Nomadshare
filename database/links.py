# NomadShare - Links Table

import logging
import uuid
from datetime import datetime
from database.client import supabase

logger = logging.getLogger(__name__)


async def save_link(file_id: str, short_url: str, short_code: str) -> dict:
    try:
        data = {
            'id': str(uuid.uuid4()),
            'file_id': file_id,
            'short_code': short_code,
            'full_url': short_url,
            'created_date': datetime.now().isoformat(),
            'access_count': 0,
            'is_active': True,
        }
        response = supabase.table('links').insert(data).execute()
        supabase.table('files').update({'short_url': short_url}).eq('id', file_id).execute()
        logger.info(f"✅ Link saved for file: {file_id}")
        return response.data[0] if response.data else data
    except Exception as e:
        logger.error(f"❌ Error saving link: {e}")
        raise


async def get_link(short_code: str):
    try:
        response = supabase.table('links').select('*').eq('short_code', short_code).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"❌ Error getting link: {e}")
        return None


async def get_link_count() -> int:
    try:
        response = supabase.table('links').select('id', count='exact').execute()
        return response.count or 0
    except Exception as e:
        logger.error(f"❌ Error counting links: {e}")
        return 0
