import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Mostra todos os comandos")
    async def help(self, ctx):
        embed = discord.Embed(
            title="📘 HBO Music • Ajuda",
            description="Prefixo: `hb!` | Slash: `/`",
            color=0x5865F2
        )
        embed.add_field(
            name="🎵 Música",
            value="play, pause, resume, skip, stop, queue, loop, volume, seek",
            inline=False
        )
        embed.add_field(
            name="⚙️ Admin",
            value="panel, stats",
            inline=False
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
