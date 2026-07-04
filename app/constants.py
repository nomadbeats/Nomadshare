# NomadShare - Message Templates
# Trimmed to commands that actually exist in this build. The original
# templates advertised /clone, /base_site, /api, streaming, etc. which
# had no matching handlers anywhere in the codebase.


class script:
    START_TXT = """
🚀 **Welcome to NomadShare!**

📁 Your permanent file storage & sharing bot.

🎯 **Quick Start:**
• Reply to a file with `/link` to generate a shareable link
• Anyone with the link can fetch the file by opening it here

👥 Owner: {owner}
📊 Version: 2.0.0
"""

    HELP_TXT = """
🎯 **NomadShare Commands**

1️⃣ `/start` — check if the bot is alive (or open a shared link)
2️⃣ `/link` — reply to a file to generate a shareable link
3️⃣ `/batch (start) (end)` — placeholder for bulk link generation
4️⃣ `/myfiles` — list files you've uploaded
5️⃣ `/deletefile (id)` — delete one of your files

**Admin only:**
6️⃣ `/mode [public|private]` — control who can save files & generate links
7️⃣ `/stats` — database statistics
8️⃣ `/broadcast` — reply to a message to send it to all users
"""

    ABOUT_TXT = """
📋 **About NomadShare**

🌟 Project: NomadShare
📊 Version: 2.0.0
💾 Database: Supabase
🔧 Framework: python-telegram-bot (webhook)
🚀 Status: Active

Made for permanent file sharing on Telegram.
"""

    STATS_TXT = """
📊 **NomadShare Statistics**

📁 Total Files: {total_files}
👥 Total Users: {total_users}
🔗 Generated Links: {total_links}
"""

    LINK_GENERATED = """
✅ **Link Generated Successfully!**

🔗 **Link:** {link}
📁 **File:** {file_name}
📊 **Size:** {file_size}
⏰ **Valid for:** {validity}

Share this link with anyone — opening it starts the bot and delivers the file.
"""

    BATCH_SUCCESS = """
✅ **Batch Processing Complete!**

📊 Files: {count}
⏰ Processing Time: {time}s
"""

    CAPTION = "Uploaded via **NomadShare** 🚀\nPermanent File Storage Solution"

    FILE_NOT_FOUND = "❌ File not found or has been deleted."
    INVALID_LINK = "❌ Invalid or expired link."
