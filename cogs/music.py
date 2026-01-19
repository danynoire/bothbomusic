import discord
from discord.ext import commands
from player import get_player

class Music(commands.Cog, name="🎵 Música"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Tocar música")
    async def play(self, ctx, *, query):
        player = get_player(ctx.guild)

        if not ctx.guild.voice_client:
            await ctx.author.voice.channel.connect()

        await player.add(query)
        await ctx.send(f"🎶 Tocando: **{query}**")

    @commands.hybrid_command(description="Pular música")
    async def skip(self, ctx):
        ctx.guild.voice_client.stop()
        await ctx.send("⏭ Pulou")

    @commands.hybrid_command(description="Parar música")
    async def stop(self, ctx):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("⏹ Parado")

async def setup(bot):
    await bot.add_cog(Music(bot))
