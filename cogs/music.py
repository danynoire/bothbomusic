import discord
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def play(self, ctx, *, query: str):
        await ctx.send(f"▶️ Tocando: `{query}`")

    @commands.hybrid_command()
    async def pause(self, ctx):
        await ctx.send("⏸️ Pausado")

    @commands.hybrid_command()
    async def resume(self, ctx):
        await ctx.send("▶️ Continuando")

    @commands.hybrid_command()
    async def skip(self, ctx):
        await ctx.send("⏭️ Pulado")

    @commands.hybrid_command()
    async def stop(self, ctx):
        await ctx.send("⏹️ Parado")

    @commands.hybrid_command()
    async def loop(self, ctx, mode: str):
        await ctx.send(f"🔁 Loop: `{mode}`")

async def setup(bot):
    await bot.add_cog(Music(bot))
