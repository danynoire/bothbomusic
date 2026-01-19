import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import wavelink
import threading

from dashboard import run_dashboard
from database import init_db

load_dotenv()
init_db()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="hb!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logado como {bot.user}")

    await wavelink.NodePool.create_node(
        bot=bot,
        host="localhost",
        port=2333,
        password="youshallnotpass"
    )

    await bot.tree.sync()
    print("🎧 Lavalink conectado")

async def load_cogs():
    await bot.load_extension("cogs.music")
    await bot.load_extension("cogs.admin")
    print("📦 Cogs carregados")

def start_dashboard():
    run_dashboard(bot)

async def main():
    await load_cogs()

    threading.Thread(
        target=start_dashboard,
        daemon=True
    ).start()

    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
