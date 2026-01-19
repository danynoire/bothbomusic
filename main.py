import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="hb!",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print(f"🤖 Logado como {bot.user}")

async def main():
    await bot.load_extension("cogs.music")
    await bot.start(os.getenv("DISCORD_TOKEN"))

asyncio.run(main())
