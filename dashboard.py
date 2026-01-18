import os, requests
from flask import Flask, redirect, request, session, render_template, jsonify
from functools import wraps
from dotenv import load_dotenv

from database import get_guild_config, get_all_guilds
from bot_state import get_state

load_dotenv()

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
BOT_OWNERS = os.getenv("BOT_OWNERS", "").split(",")

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

    @app.route("/guild/<int:gid>")
    @login_required
    def panel(gid):
        cfg = get_guild_config(gid)
        state = get_state(gid)
        return render_template("panel.html", guild_id=gid, cfg=cfg, state=state)

    # 🔥 PAINEL ADMIN GLOBAL
    @app.route("/admin")
    @login_required
    def admin():
        user = api_get("/users/@me")
        if user["id"] not in BOT_OWNERS:
            return "Acesso negado", 403

        guilds = get_all_guilds()
        return render_template("admin.html", guilds=guilds)

    print("🌐 Dashboard online")
    app.run(host="0.0.0.0", port=10000)
