# NomadShare - Users Table

import logging
from datetime import datetime
from database.client import supabase

logger = logging.getLogger(__name__)


async def get_user(user_id: int):
    try:
        response = supabase.table('users').select('*').eq('user_id', user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"❌ Error getting user: {e}")
        return None


async def add_user(user_data: dict) -> dict:
    try:
        data = {
            'user_id': user_data.get('user_id'),
            'username': user_data.get('username'),
            'first_name': user_data.get('first_name'),
            'is_admin': user_data.get('is_admin', False),
            'is_verified': False,
            'joined_date': datetime.now().isoformat(),
            'total_files': 0,
        }
        response = supabase.table('users').insert(data).execute()
        logger.info(f"✅ User added: {user_data.get('username')}")
        return response.data[0] if response.data else data
    except Exception as e:
        logger.error(f"❌ Error adding user: {e}")
        raise


async def update_user(user_id: int, update_data: dict) -> bool:
    try:
        supabase.table('users').update(update_data).eq('user_id', user_id).execute()
        return True
    except Exception as e:
        logger.error(f"❌ Error updating user: {e}")
        return False


async def get_all_users() -> list:
    try:
        response = supabase.table('users').select('*').execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"❌ Error getting users: {e}")
        return []


async def get_user_count() -> int:
    try:
        response = supabase.table('users').select('user_id', count='exact').execute()
        return response.count or 0
    except Exception as e:
        logger.error(f"❌ Error counting users: {e}")
        return 0
