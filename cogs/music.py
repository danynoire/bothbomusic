import os
import wavelink
from discord.ext import commands

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

    @commands.hybrid_command(name="play", description="Tocar música")
    async def play(self, ctx, *, query: str):
        if not ctx.voice_client:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc = ctx.voice_client

        tracks = await wavelink.Playable.search(query)
        await vc.play(tracks[0])
        await ctx.send(f"▶️ Tocando **{tracks[0].title}**")

    @commands.hybrid_command(name="loop", description="Definir loop (queue/track/none)")
    async def loop(self, ctx, mode: str):
        vc = ctx.voice_client
        if mode.lower() == "queue":
            vc.queue.mode = wavelink.QueueMode.loop
            msg = "🔁 Loop na fila"
        elif mode.lower() == "track":
            vc.queue.mode = wavelink.QueueMode.loop_track
            msg = "🔂 Loop na música"
        else:
            vc.queue.mode = wavelink.QueueMode.none
            msg = "⏹ Loop desligado"
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Music(bot))
