import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

OWNER_ID_ENV = os.getenv("BOT_OWNER_ID")
if not OWNER_ID_ENV:
    raise RuntimeError("❌ BOT_OWNER_ID não definido no ambiente")

OWNER_ID = int(OWNER_ID_ENV)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="hb!",
    intents=intents,
    owner_id=OWNER_ID,
    help_command=None  # 🔥 MUITO IMPORTANTE
)

async def main():
    async with bot:
        await bot.load_extension("cogs.help_cog")
        await bot.load_extension("music")
        await bot.start(TOKEN)

@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print("❌ Erro ao syncar slash:", e)

asyncio.run(main())
