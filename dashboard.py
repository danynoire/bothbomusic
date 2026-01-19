from flask import Flask, request, abort, render_template
import os

def run_dashboard():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET")

    DASH_TOKEN = os.getenv("DASHBOARD_TOKEN")

    def check():
        token = request.args.get("token")
        if token != DASH_TOKEN:
            abort(403)

    @app.route("/")
    def home():
        check()
        return render_template("admin.html")

    print("🌐 Dashboard online (token)")
    app.run(host="0.0.0.0", port=10000)
