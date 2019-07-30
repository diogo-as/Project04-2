import os
from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
#app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_ID"] = '573092642795-ggvdh9jddsssucqntnh972giidgnodk0.apps.googleusercontent.com'
#app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = '5se_2jPB7_CQ_1EgPsIi4NGC'
google_bp = make_google_blueprint(scope=["email"])
app.register_blueprint(google_bp, url_prefix="/login")

@app.route("/")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/userinfo/v2/me")
    assert resp.ok, resp.text
    return "You are {email} on Google".format(email=resp.json()["email"])
