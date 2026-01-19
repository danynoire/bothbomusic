import os
from flask import Flask, request, jsonify, render_template
from bot_state import get_state
from database import get_all_guilds, save_guild_config

DASHBOARD_TOKEN = os.getenv("DASHBOARD_TOKEN")
FLASK_SECRET = os.getenv("FLASK_SECRET", "dev")

def run_dashboard(bot):
    app = Flask(__name__)
    app.secret_key = FLASK_SECRET

    # 🔒 proteção simples por token
    def check_token(req):
        token = req.headers.get("Authorization")
        return token == DASHBOARD_TOKEN

    @app.route("/")
    def home():
        return render_template("login.html")

    @app.route("/panel")
    def panel():
        return render_template("panel.html")

    @app.route("/admin")
    def admin():
        return render_template("admin.html")

    # 📊 estado de uma guild
    @app.route("/api/state/<int:gid>")
    def state(gid):
        return jsonify(get_state(gid))

    # 📈 estatísticas globais
    @app.route("/api/stats")
    def stats():
        guilds = bot.guilds
        voice = sum(1 for g in guilds if g.voice_client)
        return jsonify({
            "guilds": len(guilds),
            "voice_connections": voice,
            "users": sum(g.member_count for g in guilds)
        })

    # ⚙️ controles do bot
    @app.route("/api/control", methods=["POST"])
    def control():
        if not check_token(request):
            return {"error": "unauthorized"}, 403

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
                await vc.set_volume(int(value))
                save_guild_config(gid, volume=int(value))
            elif action == "seek":
                await vc.seek(int(value) * 1000)

        bot.loop.create_task(task())
        return {"ok": True}

    print("🌐 Dashboard online (sem OAuth)")
    app.run(host="0.0.0.0", port=10000)
