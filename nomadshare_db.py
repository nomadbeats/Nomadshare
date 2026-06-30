import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class NomadShareDB:
    """Supabase database handler"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client"""
        try:
            from supabase import create_client
            self.client = create_client(supabase_url, supabase_key)
            logger.info("✅ Database connected")
        except ImportError:
            raise ImportError("Supabase not installed!")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    async def save_file(self, file_data: Dict) -> Optional[Dict]:
        """Save file metadata"""
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
            if response.data:
                logger.info(f"✅ File saved: {file_data.get('file_name')}")
                return response.data[0]
            return data
        except Exception as e:
            logger.error(f"❌ Error saving file: {e}")
            return None

    async def get_file(self, file_id: str) -> Optional[Dict]:
        """Get file by ID"""
        try:
            response = self.client.table('files').select('*').eq('id', file_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Error getting file: {e}")
            return None

    async def delete_file(self, file_id: str) -> bool:
        """Delete file"""
        try:
            self.client.table('files').delete().eq('id', file_id).execute()
            logger.info(f"✅ File deleted: {file_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting file: {e}")
            return False

    async def increment_access_count(self, file_id: str) -> bool:
        """Increment access count"""
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

    async def add_user(self, user_data: Dict) -> Optional[Dict]:
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
            if response.data:
                logger.info(f"✅ User added: {user_data.get('username')}")
                return response.data[0]
            return data
        except Exception as e:
            logger.error(f"❌ Error adding user: {e}")
            return None

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            response = self.client.table('users').select('*').eq('user_id', user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Error getting user: {e}")
            return None

    async def update_user(self, user_id: int, update_data: Dict) -> bool:
        """Update user"""
        try:
            self.client.table('users').update(update_data).eq('user_id', user_id).execute()
            logger.info(f"✅ User updated: {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error updating user: {e}")
            return False

    async def get_all_users(self) -> List[Dict]:
        """Get all users"""
        try:
            response = self.client.table('users').select('*').execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Error getting users: {e}")
            return []

    async def save_link(self, file_id: str, short_url: str, short_code: str) -> Optional[Dict]:
        """Save link"""
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
            self.client.table('files').update({'short_url': short_url}).eq('id', file_id).execute()
            
            logger.info(f"✅ Link saved: {file_id}")
            if response.data:
                return response.data[0]
            return data
        except Exception as e:
            logger.error(f"❌ Error saving link: {e}")
            return None

    async def get_link(self, short_code: str) -> Optional[Dict]:
        """Get link by code"""
        try:
            response = self.client.table('links').select('*').eq('short_code', short_code).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Error getting link: {e}")
            return None

    async def get_stats(self) -> Dict:
        """Get statistics"""
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
            for file in expired_files.data if expired_files.data else []:
                await self.delete_file(file['id'])
                deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"✅ Cleaned up {deleted_count} expired files")
            
            return deleted_count
        except Exception as e:
            logger.error(f"❌ Error cleaning up: {e}")
            return 0

    @staticmethod
    def _calculate_expiry(auto_delete_seconds: int) -> Optional[str]:
        """Calculate expiry date"""
        if auto_delete_seconds and auto_delete_seconds > 0:
            expiry_date = datetime.now() + timedelta(seconds=auto_delete_seconds)
            return expiry_date.isoformat()
        return None

    async def get_user_files(self, user_id: int) -> List[Dict]:
        """Get user files"""
        try:
            response = self.client.table('files').select('*').eq('uploaded_by', user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Error getting user files: {e}")
            return []
