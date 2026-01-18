import os
import requests
from flask import Flask, redirect, request, session, render_template, jsonify
from dotenv import load_dotenv
from functools import wraps

from database import log_action, get_logs

load_dotenv()

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
BOT_OWNERS = [int(x) for x in os.getenv("BOT_OWNERS", "").split(",") if x]

API = "https://discord.com/api"

def run_dashboard(bot):
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET")

    def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if "token" not in session:
                return redirect("/")
            return f(*args, **kwargs)
        return wrap

    def admin_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            user = api_get("/users/@me")
            if int(user["id"]) not in BOT_OWNERS:
                return "Acesso negado", 403
            return f(*args, **kwargs)
        return wrap

    def api_get(endpoint):
        return requests.get(
            f"{API}{endpoint}",
            headers={"Authorization": f"Bearer {session['token']}"}
        ).json()

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
                "scope": "identify guilds"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ).json()

        session["token"] = token["access_token"]
        return redirect("/guilds")

    @app.route("/guilds")
    @login_required
    def guilds():
        guilds = api_get("/users/@me/guilds")
        return render_template("guilds.html", guilds=guilds)

    @app.route("/guild/<gid>")
    @login_required
    def panel(gid):
        return render_template("panel.html", guild_id=gid)

    @app.route("/admin")
    @login_required
    @admin_required
    def admin_panel():
        return render_template(
            "admin.html",
            guilds=bot.guilds,
            logs=get_logs()
        )

    @app.route("/api/control", methods=["POST"])
    @login_required
    def control():
        data = request.json
        gid = int(data["guild"])
        action = data["action"]

        user = api_get("/users/@me")

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

        bot.loop.create_task(task())

        log_action(
            user_id=int(user["id"]),
            guild_id=gid,
            action=action
        )

        return {"ok": True}

    print("🌐 Dashboard online")
    app.run(host="0.0.0.0", port=10000)
