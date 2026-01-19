import os
import threading
import discord
from discord.ext import commands
from dotenv import load_dotenv

from dashboard import run_dashboard

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="hb!",
    intents=intents
)

# ================= EVENTS =================

@bot.event
async def on_ready():
    print(f"🤖 Bot online como {bot.user}")

# ================= COGS ===================

async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

# ================= START ==================

def start_dashboard():
    run_dashboard(bot)

@bot.event
async def setup_hook():
    await load_cogs()
    print("📦 Cogs carregados")

    # dashboard em thread separada
    threading.Thread(
        target=start_dashboard,
        daemon=True
    ).start()

bot.run(TOKEN)
