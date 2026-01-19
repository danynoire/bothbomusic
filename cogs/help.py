import discord
from discord.ext import commands

class HelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(
                title="🎵 HB Music • Ajuda",
                description=page,
                color=0x5865F2
            )
            await destination.send(embed=embed)

def setup_help(bot):
    bot.help_command = HelpCommand()
