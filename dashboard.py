import discord
from player import get_player

def music_embed(player):
    embed = discord.Embed(
        title="🎶 HB Music",
        description=f"**Tocando agora:**\n{player.current['title'] if player.current else 'Nada'}",
        color=0x5865F2
    )
    embed.set_footer(text="Controle a música pelos botões abaixo")
    return embed

class MusicDashboard(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player

    @discord.ui.button(emoji="⏯", style=discord.ButtonStyle.primary)
    async def pause(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc.is_playing():
            vc.pause()
        else:
            vc.resume()
        await interaction.response.defer()

    @discord.ui.button(emoji="⏭", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction, button):
        interaction.guild.voice_client.stop()
        await interaction.response.defer()

    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary)
    async def loop(self, interaction, button):
        self.player.loop = not self.player.loop
        await interaction.response.defer()

    @discord.ui.button(emoji="⏹", style=discord.ButtonStyle.danger)
    async def stop(self, interaction, button):
        await interaction.guild.voice_client.disconnect()
        await interaction.response.defer()
