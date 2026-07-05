# NomadShare - Message Templates
# HTML parse mode (see api/server.py Defaults) — not Markdown. Markdown's
# escaping rules are context-sensitive and break easily on file names with
# underscores/asterisks; HTML only needs <, >, & escaped, which tools.formatters.esc()
# handles for any dynamic value dropped into these templates.


class script:
    START_TXT = (
        "<b>NomadShare</b>\n\n"
        "Save a file, get a permanent link, share it anywhere.\n\n"
        "Reply to any file with /link to generate one."
    )

    HELP_TXT = (
        "<b>Commands</b>\n\n"
        "/start — check the bot is alive, or open a shared link\n"
        "/link — reply to a file to generate a shareable link\n"
        "/batch (start) (end) — bulk link generation (in progress)\n"
        "/myfiles — list files you've saved\n"
        "/deletefile (id) — delete one of your files\n\n"
        "<b>Admin</b>\n"
        "/mode — control who can save files and generate links\n"
        "/stats — database statistics\n"
        "/broadcast — reply to a message to send it to all users"
    )

    ABOUT_TXT = (
        "<b>About NomadShare</b>\n\n"
        "Version {version}\n"
        "Database: Supabase\n"
        "Framework: python-telegram-bot, webhook deployment\n\n"
        "Permanent file storage and sharing for Telegram."
    )

    STATS_TXT = (
        "<b>Statistics</b>\n\n"
        "Files: {total_files}\n"
        "Users: {total_users}\n"
        "Links: {total_links}"
    )

    MODE_TXT = (
        "<b>Access mode</b>\n\n"
        "Current: {current}\n\n"
        "Private — only admins can save files and generate links.\n"
        "Public — anyone can."
    )

    LINK_GENERATED = (
        "<b>Link generated</b>\n\n"
        "File: {file_name}\n"
        "Size: {file_size}\n"
        "Expires in: {validity}\n\n"
        "{link}"
    )

    BATCH_SUCCESS = "<b>Batch complete</b>\n\nFiles: {count}\nTime: {time}s"

    CAPTION = "Shared via NomadShare"

    FILE_NOT_FOUND = "That file couldn't be found — it may have expired or been removed."
    INVALID_LINK = "This link is invalid or has expired."
