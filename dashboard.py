import os
from flask import Flask, request, abort, jsonify, render_template
from functools import wraps

from bot_state import get_state
from database import save_guild_config

def run_dashboard(bot):
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET")

    DASHBOARD_TOKEN = os.getenv("DASHBOARD_TOKEN")
    BOT_OWNERS = [int(x) for x in os.getenv("BOT_OWNERS", "").split(",") if x]

    # =========================
    # AUTH POR TOKEN
    # =========================
    def token_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            token = (
                request.headers.get("X-Dashboard-Token")
                or request.args.get("token")
            )

            if not token or token != DASHBOARD_TOKEN:
                abort(403)

            return f(*args, **kwargs)
        return wrap

    # =========================
    # ROTAS HTML
    # =========================
    @app.route("/")
    @token_required
    def home():
        return render_template("index.html")

    @app.route("/admin")
    @token_required
    def admin():
        return render_template("admin.html")

    @app.route("/guild/<int:gid>")
    @token_required
    def panel(gid):
        return render_template("panel.html", guild_id=gid)

    # =========================
    # API – ESTADO
    # =========================
    @app.route("/api/state/<int:gid>")
    @token_required
    def state(gid):
        return jsonify(get_state(gid))

    # =========================
    # API – CONTROLES DO BOT
    # =========================
    @app.route("/api/control", methods=["POST"])
    @token_required
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
                await vc.set_volume(int(value))
                save_guild_config(gid, volume=int(value))

            elif action == "seek":
                await vc.seek(int(value) * 1000)

        bot.loop.create_task(task())
        return {"ok": True}

    # =========================
    # API – ADMIN GLOBAL
    # =========================
    @app.route("/api/admin/stats")
    @token_required
    def admin_stats():
        return {
            "guilds": len(bot.guilds),
            "users": sum(g.member_count for g in bot.guilds),
            "voice_clients": len(bot.voice_clients)
        }

    # =========================
    # START
    # =========================
    port = int(os.environ.get("PORT", 10000))
    print("🌐 Dashboard online (TOKEN, sem OAuth)")
    app.run(host="0.0.0.0", port=port)
