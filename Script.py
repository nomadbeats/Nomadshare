# NomadShare - Permanent File Store Bot
# Script Messages and Texts

class script(object):
    
    # ============ Start Message ============
    START_TXT = """
╔═══════════════════════════════╗
║   🚀 Welcome to NomadShare 🚀  ║
║  Your Permanent File Storage   ║
╚═══════════════════════════════╝

📁 **NomadShare** is your ultimate file storage solution!

✨ **Features:**
• Permanent shareable links
• Auto-delete after set time
• Clone bot for personal use
• Batch link generation
• Custom URL shortener
• Stream with multiple players
• Token verification
• Admin broadcasting

🎯 **Quick Start:**
• `/link` - Generate link for a file
• `/batch` - Create multiple links
• `/clone` - Create personal bot
• `/help` - Full command list

👥 Owner: {owner}
📊 Version: 1.0.0
"""

    # ============ Help Message ============
    HELP_TXT = """
╔════════════════════════════════╗
║     🎯 NomadShare Commands      ║
╚════════════════════════════════╝

**📌 Main Commands:**

1️⃣ `/start` 
   → Check if bot is alive

2️⃣ `/link`
   → Reply to file and use this
   → Generates permanent shareable link

3️⃣ `/batch (start) (end)`
   → Generate links for multiple files
   → Example: `/batch 1 50`

4️⃣ `/base_site (domain)`
   → Set your URL shortener domain
   → Example: `/base_site short.link`

5️⃣ `/api (api_key)`
   → Set URL shortener API key
   → Example: `/api your_api_key`

6️⃣ `/broadcast`
   → Reply to message for broadcast
   → Send to all users (Admin only)

7️⃣ `/deletecloned (bot_token)`
   → Delete cloned bot instance
   → (Admin only)

**🤖 Clone Bot Commands:**
Same as above but exclusive to your clone

**ℹ️ Need More Help?**
Contact support or check documentation
"""

    # ============ About Message ============
    ABOUT_TXT = """
╔════════════════════════════════╗
║       📋 About NomadShare       ║
╚════════════════════════════════╝

🌟 **Project:** NomadShare
📊 **Version:** 1.0.0
💾 **Database:** Supabase
🔧 **Framework:** Pyrogram
🚀 **Status:** Active & Running

**Key Features:**
✅ Permanent file storage
✅ Shareable links
✅ Auto-delete functionality
✅ Clone bot support
✅ Batch processing
✅ Custom URL shortener
✅ Stream support
✅ Admin controls

**Storage:**
• Files stored in Supabase
• Encrypted and secure
• 24/7 accessible

Made with ❤️ for file sharing
"""

    # ============ Stats Message ============
    STATS_TXT = """
╔════════════════════════════════╗
║      📊 NomadShare Statistics   ║
╚════════════════════════════════╝

📁 Total Files: {total_files}
👥 Total Users: {total_users}
🔗 Generated Links: {total_links}
⏰ Uptime: {uptime}
"""

    # ============ Restart Message ============
    RESTART_TXT = """
╔════════════════════════════════╗
║    🔄 NomadShare Restarted      ║
╚════════════════════════════════╝

✅ Bot is back online!

📅 Date: {0}
⏰ Time: {1}
🔧 Status: Running

Thank you for using NomadShare!
"""

    # ============ Error Messages ============
    NO_ADMIN_TXT = "❌ **Sorry!** Only admins can use this command."
    
    PREMIUM_FEATURE_TXT = "🔒 **Premium Feature** - Available for NomadShare Pro"
    
    CLONE_ERROR = "❌ Error creating clone. Check your token and try again."
    
    FILE_NOT_FOUND = "❌ File not found or has been deleted."
    
    INVALID_LINK = "❌ Invalid or expired link."

    # ============ Success Messages ============
    LINK_GENERATED = """
✅ **Link Generated Successfully!**

🔗 **Shortened URL:** `{link}`
📁 **File:** {file_name}
⏰ **Valid for:** {validity}

Share this link with anyone!
"""

    BATCH_SUCCESS = """
✅ **Batch Processing Complete!**

📊 Total Files: {count}
🔗 Links Generated: {count}
⏰ Processing Time: {time}s

All links ready to share!
"""

    CLONE_CREATED = """
✅ **Clone Bot Created!**

🤖 **Bot Token:** `{token}`
👤 **Bot Username:** @{username}
🗄️ **Database:** Separate instance
⚙️ **Status:** Ready to use

Start using your personal NomadShare!
"""

    # ============ Caption Text ============
    CAPTION = "Uploaded via **NomadShare** 🚀\n**Permanent File Storage Solution**"

    # ============ Database Schema ============
    DB_TABLES = {
        'files': {
            'id': 'UUID Primary Key',
            'file_id': 'Telegram file_id',
            'file_name': 'File name',
            'file_size': 'File size in bytes',
            'file_type': 'MIME type',
            'uploaded_by': 'User ID',
            'upload_date': 'Timestamp',
            'expiry_date': 'Auto-delete timestamp',
            'access_count': 'Number of downloads',
            'is_public': 'Public visibility',
            'short_url': 'Shortened URL',
        },
        'users': {
            'user_id': 'Telegram user_id',
            'username': 'Telegram username',
            'first_name': 'User first name',
            'is_admin': 'Admin status',
            'is_verified': 'Verification status',
            'joined_date': 'Join timestamp',
            'total_files': 'Files uploaded count',
        },
        'links': {
            'id': 'UUID Primary Key',
            'file_id': 'Reference to files.id',
            'short_code': 'Short URL code',
            'full_url': 'Full shortened URL',
            'created_date': 'Creation timestamp',
            'access_count': 'Access counter',
            'is_active': 'Active status',
        }
    }
