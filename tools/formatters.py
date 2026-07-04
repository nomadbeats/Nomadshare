# NomadShare - Display Formatters

class FileFormatter:
    @staticmethod
    def format_size(bytes_size: int) -> str:
        size = float(bytes_size or 0)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"

    @staticmethod
    def get_file_type(mime_type: str) -> str:
        type_map = {
            'image': '🖼️ Image',
            'video': '🎥 Video',
            'audio': '🎵 Audio',
            'application/pdf': '📕 PDF',
            'application/zip': '📦 Archive',
            'document': '📄 Document',
            'text': '📝 Text',
        }
        mime_type = mime_type or ""
        for key, value in type_map.items():
            if key in mime_type.lower():
                return value
        return '📁 File'


class TimeFormatter:
    @staticmethod
    def get_expiry_text(seconds: int) -> str:
        if not seconds:
            return "no expiry"
        if seconds >= 86400:
            days = seconds // 86400
            return f"{days} day{'s' if days > 1 else ''}"
        elif seconds >= 3600:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''}"
        elif seconds >= 60:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        return f"{seconds} second{'s' if seconds > 1 else ''}"
