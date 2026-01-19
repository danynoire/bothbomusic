from flask import Flask

def run_dashboard(bot):
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "HB Music Dashboard Online ✅"

    print("🌐 Dashboard online")
    app.run(host="0.0.0.0", port=10000)
