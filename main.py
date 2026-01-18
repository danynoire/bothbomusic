import discord
from discord.ext import commands
import os, asyncio
from dotenv import load_dotenv
import wavelink
from dashboard import run_dashboard

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_IDS = [int(x) for x in os.getenv("BOT_OWNER_IDS").split(",")]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="hb!", intents=intents)
bot.owner_ids = OWNER_IDS

@bot.event
async def on_ready():
    print(f"✅ Conectado como {bot.user}")

    await wavelink.NodePool.create_node(
        bot=bot,
        host="127.0.0.1",
        port=2333,
        password="youshallnotpass"
    )

async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

async def main():
    await load_cogs()
    asyncio.create_task(run_dashboard(bot))
    await bot.start(TOKEN)

asyncio.run(main())
