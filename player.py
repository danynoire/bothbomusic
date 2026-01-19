import yt_dlp
import discord
import asyncio
import random

YDL = yt_dlp.YoutubeDL({
    "format": "bestaudio",
    "quiet": True
})

class MusicPlayer:
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.queue = []
        self.loop = False

    async def add(self, query):
        data = YDL.extract_info(query, download=False)
        if "entries" in data:
            data = data["entries"][0]

        self.queue.append(data)

        if not self.guild.voice_client.is_playing():
            await self.play_next()

    async def play_next(self):
        if not self.queue:
            return

        data = self.queue[0]
        source = discord.FFmpegPCMAudio(data["url"])
        self.guild.voice_client.play(
            source,
            after=lambda e: self.bot.loop.create_task(self.after())
        )

    async def after(self):
        if not self.loop:
            self.queue.pop(0)
        await self.play_next()

    def shuffle(self):
        random.shuffle(self.queue)

    def queue_text(self):
        if not self.queue:
            return "Fila vazia"
        return "\n".join(f"{i+1}. {x['title']}" for i, x in enumerate(self.queue))

    def seek(self, seconds):
        pass  # seek avançado (ffmpeg args)
