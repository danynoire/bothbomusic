import discord
from discord.ext import commands
from discord import app_commands
import wavelink
from collections import deque

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.looping = set()

    # ======================
    # 🔧 HELPERS
    # ======================
    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    async def play_next(self, vc: wavelink.Player):
        queue = self.get_queue(vc.guild.id)

        if vc.guild.id in self.looping and vc.current:
            await vc.play(vc.current)
            return

        if not queue:
            return

        track = queue.popleft()
        await vc.play(track)

    def embed(self, title, desc, color):
        return discord.Embed(
            title=title,
            description=desc,
            color=color
        )

    # ======================
    # 🎵 PREFIX PLAY
    # ======================
    @commands.command(name="play", aliases=["p"])
    async def play_prefix(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send(
                embed=self.embed(
                    "❌ Erro",
                    "Entre em um canal de voz primeiro.",
                    discord.Color.red()
                )
            )

        vc: wavelink.Player = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

        tracks = await wavelink.Playable.search(search)
        if not tracks:
            return await ctx.send(
                embed=self.embed(
                    "❌ Não encontrado",
                    "Nenhuma música encontrada.",
                    discord.Color.red()
                )
            )

        track = tracks[0]
        queue = self.get_queue(ctx.guild.id)

        if vc.is_playing():
            queue.append(track)
            await ctx.send(
                embed=self.embed(
                    "➕ Adicionado à fila",
                    f"**{track.title}**",
                    discord.Color.blue()
                )
            )
        els
