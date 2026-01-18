import discord
from discord.ext import commands
import wavelink
import yt_dlp
import asyncio

from bot_state import get_state
from database import get_guild_config, update_guild_config

YTDL_OPTS = {
    "format": "bestaudio",
    "quiet": True,
    "default_search": "ytsearch",
    "noplaylist": True,
}

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure_vc(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Entre em um canal de voz.")
            return None

        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect()

        return vc

    # ===================== PLAY =====================
    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, query: str):
        vc = await self.ensure_vc(ctx)
        if not vc:
            return

        state = get_state(ctx.guild.id)

        # 🔹 tenta Lavalink primeiro
        try:
            track = await wavelink.YouTubeTrack.search(query, return_first=True)
            player: wavelink.Player = ctx.voice_client

            if not isinstance(player, wavelink.Player):
                player = await ctx.author.voice.channel.connect(cls=wavelink.Player)

            await player.play(track)
            await player.set_volume(state["volume"])

            embed = discord.Embed(
                title="🎵 Tocando agora (Lavalink)",
                description=track.title,
                color=0x5865F2
            )
            await ctx.send(embed=embed)
            return

        except Exception:
            pass  # cai pro yt-dlp

        # 🔹 yt-dlp fallback
        await ctx.send("⚠️ Usando fallback yt-dlp...")

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(YTDL_OPTS).extract_info(query, download=False)
        )

        if "entries" in data:
            data = data["entries"][0]

        url = data["url"]
        title = data.get("title", "Desconhecido")

        vc.play(
            discord.FFmpegPCMAudio(url, **FFMPEG_OPTS)
        )

        embed = discord.Embed(
            title="🎵 Tocando agora (yt-dlp)",
            description=title,
            color=0xED4245
        )
        await ctx.send(embed=embed)

    # ===================== VOLUME =====================
    @commands.command(name="volume")
    async def volume(self, ctx, vol: int):
        if not ctx.voice_client:
            return

        vol = max(1, min(vol, 200))

        vc = ctx.voice_client
        if isinstance(vc, wavelink.Player):
            await vc.set_volume(vol)

        update_guild_config(ctx.guild.id, volume=vol)
        get_state(ctx.guild.id)["volume"] = vol

        await ctx.send(f"🔊 Volume definido para **{vol}%**")

    # ===================== LOOP =====================
    @commands.command(name="loop")
    async def loop(self, ctx):
        config = get_guild_config(ctx.guild.id)
        new_state = not config.loop_queue

        update_guild_config(ctx.guild.id, loop_queue=new_state)
        get_state(ctx.guild.id)["loop"] = new_state

        await ctx.send(
            "🔁 Loop da fila **ativado**" if new_state else "⏹ Loop da fila **desativado**"
        )

async def setup(bot):
    await bot.add_cog(Music(bot))
