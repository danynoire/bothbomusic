import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "hb!")
OWNERS = [int(x) for x in os.getenv("BOT_OWNERS", "").split(",")]

DATABASE_URL = os.getenv("DATABASE_URL")
