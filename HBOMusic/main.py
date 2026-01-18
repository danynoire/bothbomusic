import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Load env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_IDS = [int(x) for x in os.getenv("BOT_OWNER_IDS", "").split(",")]

# Intents
intents = discord.Intents.all()
client = commands.Bot(command_prefix="hb!", intents=intents)
client.owner_ids = OWNER_IDS

# Ensure config dirs
if not os.path.exists("config/guilds"):
    os.makedirs("config/guilds")

# Load Cogs
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(f"[OK] Carregado: {filename}")
            except Exception as e:
                print(f"[ERRO] {filename} -> {e}")

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}!")

async def main():
    await load_cogs()
    await client.start(TOKEN)

asyncio.run(main())
