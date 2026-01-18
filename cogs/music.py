import discord
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send("❌ Entre em um canal de voz.")

        vc: wavelink.Player = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

        track = await wavelink.YouTubeTrack.search(search, return_first=True)
        await vc.play(track)
        await ctx.send(f"🎵 Tocando: **{track.title}**")

    @commands.command(name="volume")
    async def volume(self, ctx, vol: int):
        vc: wavelink.Player = ctx.voice_client
        if not vc:
            return
        await vc.set_volume(vol)
        await ctx.send(f"🔊 Volume: {vol}%")

    @commands.command(name="skip")
    async def skip(self, ctx):
        vc: wavelink.Player = ctx.voice_client
        if vc:
            await vc.stop()
            await ctx.send("⏭ Pulado")

    @commands.command(name="stop")
    async def stop(self, ctx):
        vc: wavelink.Player = ctx.voice_client
        if vc:
            await vc.disconnect()
            await ctx.send("⏹ Parado")

async def setup(bot):
    await bot.add_cog(Music(bot))
