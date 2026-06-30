class script(object):
    
    START_TXT = """
╔═══════════════════════════════╗
║   🚀 Welcome to NomadShare 🚀  ║
║  Your Permanent File Storage   ║
╚═══════════════════════════════╝

📁 **NomadShare** is your ultimate file storage solution!

✨ **Features:**
• Permanent shareable links
• Auto-delete after set time
• User-friendly interface

🎯 **Quick Start:**
• `/link` - Generate link (reply to file)
• `/myfiles` - View your files
• `/help` - Show all commands

👥 **Owner:** {owner}
📊 **Version:** 1.0.0

✅ Bot is ready to use!
"""

    HELP_TXT = """
╔════════════════════════════════╗
║     📚 NomadShare Help         ║
╚════════════════════════════════╝

**Available Commands:**

1️⃣ `/start` - Start bot and register

2️⃣ `/help` - Show this message

3️⃣ `/link` - Generate link
   → Reply to a file first

4️⃣ `/myfiles` - View your files

5️⃣ `/deletefile` - Delete file
   → Usage: /deletefile <file_id>

6️⃣ `/ping` - Check if alive

7️⃣ `/stats` - Statistics (Admin)

8️⃣ `/broadcast` - Broadcast (Admin)
   → Reply to message first

9️⃣ `/about` - About NomadShare

**Usage Tips:**
✅ Reply to file with /link to create link
✅ Share the link with anyone
✅ Files stored permanently
✅ Each file gets unique ID
"""

    ABOUT_TXT = """
╔════════════════════════════════╗
║       ℹ️  About NomadShare      ║
╚════════════════════════════════╝

🤖 **Project:** NomadShare
📊 **Version:** 1.0.0
🔧 **Framework:** Pyrogram
💾 **Database:** Supabase
🚀 **Deployment:** Vercel Webhook

📝 **Description:**
NomadShare is a Telegram bot for permanent
file storage with shareable links.

✨ **Features:**
✅ Permanent file storage
✅ Instant shareable links
✅ Auto-delete support
✅ User tracking
✅ Admin controls
✅ Statistics

🔒 **Privacy:**
• Files stored securely
• User data encrypted
• Admin-only commands

Made with ❤️ for file sharing
"""

    CAPTION = "📤 Uploaded via **NomadShare** 🚀"
