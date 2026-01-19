import yt_dlp
import discord
import asyncio
import random

YDL = yt_dlp.YoutubeDL({
    "format": "bestaudio",
    "quiet": True,
    "noplaylist": False
})

class MusicPlayer:
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.queue = []
        self.loop = False
        self.current = None
        self.position = 0

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

        self.current = self.queue[0]
        self.position = 0

        self._play()

    def _play(self):
        url = self.current["url"]

        source = discord.FFmpegPCMAudio(
            url,
            before_options=f"-ss {self.position} -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn"
        )

        self.guild.voice_client.play(
            source,
            after=lambda e: self.bot.loop.create_task(self.after())
        )

    async def after(self):
        if not self.loop:
            self.queue.pop(0)
        await self.play_next()

    def seek(self, seconds: int):
        self.position = seconds
        self.guild.voice_client.stop()

    def shuffle(self):
        random.shuffle(self.queue)

    def queue_text(self):
        if not self.queue:
            return "Fila vazia"
        return "\n".join(
            f"{i+1}. {x['title']}" for i, x in enumerate(self.queue)
        )
