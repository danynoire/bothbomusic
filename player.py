import yt_dlp
import discord
import asyncio
from collections import deque

ytdlp_opts = {
    "format": "bestaudio",
    "quiet": True,
    "default_search": "ytsearch",
}

class MusicPlayer:
    def __init__(self, guild):
        self.guild = guild
        self.queue = deque()
        self.current = None
        self.loop = False

    async def add(self, query):
        with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if "entries" in info:
                info = info["entries"][0]

        self.queue.append(info)
        if not self.current:
            await self.play_next()

    async def play_next(self):
        if self.loop and self.current:
            self.queue.appendleft(self.current)

        if not self.queue:
            self.current = None
            return

        self.current = self.queue.popleft()
        source = discord.FFmpegPCMAudio(self.current["url"])
        vc = self.guild.voice_client
        vc.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(self.play_next(), vc.loop))

players = {}

def get_player(guild):
    if guild.id not in players:
        players[guild.id] = MusicPlayer(guild)
    return players[guild.id]
