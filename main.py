import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="hb!",
    intents=intents,
)

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

async def main():
    await bot.load_extension("cogs.music")
    await bot.start(os.getenv("BOT_TOKEN"))

asyncio.run(main())
