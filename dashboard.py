import os
import requests
from flask import Flask, redirect, request, session, render_template, jsonify
from dotenv import load_dotenv
from functools import wraps

from bot_state import get_state
from database import save_guild_config

load_dotenv()

# ================== CONFIG ==================

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
FLASK_SECRET = os.getenv("FLASK_SECRET")

BOT_OWNERS = [
    int(x) for x in os.getenv("BOT_OWNERS", "").split(",") if x
]

API = "https://discord.com/api"

# ============================================


def run_dashboard(bot):
    app = Flask(__name__)
    app.secret_key = FLASK_SECRET

    # ----------- HELPERS -----------

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
            headers={
                "Authorization": f"Bearer {session['token']}"
            }
        ).json()

    # ----------- ROTAS -----------

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
            f"&scope=identify%20guilds"
        )

    # ===== CALLBACK OAUTH2 (CRÍTICO) =====
    @app.route("/callback")
    def callback():
        code = request.args.get("code")
        if not code:
            return "Código OAuth não recebido", 400

        r = requests.post(
            f"{API}/oauth2/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "scope": "identify guilds",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )

        if r.status_code != 200:
            return f"<pre>OAuth ERROR:\n{r.text}</pre>", 400

        token = r.json()
        session["token"] = token["access_token"]
        return redirect("/guilds")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/")

    @app.route("/guilds")
    @login_required
    def guilds():
        guilds = api_get("/users/@me/guilds")
        return render_template("guilds.html", guilds=guilds)

    # ----------- ADMIN GLOBAL -----------

    @app.route("/admin")
    @login_required
    def admin():
        user = api_get("/users/@me")
        if int(user["id"]) not in BOT_OWNERS:
            return "Acesso negado", 403

        guilds_data = []
        for g in bot.guilds:
            state = get_state(g.id)
            guilds_data.append({
                "guild_id": g.id,
                "name": g.name,
                "playing": state["playing"],
                "paused": state["paused"],
                "volume": state["volume"],
                "loop": state["loop"],
                "queue_size": len(state["queue"]),
            })

        return render_template("admin.html", guilds=guilds_data)

    # ----------- PAINEL POR GUILD -----------

    @app.route("/guild/<int:gid>")
    @login_required
    def panel(gid):
        return render_template("panel.html", guild_id=gid)

    # ----------- API -----------

    @app.route("/api/state/<int:gid>")
    def state(gid):
        return jsonify(get_state(gid))

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

            elif action == "loop_queue":
                # equivalente a: hb!loop queue
                state = get_state(gid)
                state["loop"] = not state["loop"]

        bot.loop.create_task(task())
        return jsonify({"ok": True})

    # ----------- START -----------

    print("🌐 Dashboard iniciando...")
    app.run(host="0.0.0.0", port=10000)
