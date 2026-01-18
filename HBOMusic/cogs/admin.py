import discord
from discord.ext import commands
import json
import os

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="botlanguage")
    async def botlanguage(self, ctx, lang: str):
        if ctx.author.id not in self.client.owner_ids:
            return await ctx.send("Somente donos do bot podem usar.")
        with open("config/bot.json","w") as f:
            json.dump({"language":lang},f)
        await ctx.send(f"Idioma global alterado para {lang}!")

    @commands.command(name="botstatus")
    async def botstatus(self, ctx, type:str, *, text:str):
        if ctx.author.id not in self.client.owner_ids:
            return await ctx.send("Somente donos do bot podem usar.")
        types_map = {
            "playing":discord.ActivityType.playing,
            "listening":discord.ActivityType.listening,
            "watching":discord.ActivityType.watching,
            "competing":discord.ActivityType.competing
        }
        await self.client.change_presence(activity=discord.Activity(type=types_map.get(type.lower(),discord.ActivityType.playing), name=text))
        await ctx.send(f"Status global alterado: {type} {text}")

    @commands.command(name="setlanguage")
    async def setlanguage(self, ctx, lang:str):
        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.send("Somente admins podem usar.")
        path = f"config/guilds/{ctx.guild.id}.json"
        cfg = {}
        if os.path.exists(path):
            with open(path,"r") as f:
                cfg = json.load(f)
        cfg["language"] = lang
        with open(path,"w") as f:
            json.dump(cfg,f)
        await ctx.send(f"Idioma do servidor alterado para {lang}")

    @commands.command(name="setprefix")
    async def setprefix(self, ctx, prefix:str):
        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.send("Somente admins podem usar.")
        path = f"config/guilds/{ctx.guild.id}.json"
        cfg = {}
        if os.path.exists(path):
            with open(path,"r") as f:
                cfg = json.load(f)
        cfg["prefix"] = prefix
        with open(path,"w") as f:
            json.dump(cfg,f)
        await ctx.send(f"Prefixo do servidor alterado para {prefix}")

async def setup(client):
    await client.add_cog(Admin(client))
