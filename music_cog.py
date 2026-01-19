import discord
from discord.ext import commands
from discord import app_commands
from player import MusicPlayer

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def get_player(self, guild):
        if guild.id not in self.players:
            self.players[guild.id] = MusicPlayer(self.bot, guild)
        return self.players[guild.id]

    async def ensure_voice(self, ctx):
        if ctx.author.voice is None:
            raise commands.CommandError("Entre em um canal de voz.")

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()

    # ======================
    # PLAY
    # ======================
    @commands.hybrid_command(name="play", description="Tocar música")
    async def play(self, ctx, *, query: str):
        await self.ensure_voice(ctx)
        player = self.get_player(ctx.guild)
        await player.add(query)
        await ctx.reply(f"🎶 Adicionado: `{query}`")

    # ======================
    # PAUSE / RESUME
    # ======================
    @commands.hybrid_command()
    async def pause(self, ctx):
        ctx.voice_client.pause()
        await ctx.reply("⏸ Pausado")

    @commands.hybrid_command()
    async def resume(self, ctx):
        ctx.voice_client.resume()
        await ctx.reply("▶️ Retomado")

    # ======================
    # SKIP / STOP
    # ======================
    @commands.hybrid_command()
    async def skip(self, ctx):
        ctx.voice_client.stop()
        await ctx.reply("⏭ Pulou")

    @commands.hybrid_command()
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()
        await ctx.reply("⏹ Desconectado")

    # ======================
    # QUEUE
    # ======================
    @commands.hybrid_command()
    async def queue(self, ctx):
        player = self.get_player(ctx.guild)
        await ctx.reply(player.queue_text())

    # ======================
    # VOLUME
    # ======================
    @commands.hybrid_command()
    async def volume(self, ctx, value: int):
        ctx.voice_client.source.volume = value / 100
        await ctx.reply(f"🔊 Volume: {value}%")

    # ======================
    # SEEK
    # ======================
    @commands.hybrid_command()
    async def seek(self, ctx, seconds: int):
        player.seek(seconds)
        await ctx.reply(f"⏩ Pulou para {seconds}s")

    # ======================
    # LOOP / SHUFFLE
    # ======================
    @commands.hybrid_command()
    async def loop(self, ctx):
        player = self.get_player(ctx.guild)
        player.loop = not player.loop
        await ctx.reply(f"🔁 Loop {'ativado' if player.loop else 'desativado'}")

    @commands.hybrid_command()
    async def shuffle(self, ctx):
        player = self.get_player(ctx.guild)
        player.shuffle()
        await ctx.reply("🔀 Fila embaralhada")

async def setup(bot):
    await bot.add_cog(Music(bot))
