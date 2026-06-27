# NomadShare - Supabase Database Module
# Database operations for Supabase

import os
from supabase import create_client, Client
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

class NomadShareDB:
    """
    Supabase database handler for NomadShare bot
    """
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client"""
        try:
            self.client: Client = create_client(supabase_url, supabase_key)
            self.url = supabase_url
            self.key = supabase_key
            logger.info("✅ Supabase connected successfully")
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")
            raise

    # ============ FILE OPERATIONS ============
    
    async def save_file(self, file_data: dict) -> dict:
        """Save file metadata to database"""
        try:
            file_id = str(uuid.uuid4())
            data = {
                'id': file_id,
                'file_id': file_data.get('file_id'),
                'file_name': file_data.get('file_name'),
                'file_size': file_data.get('file_size'),
                'file_type': file_data.get('file_type'),
                'uploaded_by': file_data.get('user_id'),
                'upload_date': datetime.now().isoformat(),
                'expiry_date': self._calculate_expiry(file_data.get('auto_delete_time')),
                'access_count': 0,
                'is_public': file_data.get('is_public', True),
                'short_url': None
            }
            
            response = self.client.table('files').insert(data).execute()
            logger.info(f"✅ File saved: {file_data.get('file_name')}")
            return response.data[0] if response.data else data
        except Exception as e:
            logger.error(f"❌ Error saving file: {e}")
            raise

    async def get_file(self, file_id: str) -> dict:
        """Get file metadata"""
        try:
            response = self.client.table('files').select('*').eq('id', file_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Error getting file: {e}")
            return None

    async def get_file_by_telegram_id(self, telegram_file_id: str) -> dict:
        """Get file by Telegram file_id"""
        try:
            response = self.client.table('files').select('*').eq('file_id', telegram_file_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Error getting file: {e}")
            return None

    async def delete_file(self, file_id: str) -> bool:
        """Delete file metadata"""
        try:
            self.client.table('files').delete().eq('id', file_id).execute()
            logger.info(f"✅ File deleted: {file_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting file: {e}")
            return False

    async def increment_access_count(self, file_id: str) -> bool:
        """Increment file access count"""
        try:
            file_data = await self.get_file(file_id)
            if file_data:
                new_count = file_data.get('access_count', 0) + 1
                self.client.table('files').update({'access_count': new_count}).eq('id', file_id).execute()
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error incrementing access: {e}")
            return False

    # ============ USER OPERATIONS ============
    
    async def add_user(self, user_data: dict) -> dict:
        """Add new user"""
        try:
            data = {
                'user_id': user_data.get('user_id'),
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'is_admin': user_data.get('is_admin', False),
                'is_verified': False,
                'joined_date': datetime.now().isoformat(),
                'total_files': 0
            }
            
            response = self.client.table('users').insert(data).execute()
            logger.info(f"✅ User added: {user_data.get('username')}")
            return response.data[0] if response.data else data
        except Exception as e:
            logger.error(f"❌ Error adding user: {e}")
            raise

    async def get_user(self, user_id: int) -> dict:
        """Get user data"""
        try:
            response = self.client.table('users').select('*').eq('user_id', user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Error getting user: {e}")
            return None

    async def update_user(self, user_id: int, update_data: dict) -> bool:
        """Update user data"""
        try:
            self.client.table('users').update(update_data).eq('user_id', user_id).execute()
            logger.info(f"✅ User updated: {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error updating user: {e}")
            return False

    async def get_all_users(self) -> list:
        """Get all users"""
        try:
            response = self.client.table('users').select('*').execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Error getting users: {e}")
            return []

    # ============ LINK OPERATIONS ============
    
    async def save_link(self, file_id: str, short_url: str, short_code: str) -> dict:
        """Save generated link"""
        try:
            data = {
                'id': str(uuid.uuid4()),
                'file_id': file_id,
                'short_code': short_code,
                'full_url': short_url,
                'created_date': datetime.now().isoformat(),
                'access_count': 0,
                'is_active': True
            }
            
            response = self.client.table('links').insert(data).execute()
            
            # Update file with short_url
            self.client.table('files').update({'short_url': short_url}).eq('id', file_id).execute()
            
            logger.info(f"✅ Link saved for file: {file_id}")
            return response.data[0] if response.data else data
        except Exception as e:
            logger.error(f"❌ Error saving link: {e}")
            raise

    async def get_link(self, short_code: str) -> dict:
        """Get link by short code"""
        try:
            response = self.client.table('links').select('*').eq('short_code', short_code).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Error getting link: {e}")
            return None

    async def get_user_links(self, user_id: int) -> list:
        """Get all links created by user"""
        try:
            response = self.client.table('links').select('*,files(uploaded_by)').eq('files.uploaded_by', user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Error getting user links: {e}")
            return []

    # ============ UTILITY OPERATIONS ============
    
    def _calculate_expiry(self, auto_delete_seconds: int) -> str:
        """Calculate expiry date"""
        if auto_delete_seconds:
            expiry_date = datetime.now() + timedelta(seconds=auto_delete_seconds)
            return expiry_date.isoformat()
        return None

    async def get_stats(self) -> dict:
        """Get database statistics"""
        try:
            files = self.client.table('files').select('count', count='exact').execute()
            users = self.client.table('users').select('count', count='exact').execute()
            links = self.client.table('links').select('count', count='exact').execute()
            
            return {
                'total_files': files.count or 0,
                'total_users': users.count or 0,
                'total_links': links.count or 0
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {'total_files': 0, 'total_users': 0, 'total_links': 0}

    async def cleanup_expired_files(self) -> int:
        """Delete expired files"""
        try:
            expired_files = self.client.table('files')\
                .select('*')\
                .lt('expiry_date', datetime.now().isoformat())\
                .execute()
            
            deleted_count = 0
            for file in expired_files.data:
                await self.delete_file(file['id'])
                deleted_count += 1
            
            logger.info(f"✅ Cleaned up {deleted_count} expired files")
            return deleted_count
        except Exception as e:
            logger.error(f"❌ Error cleaning up files: {e}")
            return 0

    async def get_user_files(self, user_id: int) -> list:
        """Get all files uploaded by user"""
        try:
            response = self.client.table('files').select('*').eq('uploaded_by', user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Error getting user files: {e}")
            return []
