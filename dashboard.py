import os
import requests
from flask import Flask, redirect, request, session, render_template, jsonify
from functools import wraps

API = "https://discord.com/api"

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
FLASK_SECRET = os.getenv("FLASK_SECRET", "dev")

def run_dashboard(bot):
    app = Flask(__name__)
    app.secret_key = FLASK_SECRET

    # ========================
    # HELPERS
    # ========================

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

    # ========================
    # ROTAS
    # ========================

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

        if not code:
            return "Código OAuth inválido", 400

        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "scope": "identify guilds"
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        token_res = requests.post(
            f"{API}/oauth2/token",
            data=data,
            headers=headers
        ).json()

        session["token"] = token_res.get("access_token")
        return redirect("/dashboard")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = api_get("/users/@me")
        guilds = api_get("/users/@me/guilds")

        return render_template(
            "panel.html",
            user=user,
            guilds=guilds
        )

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/")

    # ========================
    # START SERVER (RENDER)
    # ========================

    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Dashboard rodando em 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
