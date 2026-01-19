import os
from flask import Flask, render_template, jsonify, request
from functools import wraps

from bot_state import get_state
from database import save_guild_config

BOT_OWNERS = [int(x) for x in os.getenv("BOT_OWNERS", "").split(",") if x]
DASHBOARD_TOKEN = os.getenv("DASHBOARD_TOKEN", "admin123")


def run_dashboard(bot):
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET", "secret")

    # ───────────────────────────────
    # 🔐 Auth simples por token
    # ───────────────────────────────
    def admin_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get("X-Admin-Token")
            if token != DASHBOARD_TOKEN:
                return {"error": "unauthorized"}, 403
            return f(*args, **kwargs)
        return wrapper

    # ───────────────────────────────
    # 🏠 Home
    # ───────────────────────────────
    @app.route("/")
    def home():
        return render_template("index.html")

    # ───────────────────────────────
    # 📊 Estado do bot
    # ───────────────────────────────
    @app.route("/api/status")
    def status():
        return jsonify({
            "online": bot.is_ready(),
            "guilds": len(bot.guilds),
            "latency": round(bot.latency * 1000) if bot.is_ready() else None
        })

    # ───────────────────────────────
    # 📊 Estado de uma guild
    # ───────────────────────────────
    @app.route("/api/state/<int:gid>")
    def state(gid):
        return jsonify(get_state(gid))

    # ───────────────────────────────
    # 🎛️ Controle do bot
    # ───────────────────────────────
    @app.route("/api/control", methods=["POST"])
    @admin_required
    def control():
        data = request.json
        gid = int(data["guild"])
        action = data["action"]
        value = data.get("value")

        async def task():
            guild = bot.get_guild(gid)
            if not guild or not guild.voice_client:
                return

            vc = guild.voice_client

            if action == "pause":
                vc.pause()

            elif action == "resume":
                vc.resume()

            elif action == "skip":
                await vc.stop()

            elif action == "volume":
                vol = max(0, min(200, int(value)))
                await vc.set_volume(vol)
                save_guild_config(gid, volume=vol)

            elif action == "disconnect":
                await vc.disconnect()

        bot.loop.create_task(task())
        return {"ok": True}

    # ───────────────────────────────
    print("🌐 Dashboard iniciado (SEM OAuth)")
    app.run(host="0.0.0.0", port=10000)
