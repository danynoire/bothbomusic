import wavelink
from discord.ext import commands
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

    @commands.command()
    async def play(self, ctx, *, query: str):
        if not ctx.voice_client:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc = ctx.voice_client

        track = await wavelink.Playable.search(query, source=wavelink.TrackSource.YouTube)
        await vc.play(track[0])
        await ctx.send(f"▶️ Tocando **{track[0].title}**")

def setup(bot):
    bot.add_cog(Music(bot))
