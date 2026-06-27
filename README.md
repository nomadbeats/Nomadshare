# 🚀 NomadShare - Permanent File Storage Bot

A powerful Telegram bot for creating permanent shareable file links with Supabase backend.

![NomadShare](https://img.shields.io/badge/NomadShare-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![Supabase](https://img.shields.io/badge/Supabase-Database-blueviolet)

---

## ✨ Features

✅ **Permanent File Storage** - Store files indefinitely in Supabase  
✅ **Shareable Links** - Generate unique links for any file  
✅ **Auto-Delete** - Automatically remove files after set time  
✅ **Batch Processing** - Create multiple links at once  
✅ **Custom URL Shortener** - Use your own domain for links  
✅ **Clone Bot** - Create personal bot instances  
✅ **Stream Support** - Multiple media player support  
✅ **Admin Broadcasting** - Send messages to all users  
✅ **Token Verification** - Secure file access  
✅ **User Management** - Track users and their uploads  

---

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- Telegram Bot Token (from @BotFather)
- Supabase Account & Project
- API ID & Hash (from my.telegram.org)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/nomadshare.git
cd nomadshare
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup Supabase

1. Create a Supabase project at https://supabase.com
2. Create tables using SQL:

```sql
-- Files table
CREATE TABLE files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  file_id TEXT NOT NULL,
  file_name TEXT NOT NULL,
  file_size BIGINT,
  file_type TEXT,
  uploaded_by BIGINT,
  upload_date TIMESTAMP DEFAULT now(),
  expiry_date TIMESTAMP,
  access_count INTEGER DEFAULT 0,
  is_public BOOLEAN DEFAULT true,
  short_url TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- Users table
CREATE TABLE users (
  user_id BIGINT PRIMARY KEY,
  username TEXT,
  first_name TEXT,
  is_admin BOOLEAN DEFAULT false,
  is_verified BOOLEAN DEFAULT false,
  joined_date TIMESTAMP DEFAULT now(),
  total_files INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT now()
);

-- Links table
CREATE TABLE links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  file_id UUID REFERENCES files(id),
  short_code TEXT UNIQUE,
  full_url TEXT,
  created_date TIMESTAMP DEFAULT now(),
  access_count INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT now()
);
```

### Step 4: Setup Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your values:
```
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
BOT_USERNAME=your_bot_username
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
ADMINS=123456789 987654321
LOG_CHANNEL=-100your_channel_id
```

### Step 5: Run Bot
```bash
python bot.py
```

---

## 📱 Commands

### User Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/about` - About NomadShare
- `/link` - Generate link (reply to file)
- `/batch 1 50` - Generate batch links
- `/stats` - Show statistics (Admin)

### Admin Commands
- `/broadcast` - Send message to all users (reply to message)
- `/deletecloned` - Delete clone bot

---

## 🗄️ Database Schema

### Files Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| file_id | TEXT | Telegram file_id |
| file_name | TEXT | File name |
| file_size | BIGINT | Size in bytes |
| file_type | TEXT | MIME type |
| uploaded_by | BIGINT | User ID |
| upload_date | TIMESTAMP | Upload time |
| expiry_date | TIMESTAMP | Auto-delete time |
| access_count | INTEGER | Download count |
| is_public | BOOLEAN | Public visibility |
| short_url | TEXT | Shortened URL |

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| user_id | BIGINT | Telegram user ID |
| username | TEXT | Username |
| first_name | TEXT | First name |
| is_admin | BOOLEAN | Admin status |
| is_verified | BOOLEAN | Verification status |
| joined_date | TIMESTAMP | Join date |
| total_files | INTEGER | File count |

### Links Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| file_id | UUID | File reference |
| short_code | TEXT | Short code |
| full_url | TEXT | Full URL |
| created_date | TIMESTAMP | Creation time |
| access_count | INTEGER | Access count |
| is_active | BOOLEAN | Active status |

---

## 🚀 Deployment

### Heroku Deployment

1. Create `runtime.txt`:
```
python-3.10.8
```

2. Deploy:
```bash
heroku login
heroku create nomadshare
git push heroku main
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
# ... set other variables
```

### Docker Deployment

```bash
docker build -t nomadshare .
docker run -d --name nomadshare nomadshare
```

### Render.com Deployment

1. Push code to GitHub
2. Connect Render to repo
3. Set environment variables
4. Deploy

---

## 📊 API Endpoints

### Health Check
```
GET /health
Response: {"status": "healthy", "service": "NomadShare"}
```

### Get File
```
GET /file/{file_id}
Response: {file data}
```

### Access Link
```
GET /link/{short_code}
Response: {file data and bot info}
```

### Statistics
```
GET /stats
Response: {"total_files": 0, "total_users": 0, "total_links": 0}
```

---

## 🔧 Configuration Options

### Auto-Delete
```
AUTO_DELETE_MODE=True
AUTO_DELETE=30  # Minutes
AUTO_DELETE_TIME=1800  # Seconds
```

### URL Shortener
```
VERIFY_MODE=True
SHORTLINK_URL=short.link
SHORTLINK_API=your_api_key
```

### Stream Mode
```
STREAM_MODE=True
SLEEP_THRESHOLD=60
PING_INTERVAL=1200
```

---

## 📝 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| API_ID | Yes | Telegram API ID |
| API_HASH | Yes | Telegram API Hash |
| BOT_TOKEN | Yes | Bot token from @BotFather |
| BOT_USERNAME | Yes | Bot username (without @) |
| SUPABASE_URL | Yes | Supabase project URL |
| SUPABASE_KEY | Yes | Supabase anon key |
| ADMINS | Yes | Admin user IDs (space-separated) |
| LOG_CHANNEL | Yes | Log channel ID |
| AUTO_DELETE_MODE | No | Enable auto-delete |
| AUTO_DELETE | No | Delete after N minutes |
| SHORTLINK_URL | No | URL shortener domain |
| SHORTLINK_API | No | Shortener API key |
| VERIFY_MODE | No | Enable link verification |
| STREAM_MODE | No | Enable streaming |
| URL | No | Server URL |
| PORT | No | Server port (default: 8080) |

---

## 🐛 Troubleshooting

### Bot not responding
- Check BOT_TOKEN validity
- Verify API_ID and API_HASH
- Check Supabase connection

### Files not saving
- Verify SUPABASE_URL and SUPABASE_KEY
- Check database tables exist
- Review logs in nomadshare.log

### Links not shortening
- Verify SHORTLINK_URL and SHORTLINK_API
- Check internet connection
- Test shortener API manually

---

## 📚 Usage Examples

### Generate Single Link
```
1. Send file to bot
2. Reply with /link
3. Receive shortened URL
```

### Batch Generate
```
1. Upload multiple files to a channel
2. Send /batch 1 50
3. Get all links at once
```

### Admin Broadcast
```
1. Reply to any message with /broadcast
2. Message sent to all users
```

---

## 🔒 Security

- Uses Supabase Row Level Security
- Token verification for sensitive operations
- Admin-only dangerous commands
- Encrypted file storage
- Rate limiting on requests

---

## 📈 Performance

- Async/await for non-blocking operations
- Efficient database queries
- Caching implemented
- Batch operations supported
- Auto-cleanup of expired files

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👨‍💻 Support

For issues and questions:
- Create GitHub issue
- Contact: support@nomadshare.com
- Telegram: @NomadShareSupport

---

## 🌟 Credits

- Built with Pyrogram
- Powered by Supabase
- Inspired by file sharing solutions

---

## 📞 Contact

- **Telegram**: @NomadShare
- **Email**: contact@nomadshare.com
- **GitHub**: https://github.com/nomadshare

---

**Made with ❤️ for seamless file sharing**

### Star ⭐ this repo if you found it helpful!
