import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from dashboard import run_dashboard

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("BOT_OWNER_ID"))

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="hb!",
    intents=intents,
    owner_id=OWNER_ID
)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online como {bot.user}")

async def main():
    async with bot:
        await bot.load_extension("cogs.help_cog")
        await bot.load_extension("cogs.music")
        await bot.load_extension("cogs.admin_panel")
        run_dashboard(bot)
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())
