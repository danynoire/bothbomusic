import discord
from discord.ext import commands
import wavelink
import os

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not wavelink.Pool.nodes:
            await wavelink.Pool.connect(
                client=self.bot,
                nodes=[
                    wavelink.Node(
                        uri=f"https://{os.getenv('LAVALINK_HOST')}",
                        password=os.getenv("LAVALINK_PASSWORD")
                    )
                ]
            )
            print("🎵 Lavalink conectado")

    @commands.command(name="play")
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            return await ctx.send("❌ Você precisa estar em um canal de voz.")

        # conecta na call
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        tracks = await wavelink.Playable.search(query)

        if not tracks:
            return await ctx.send("❌ Música não encontrada.")

        track = tracks[0]
        await vc.play(track)

        await ctx.send(f"▶️ Tocando **{track.title}**")

    @commands.command()
    async def volume(self, ctx, vol: int):
        vc: wavelink.Player = ctx.voice_client
        if not vc:
            return await ctx.send("❌ Não estou em call.")

        await vc.set_volume(vol)
        await ctx.send(f"🔊 Volume definido para **{vol}%**")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ Sai da call.")

async def setup(bot):
    await bot.add_cog(Music(bot))
