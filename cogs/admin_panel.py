import discord
from discord.ext import commands

class ControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⏯️ Pause", style=discord.ButtonStyle.primary)
    async def pause(self, interaction, button):
        await interaction.response.send_message("⏸️ Pausado", ephemeral=True)

    @discord.ui.button(label="▶️ Resume", style=discord.ButtonStyle.success)
    async def resume(self, interaction, button):
        await interaction.response.send_message("▶️ Continuando", ephemeral=True)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction, button):
        await interaction.response.send_message("⏭️ Pulado", ephemeral=True)

class AdminPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="panel", description="Painel de controle do servidor")
    async def panel(self, ctx):
        embed = discord.Embed(
            title="🎛️ Painel de Controle",
            description="Controle o bot sem site",
            color=0x2ECC71
        )
        await ctx.send(embed=embed, view=ControlView())

async def setup(bot):
    await bot.add_cog(AdminPanel(bot))
