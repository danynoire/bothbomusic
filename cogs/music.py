import discord
from discord.ext import commands
from discord import app_commands
import wavelink

from bot_state import (
    get_state, add_to_queue, pop_queue,
    set_playing, set_paused, toggle_loop, set_current
)

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

    async def play_next(self, vc: wavelink.Player, guild_id: int):
        state = get_state(guild_id)

        if state["loop"] and state["current"]:
            await vc.play(state["current"])
            return

        track = pop_queue(guild_id)
        if not track:
            set_playing(guild_id, False)
            return

        set_current(guild_id, track)
        await vc.play(track)

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, search: str):
        vc = await self.ensure_voice(ctx)
        if not vc:
            return

        track = await wavelink.YouTubeTrack.search(search, return_first=True)
        add_to_queue(ctx.guild.id, track)

        state = get_state(ctx.guild.id)
        if not vc.playing:
            await self.play_next(vc, ctx.guild.id)
            set_playing(ctx.guild.id, True)

        embed = discord.Embed(
            title="🎵 Música adicionada",
            description=f"**{track.title}**",
            color=0x2ecc71
        )
        await ctx.send(embed=embed)

    @commands.command(name="pause")
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc:
            vc.pause()
            set_paused(ctx.guild.id, True)
            await ctx.send("⏸ Pausado")

    @commands.command(name="resume")
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc:
            vc.resume()
            set_paused(ctx.guild.id, False)
            await ctx.send("▶️ Continuando")

    @commands.command(name="skip")
    async def skip(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.stop()
            await self.play_next(vc, ctx.guild.id)
            await ctx.send("⏭ Pulado")

    @commands.command(name="loop")
    async def loop(self, ctx):
        enabled = toggle_loop(ctx.guild.id)
        await ctx.send(f"🔁 Loop {'ativado' if enabled else 'desativado'}")

    # ---------- SLASH ----------

    @app_commands.command(name="loop", description="Ativa/desativa loop da fila")
    async def slash_loop(self, interaction: discord.Interaction):
        enabled = toggle_loop(interaction.guild.id)
        await interaction.response.send_message(
            f"🔁 Loop {'ativado' if enabled else 'desativado'}",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Music(bot))
