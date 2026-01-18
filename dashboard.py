import os
import requests
from flask import Flask, redirect, request, session, render_template, jsonify
from dotenv import load_dotenv
from functools import wraps

from bot_state import get_state
from database import (
    save_guild_config,
    SessionLocal,
    GuildConfig
)

load_dotenv()

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
BOT_OWNERS = [int(x) for x in os.getenv("BOT_OWNERS", "").split(",") if x]

API = "https://discord.com/api"


def run_dashboard(bot):
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET")

    # ======================
    # Helpers
    # ======================

    def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if "token" not in session:
                return redirect("/")
            return f(*args, **kwargs)
        return wrap

    def api_get(endpoint):
        return requests.get(
            f"{API}{endpoint}",
            headers={"Authorization": f"Bearer {session['token']}"}
        ).json()

    def is_owner():
        user = api_get("/users/@me")
        return int(user["id"]) in BOT_OWNERS

    # ======================
    # Rotas públicas
    # ======================

    @app.route("/")
    def home():
        return render_template("login.html")

    @app.route("/login")
    def login():
        return redirect(
            f"{API}/oauth2/authorize"
            f"?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=identify guilds"
        )

    @app.route("/callback")
    def callback():
        code = request.args.get("code")

        token = requests.post(
            f"{API}/oauth2/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ).json()

        session["token"] = token["access_token"]
        return redirect("/guilds")

    # ======================
    # Guilds do usuário
    # ======================

    @app.route("/guilds")
    @login_required
    def guilds():
        guilds = api_get("/users/@me/guilds")
        return render_template("guilds.html", guilds=guilds)

    # ======================
    # Painel Admin Global
    # ======================

    @app.route("/admin")
    @login_required
    def admin():
        if not is_owner():
            return "Acesso negado", 403

        db = SessionLocal()
        guilds_db = db.query(GuildConfig).all()
        db.close()

        total_bot_guilds = len(bot.guilds)
        registered = len(guilds_db)

        playing = 0
        paused = 0
        volumes = []

        for g in guilds_db:
            state = get_state(g.guild_id)
            if state["playing"]:
                playing += 1
            if state["paused"]:
                paused += 1
            volumes.append(g.volume)

        avg_volume = int(sum(volumes) / len(volumes)) if volumes else 0

        stats = {
            "total_bot_guilds": total_bot_guilds,
            "registered": registered,
            "playing": playing,
            "paused": paused,
            "avg_volume": avg_volume
        }

        return render_template(
            "admin.html",
            guilds=guilds_db,
            stats=stats
        )

    # ======================
    # Painel por guild
    # ======================

    @app.route("/guild/<gid>")
    @login_required
    def panel(gid):
        return render_template("panel.html", guild_id=gid)

    # ======================
    # API Estado
    # ======================

    @app.route("/api/state/<gid>")
    def state(gid):
        return jsonify(get_state(int(gid)))

    # ======================
    # API Controle individual
    # ======================

    @app.route("/api/control", methods=["POST"])
    @login_required
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
                await vc.pause()
            elif action == "resume":
                await vc.resume()
            elif action == "skip":
                await vc.stop()
            elif action == "volume":
                await vc.set_volume(int(value))
                save_guild_config(gid, volume=int(value))
            elif action == "seek":
                await vc.seek(int(value) * 1000)

        bot.loop.create_task(task())
        return {"ok": True}

    # ======================
    # API Controle GLOBAL (ADMIN)
    # ======================

    @app.route("/api/admin/control", methods=["POST"])
    @login_required
    def admin_control():
        if not is_owner():
            return {"error": "unauthorized"}, 403

        action = request.json.get("action")

        async def task():
            for guild in bot.guilds:
                vc = guild.voice_client
                if not vc:
                    continue

                if action == "pause_all":
                    await vc.pause()

                elif action == "resume_all":
                    await vc.resume()

                elif action == "skip_all":
                    await vc.stop()

                elif action == "disable_loop_all":
                    save_guild_config(guild.id, loop=False)

        bot.loop.create_task(task())
        return {"ok": True}

    print("🌐 Dashboard online")
    app.run(host="0.0.0.0", port=10000)
