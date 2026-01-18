import discord
from discord.ext import commands
import wavelink

from bot_state import (
    get_state,
    toggle_loop,
    add_to_queue,
    pop_queue,
    set_current
)
from database import save_guild_config


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure_voice(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Entre em um canal de voz.")
            return None

        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

        return vc

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, search: str):
        vc = await self.ensure_voice(ctx)
        if not vc:
            return

        track = await wavelink.YouTubeTrack.search(search, return_first=True)
        state = get_state(ctx.guild.id)

        if vc.is_playing():
            add_to_queue(ctx.guild.id, track)
            await ctx.send(f"➕ Adicionado à fila: **{track.title}**")
        else:
            await vc.play(track)
            set_current(ctx.guild.id, track.title)
            await ctx.send(f"🎵 Tocando: **{track.title}**")

    @commands.command(name="loop")
    async def loop_queue(self, ctx, mode: str = None):
        """
        hb!loop queue
        """
        if mode != "queue":
            return await ctx.send("❌ Use: `hb!loop queue`")

        enabled = toggle_loop(ctx.guild.id)
        save_guild_config(ctx.guild.id, loop=enabled)

        await ctx.send(
            f"🔁 Loop da fila {'ativado' if enabled else 'desativado'}"
        )

    @commands.command(name="skip")
    async def skip(self, ctx):
        vc = ctx.voice_client
        if not vc:
            return

        await vc.stop()
        await ctx.send("⏭ Música pulada")

    @commands.command(name="stop")
    async def stop(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.disconnect()
            await ctx.send("⏹ Player parado")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = payload.player
        guild_id = player.guild.id
        state = get_state(guild_id)

        next_track = pop_queue(guild_id)

        if next_track:
            await player.play(next_track)
            set_current(guild_id, next_track.title)
            return

        if state["loop"] and payload.track:
            await player.play(payload.track)
            return


async def setup(bot):
    await bot.add_cog(Music(bot))
