import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import wavelink

from dashboard import run_dashboard
from database import init_db

# 🔹 inicia banco
init_db()

# 🔹 carrega env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 🔹 intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# 🔹 bot
bot = commands.Bot(command_prefix="hb!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logado como {bot.user}")

    # 🔹 Lavalink
    try:
        await wavelink.NodePool.create_node(
            bot=bot,
            host="localhost",
            port=2333,
            password="youshallnotpass"
        )
        print("🎧 Lavalink conectado")
    except Exception as e:
        print("❌ Erro ao conectar no Lavalink:", e)

    # 🔹 Slash commands
    await bot.tree.sync()
    print("✅ Slash commands sincronizados")

# 🔹 carregar cogs
async def load_cogs():
    await bot.load_extension("cogs.music")
    await bot.load_extension("cogs.admin")
    print("📦 Cogs carregados")

# 🔹 inicia dashboard em thread separada
def start_dashboard():
    print("🌐 Dashboard iniciando...")
    run_dashboard(bot)

async def main():
    await load_cogs()

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, start_dashboard)

    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
