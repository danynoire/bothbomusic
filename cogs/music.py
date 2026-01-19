import os
import discord
import wavelink
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =========================
    # LAVALINK CONNECT
    # =========================
    @commands.Cog.listener()
    async def on_ready(self):
        if not wavelink.Pool.nodes:
            await wavelink.Pool.connect(
                client=self.bot,
                nodes=[
                    wavelink.Node(
                        uri=f"http://{os.getenv('LAVALINK_HOST')}:{os.getenv('LAVALINK_PORT')}",
                        password=os.getenv("LAVALINK_PASSWORD"),
                        identifier="MAIN"
                    )
                ]
            )
            print("🎵 Lavalink conectado com sucesso")

    # =========================
    # PLAY
    # =========================
    @commands.hybrid_command(name="play", description="Tocar uma música")
    async def play(self, ctx: commands.Context, *, query: str):
        await ctx.defer()

        # usuário precisa estar em call
        if not ctx.author.voice:
            return await ctx.send("❌ Você precisa estar em um canal de voz.")

        # conecta ou pega player
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        # busca música
        tracks = await wavelink.Playable.search(query)
        if not tracks:
            return await ctx.send("❌ Nenhuma música encontrada.")

        track = tracks[0]

        # adiciona à fila
        await vc.queue.put_wait(track)

        # se não estiver tocando, toca
        if not vc.playing:
            next_track = await vc.queue.get_wait()
            await vc.play(next_track)

        embed = discord.Embed(
            title="🎶 Música adicionada",
            description=f"**{track.title}**",
            color=discord.Color.purple()
        )
        embed.add_field(name="⏱ Duração", value=str(track.length // 1000) + "s")
        embed.add_field(name="📜 Fila", value=f"{vc.queue.count} músicas")
        await ctx.send(embed=embed)

    # =========================
    # SKIP
    # =========================
    @commands.hybrid_command(name="skip", description="Pular música atual")
    async def skip(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if not vc or not vc.playing:
            return await ctx.send("❌ Nada tocando.")

        await vc.stop()
        await ctx.send("⏭ Música pulada.")

    # =========================
    # PAUSE / RESUME
    # =========================
    @commands.hybrid_command(name="pause", description="Pausar música")
    async def pause(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if vc and vc.playing:
            await vc.pause()
            await ctx.send("⏸ Música pausada.")

    @commands.hybrid_command(name="resume", description="Retomar música")
    async def resume(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if vc and vc.paused:
            await vc.resume()
            await ctx.send("▶️ Música retomada.")

    # =========================
    # VOLUME
    # =========================
    @commands.hybrid_command(name="volume", description="Definir volume (0–150)")
    async def volume(self, ctx: commands.Context, value: int):
        vc: wavelink.Player = ctx.voice_client
        if not vc:
            return await ctx.send("❌ Bot não está em call.")

        value = max(0, min(150, value))
        await vc.set_volume(value)
        await ctx.send(f"🔊 Volume definido para **{value}%**")

    # =========================
    # LOOP
    # =========================
    @commands.hybrid_command(name="loop", description="Loop: queue | track | off")
    async def loop(self, ctx: commands.Context, mode: str):
        vc: wavelink.Player = ctx.voice_client
        if not vc:
            return await ctx.send("❌ Bot não está em call.")

        mode = mode.lower()
        if mode == "queue":
            vc.queue.mode = wavelink.QueueMode.loop
            msg = "🔁 Loop da fila ativado"
        elif mode == "track":
            vc.queue.mode = wavelink.QueueMode.loop_track
            msg = "🔂 Loop da música ativado"
        else:
            vc.queue.mode = wavelink.QueueMode.none
            msg = "⏹ Loop desativado"

        await ctx.send(msg)

    # =========================
    # QUEUE
    # =========================
    @commands.hybrid_command(name="queue", description="Ver fila")
    async def queue(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if not vc or vc.queue.is_empty:
            return await ctx.send("📭 A fila está vazia.")

        desc = ""
        for i, track in enumerate(vc.queue, start=1):
            desc += f"**{i}.** {track.title}\n"

        embed = discord.Embed(
            title="📜 Fila de músicas",
            description=desc[:4000],
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)

    # =========================
    # STOP
    # =========================
    @commands.hybrid_command(name="stop", description="Parar e sair da call")
    async def stop(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if vc:
            await vc.disconnect()
            await ctx.send("⏹ Música parada e saí da call.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
