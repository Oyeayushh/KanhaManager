import os

class Config:
    # Bot Token from @BotFather
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # Your Telegram User ID
    OWNER_ID = int(os.environ.get("OWNER_ID", "7682307978"))
    
    # Owner username (without @)
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "")
    
    # Sudo users (space separated IDs)
    SUDO_USERS = set(int(x) for x in os.environ.get("SUDO_USERS", "7682307978").split() if x)
    
    # PostgreSQL Database URL (from Heroku Postgres addon)
    DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://", 1)
    
    # Bot API ID and Hash (from my.telegram.org)
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    
    # Log group chat ID (optional)
    LOG_CHAT = int(os.environ.get("LOG_CHAT", "0"))
    
    # Workers
    WORKERS = int(os.environ.get("WORKERS", "8"))
