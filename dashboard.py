from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "Dashboard online (sem OAuth)"

def run_dashboard():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
