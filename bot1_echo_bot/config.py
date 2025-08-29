import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./echo_bot.db')

config = Config()