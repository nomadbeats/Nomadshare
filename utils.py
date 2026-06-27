# NomadShare - Utility Functions

import os
import json
import requests
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from config import SHORTLINK_URL, SHORTLINK_API

logger = logging.getLogger(__name__)

class URLShortener:
    """Handle URL shortening operations"""
    
    @staticmethod
    async def shorten(long_url: str) -> str:
        """Shorten URL using external service"""
        if not SHORTLINK_URL or not SHORTLINK_API:
            return long_url
        
        try:
            api_url = f"https://{SHORTLINK_URL}/api"
            params = {
                'api': SHORTLINK_API,
                'url': long_url
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.text.strip()
            else:
                logger.warning(f"Failed to shorten URL: {response.status_code}")
                return long_url
                
        except Exception as e:
            logger.error(f"Error shortening URL: {e}")
            return long_url

class TimeFormatter:
    """Format time intervals"""
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Convert seconds to human-readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h"
        else:
            days = seconds // 86400
            return f"{days}d"
    
    @staticmethod
    def format_date(date_obj: datetime) -> str:
        """Format datetime to readable string"""
        return date_obj.strftime("%d %B %Y, %H:%M:%S")
    
    @staticmethod
    def get_expiry_text(seconds: int) -> str:
        """Get expiry time text"""
        if seconds >= 86400:
            days = seconds // 86400
            return f"{days} day{'s' if days > 1 else ''}"
        elif seconds >= 3600:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''}"
        elif seconds >= 60:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return f"{seconds} second{'s' if seconds > 1 else ''}"

class FileFormatter:
    """Format file information"""
    
    @staticmethod
    def format_size(bytes_size: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.2f} PB"
    
    @staticmethod
    def get_file_type(mime_type: str) -> str:
        """Get file type from MIME type"""
        type_map = {
            'image': '🖼️ Image',
            'video': '🎥 Video',
            'audio': '🎵 Audio',
            'document': '📄 Document',
            'text': '📝 Text',
            'application/pdf': '📕 PDF',
            'application/zip': '📦 Archive',
        }
        
        for key, value in type_map.items():
            if key in mime_type.lower():
                return value
        
        return '📁 File'

class TextFormatter:
    """Format text outputs"""
    
    @staticmethod
    def create_box(text: str, title: str = None) -> str:
        """Create a formatted text box"""
        lines = text.split('\n')
        max_length = max(len(line) for line in lines) if lines else 0
        
        if title:
            box = f"╔{'═' * (max_length + 2)}╗\n"
            box += f"║ {title.center(max_length)} ║\n"
            box += f"╠{'═' * (max_length + 2)}╣\n"
        else:
            box = f"╔{'═' * (max_length + 2)}╗\n"
        
        for line in lines:
            box += f"║ {line.ljust(max_length)} ║\n"
        
        box += f"╚{'═' * (max_length + 2)}╝"
        return box
    
    @staticmethod
    def create_button_text(text: str, buttons: List[tuple]) -> str:
        """Create text with button layout"""
        result = text + "\n\n"
        for label, url in buttons:
            result += f"[{label}]({url})\n"
        return result

class Logger:
    """Logging utilities"""
    
    @staticmethod
    def log_action(action: str, user_id: int, details: str = ""):
        """Log user action"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] User {user_id}: {action}"
        if details:
            log_message += f" - {details}"
        logger.info(log_message)
    
    @staticmethod
    def log_error(error: str, context: str = ""):
        """Log error"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] ERROR: {error}"
        if context:
            log_message += f" ({context})"
        logger.error(log_message)

class Validator:
    """Input validation"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format"""
        import re
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    @staticmethod
    def is_valid_username(username: str) -> bool:
        """Validate username format"""
        import re
        username_pattern = re.compile(r'^[a-zA-Z0-9_]{5,32}$')
        return username_pattern.match(username) is not None
    
    @staticmethod
    def is_valid_file_size(size_bytes: int, max_mb: int = 2000) -> bool:
        """Check if file size is valid"""
        max_bytes = max_mb * 1024 * 1024
        return size_bytes <= max_bytes

class StatisticsCalculator:
    """Calculate statistics"""
    
    @staticmethod
    def calculate_growth(current: int, previous: int) -> float:
        """Calculate growth percentage"""
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    
    @staticmethod
    def get_peak_hours(access_logs: List[dict]) -> List[int]:
        """Get peak access hours"""
        hour_counts = {}
        for log in access_logs:
            hour = log.get('hour')
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if not hour_counts:
            return []
        
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, _ in sorted_hours[:3]]

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
