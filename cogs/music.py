import discord
from discord.ext import commands
import wavelink
import time

from bot_state import guild_states
from database import get_guild_config, save_guild_config

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_times = {}

    async def get_player(self, ctx):
        if not ctx.voice_client:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

            cfg = get_guild_config(ctx.guild.id)
            await vc.set_volume(cfg["volume"])

            return vc
        return ctx.voice_client

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send("❌ Entre em um canal de voz")

        vc = await self.get_player(ctx)
        track = await wavelink.YouTubeTrack.search(search, return_first=True)

        await vc.play(track)
        self.start_times[ctx.guild.id] = time.time()

        cfg = get_guild_config(ctx.guild.id)

        guild_states[ctx.guild.id] = {
            "track": track.title,
            "url": track.uri,
            "paused": False,
            "volume": vc.volume,
            "position": 0,
            "duration": track.length,
            "loop_queue": cfg["loop_queue"]
        }

        embed = discord.Embed(
            title="🎶 Tocando agora",
            description=f"[{track.title}]({track.uri})",
            color=0x5865F2
        )
        await ctx.send(embed=embed)

    # 🔊 VOLUME (BANCO)
    @commands.command()
    async def volume(self, ctx, vol: int):
        vc = ctx.voice_client
        if not vc:
            return

        vol = max(1, min(vol, 100))
        await vc.set_volume(vol)

        save_guild_config(ctx.guild.id, volume=vol)

        guild_states.setdefault(ctx.guild.id, {})["volume"] = vol

        await ctx.send(f"🔊 Volume salvo: **{vol}%**")

    # 🔁 LOOP FILA (BANCO)
    @commands.command()
    async def loop(self, ctx):
        cfg = get_guild_config(ctx.guild.id)
        new_state = not cfg["loop_queue"]

        save_guild_config(ctx.guild.id, loop_queue=new_state)

        guild_states.setdefault(ctx.guild.id, {})["loop_queue"] = new_state

        estado = "ativado 🔁" if new_state else "desativado ❌"
        await ctx.send(f"Loop da fila **{estado}**")

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.pause()
            guild_states[ctx.guild.id]["paused"] = True
            await ctx.send("⏸ Pausado")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.resume()
            guild_states[ctx.guild.id]["paused"] = False
            self.start_times[ctx.guild.id] = time.time()
            await ctx.send("▶️ Retomado")

    @commands.command()
    async def seek(self, ctx, seconds: int):
        vc = ctx.voice_client
        if not vc:
            return

        await vc.seek(seconds * 1000)
        self.start_times[ctx.guild.id] = time.time() - seconds
        guild_states[ctx.guild.id]["position"] = seconds

        await ctx.send(f"⏩ Avançado para {seconds}s")

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.stop()
            await ctx.send("⏭ Pulado")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            guild_states.pop(ctx.guild.id, None)
            await ctx.send("⏹ Desconectado")

async def setup(bot):
    await bot.add_cog(Music(bot))
