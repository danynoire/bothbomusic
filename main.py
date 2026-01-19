import discord
from discord.ext import commands
from config import TOKEN, PREFIX
from player import get_player
from dashboard import MusicDashboard, music_embed
from checks import owner_only

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents
)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("🤖 Bot online")

@commands.hybrid_command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("🎧 Conectado")

@commands.hybrid_command()
async def play(ctx, *, query):
    player = get_player(ctx.guild)

    if not ctx.guild.voice_client:
        await ctx.author.voice.channel.connect()

    await player.add(query)

    await ctx.send(
        embed=music_embed(player),
        view=MusicDashboard(player)
    )

@commands.hybrid_command()
async def skip(ctx):
    ctx.guild.voice_client.stop()
    await ctx.send("⏭ Pulou")

@commands.hybrid_command()
async def stop(ctx):
    await ctx.guild.voice_client.disconnect()
    await ctx.send("⏹ Parou")

@commands.hybrid_command()
@owner_only()
async def shutdown(ctx):
    await ctx.send("🔌 Desligando bot")
    await bot.close()

bot.run(TOKEN)
