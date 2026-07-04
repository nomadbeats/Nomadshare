# NomadShare - Files Table

import logging
import uuid
from datetime import datetime, timedelta
from database.client import supabase

logger = logging.getLogger(__name__)


def _calculate_expiry(auto_delete_seconds):
    if auto_delete_seconds:
        return (datetime.now() + timedelta(seconds=auto_delete_seconds)).isoformat()
    return None


async def save_file(file_data: dict) -> dict:
    """
    file_data expects: file_id (telegram), file_name, file_size, file_type (mime),
    category ('document'|'photo'|'video'|'audio' - which bot.send_* to use on
    delivery), user_id, auto_delete_time (seconds, optional).
    """
    try:
        record_id = str(uuid.uuid4())
        data = {
            'id': record_id,
            'file_id': file_data.get('file_id'),
            'file_name': file_data.get('file_name'),
            'file_size': file_data.get('file_size'),
            'file_type': file_data.get('file_type'),
            'category': file_data.get('category', 'document'),
            'uploaded_by': file_data.get('user_id'),
            'upload_date': datetime.now().isoformat(),
            'expiry_date': _calculate_expiry(file_data.get('auto_delete_time')),
            'access_count': 0,
            'is_public': file_data.get('is_public', True),
            'short_url': None,
        }
        response = supabase.table('files').insert(data).execute()
        logger.info(f"✅ File saved: {data['file_name']}")
        return response.data[0] if response.data else data
    except Exception as e:
        logger.error(f"❌ Error saving file: {e}")
        raise


async def get_file(file_id: str):
    try:
        response = supabase.table('files').select('*').eq('id', file_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"❌ Error getting file: {e}")
        return None


async def delete_file(file_id: str) -> bool:
    try:
        supabase.table('files').delete().eq('id', file_id).execute()
        logger.info(f"✅ File deleted: {file_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Error deleting file: {e}")
        return False


async def increment_access_count(file_id: str) -> bool:
    try:
        file_data = await get_file(file_id)
        if file_data:
            new_count = file_data.get('access_count', 0) + 1
            supabase.table('files').update({'access_count': new_count}).eq('id', file_id).execute()
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Error incrementing access: {e}")
        return False


async def get_user_files(user_id: int) -> list:
    try:
        response = supabase.table('files').select('*').eq('uploaded_by', user_id).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"❌ Error getting user files: {e}")
        return []


async def get_file_count() -> int:
    try:
        response = supabase.table('files').select('id', count='exact').execute()
        return response.count or 0
    except Exception as e:
        logger.error(f"❌ Error counting files: {e}")
        return 0


async def cleanup_expired_files() -> int:
    """Delete files past their expiry_date. Call this from a Vercel Cron hitting /cleanup."""
    try:
        expired = supabase.table('files').select('*').lt('expiry_date', datetime.now().isoformat()).execute()
        deleted = 0
        for f in expired.data or []:
            await delete_file(f['id'])
            deleted += 1
        logger.info(f"✅ Cleaned up {deleted} expired files")
        return deleted
    except Exception as e:
        logger.error(f"❌ Error cleaning up files: {e}")
        return 0
