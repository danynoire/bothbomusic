import discord
from discord.ext import commands

class Info(commands.Cog, name="ℹ️ Informações"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Ping do bot")
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong! `{round(self.bot.latency*1000)}ms`")

async def setup(bot):
    await bot.add_cog(Info(bot))
