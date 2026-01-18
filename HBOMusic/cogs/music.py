import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio
import os

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.is_playing = False
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None
        self.vote_skip_users = set()

    @commands.command(name="play", aliases=["p","tocar"])
    async def play(self, ctx, *, query):
        voice_channel = getattr(ctx.author.voice, "channel", None)
        if not voice_channel:
            return await ctx.send("Entre em um canal de voz primeiro.")

        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]

        self.music_queue.append([info['formats'][0]['url'], voice_channel])
        await ctx.send(f"Adicionado: **{info['title']}**")

        if not self.is_playing:
            await self.start_music()

    async def start_music(self):
        if len(self.music_queue) == 0:
            self.is_playing = False
            return

        self.is_playing = True
        url, channel = self.music_queue.pop(0)

        if not self.vc or not self.vc.is_connected():
            self.vc = await channel.connect()

        self.vc.play(discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS),
                     after=lambda e: asyncio.run_coroutine_threadsafe(self.start_music(), self.client.loop))

    @commands.command(name="queue", aliases=["q","fila"])
    async def queue(self, ctx):
        if not self.music_queue:
            return await ctx.send("Fila vazia.")
        msg = "\n".join(f"{i+1}. {item[0]}" for i, item in enumerate(self.music_queue))
        await ctx.send(msg)

    @commands.command(name="skip", aliases=["pular","next"])
    async def skip(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("Não estou tocando música.")

        members = [m for m in ctx.voice_client.channel.members if not m.bot]
        if ctx.author.id in self.client.owner_ids or ctx.author.guild_permissions.manage_guild:
            vc.stop()
            self.vote_skip_users.clear()
            await ctx.send("⏭ Música pulada!")
        else:
            if ctx.author.id in self.vote_skip_users:
                await ctx.send("Você já votou para pular!")
            else:
                self.vote_skip_users.add(ctx.author.id)
                votes_needed = len(members) // 2 + 1
                if len(self.vote_skip_users) >= votes_needed:
                    vc.stop()
                    self.vote_skip_users.clear()
                    await ctx.send("⏭ Música pulada por votação!")
                else:
                    await ctx.send(f"Votação para pular: {len(self.vote_skip_users)}/{votes_needed}")

    @commands.command(name="stop", aliases=["leave","sair"])
    async def stop(self, ctx):
        self.music_queue.clear()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        self.is_playing = False
        await ctx.send("Parado e desconectado!")

async def setup(client):
    await client.add_cog(Music(client))
