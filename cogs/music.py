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
                        uri=f"http://{os.getenv('LAVALINK_HOST')}:{os.getenv('LAVALINK_PORT')}",
                        password=os.getenv("LAVALINK_PASSWORD")
                    )
                ]
            )
            print("🎵 Lavalink conectado")

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, query: str):
        # usuário precisa estar em call
        if not ctx.author.voice:
            return await ctx.send("❌ Você precisa estar em um canal de voz.")

        # conecta o bot
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(
                cls=wavelink.Player
            )
        else:
            vc: wavelink.Player = ctx.voice_client

        # busca música
        tracks = await wavelink.Playable.search(query)
        if not tracks:
            return await ctx.send("❌ Música não encontrada.")

        track = tracks[0]
        await vc.play(track)

        embed = discord.Embed(
            title="🎶 Tocando agora",
            description=f"**{track.title}**",
            color=0x2b2d31
        )
        embed.set_footer(text=f"Pedido por {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ Desconectado.")

async def setup(bot):
    await bot.add_cog(Music(bot))
