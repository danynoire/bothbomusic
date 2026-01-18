from flask import Flask, render_template_string
import asyncio

def run_dashboard(bot):
    app = Flask(__name__)

    TEMPLATE = """
    <h1>🎧 Bot Dashboard</h1>
    <p><b>Bot:</b> {{ bot.user }}</p>

    {% for guild in bot.guilds %}
      <h3>{{ guild.name }}</h3>
      {% if guild.voice_client %}
        <p>🎵 Tocando: {{ guild.voice_client.track.title }}</p>
        <p>🔊 Volume: {{ guild.voice_client.volume }}%</p>
      {% else %}
        <p>⏸ Nada tocando</p>
      {% endif %}
    {% endfor %}
    """

    @app.route("/")
    def index():
        return render_template_string(TEMPLATE, bot=bot)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, app.run, "0.0.0.0", 5000)
