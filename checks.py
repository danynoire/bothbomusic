from discord.ext import commands
from config import OWNERS

def owner_only():
    async def predicate(ctx):
        return ctx.author.id in OWNERS
    return commands.check(predicate)
