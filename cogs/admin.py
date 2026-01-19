from discord.ext import commands
from checks import owner_only

class Admin(commands.Cog, name="⚙️ Admin"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Desligar bot")
    @owner_only()
    async def shutdown(self, ctx):
        await ctx.send("🔌 Desligando...")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Admin(bot))
