import discord
from discord.ext import commands
from config import TOKEN, PREFIX
from help import setup_help

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    for ext in ["cogs.music", "cogs.info", "cogs.admin"]:
        await bot.load_extension(ext)

    setup_help(bot)
    await bot.tree.sync()
    print("🤖 Bot online")

bot.run(TOKEN)
