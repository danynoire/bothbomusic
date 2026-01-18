import discord
from discord.ext import commands
import os, asyncio, threading
from dotenv import load_dotenv
import wavelink
from dashboard import run_dashboard

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_IDS = [int(x) for x in os.getenv("BOT_OWNER_IDS", "").split(",") if x]

LAVALINK_HOST = os.getenv("LAVALINK_HOST")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", 2333))
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")

# 🔥 INTENTS SEM PRIVILEGIADOS
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="hb!", intents=intents)
bot.owner_ids = OWNER_IDS

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

    await wavelink.NodePool.create_node(
        bot=bot,
        host=LAVALINK_HOST,
        port=LAVALINK_PORT,
        password=LAVALINK_PASSWORD
    )

async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

def start_dashboard():
    run_dashboard(bot)

async def main():
    await load_cogs()

    threading.Thread(
        target=start_dashboard,
        daemon=True
    ).start()

    await bot.start(TOKEN)

asyncio.run(main())
