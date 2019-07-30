import os
from flask import Flask, redirect, url_for, jsonify
from flask_dance.contrib.github import make_github_blueprint, github

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["GITHUB_OAUTH_CLIENT_ID"] = 'e0495f5164e6ef2dfc77'
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = '0c8c10f71646870a8b538ec25226302defc84553'
github_bp = make_github_blueprint()
app.register_blueprint(github_bp, url_prefix="/login")


@app.route("/")
def index():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    assert resp.ok
    #return "You are @{login} on GitHub".format(login=resp.json()["login"])
    return resp.json()

if __name__ == '__main__':
    app.debug = True
    app.secret_key="secret"
    app.run(ssl_context="adhoc")
