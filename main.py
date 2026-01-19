import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=os.getenv("PREFIX", "hb!"),
    intents=intents
)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online como {bot.user}")

async def setup():
    await bot.load_extension("music_cog")

bot.loop.create_task(setup())
bot.run(os.getenv("DISCORD_TOKEN"))
