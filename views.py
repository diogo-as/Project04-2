#!/usr/bin/python
# -*- coding: utf-8 -*-

# Internal imports
from models import Base, Categoria, Item, Usuario
from user import User
# External imports
from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    jsonify,
    flash,
    make_response,
    session as login_session
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from oauthlib.oauth2 import WebApplicationClient
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc

import sqlalchemy
import json
import os
import random
import string
import httplib2
import requests


# Configuration Google oatuh secrets
# GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
# GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_CLIENT_ID = "573092642795-ggvdh9jddsssucqntnh972giidgnodk0.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "5se_2jPB7_CQ_1EgPsIi4NGC"

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__)


engine = create_engine('sqlite:///catalogo.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# google login based on
# https://github.com/realpython/materials/tree/master/flask-google-login
# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('login.html')


# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    # Doesn't exist? Add to database
    if not User.get(unique_id):
        user = Usuario(
            google_id=unique_id.encode('utf-8'),
            name=users_name.encode('utf-8'),
            email=users_email.encode('utf-8'),
            profile_pic=picture.encode('utf-8')
        )
        session.add(user)
        session.commit()
    # Begin user session by logging the user in
    loggedUser = User.get(unique_id)
    login_user(loggedUser)

    # Send user back to homepage
    return render_template(
        "index.html",
        categorias=session.query
        (Categoria).order_by
        (sqlalchemy.asc(Categoria.id)).all(),
        itens=session.query(Item).order_by(sqlalchemy.asc(Item.id)).all(),
        loggeduser=loggedUser.name
        )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("index.html")


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

# Endpoint open to all visitors. Display all categories
# and itens.


@app.route('/', methods=['GET'])
def allcategoriasanditens():
    # check if users is logged to display name on page
    if current_user.is_authenticated and request.method == "GET":
        return render_template(
            "index.html",
            categorias=session.query
            (Categoria).order_by
            (sqlalchemy.asc(Categoria.id)).all(),
            itens=session.query(Item).order_by(sqlalchemy.asc(Item.id)).all(),
            loggeduser=current_user.name
        )
    else:
        return render_template(
            "index.html",
            categorias=session.query
            (Categoria).order_by
            (sqlalchemy.asc(Categoria.id)).all(),
            itens=session.query(Item).order_by(sqlalchemy.asc(Item.id)).all(),
            loggeduser=''
        )


# endpoint to list all categories in json
@app.route('/categories')
def categoriesjson():
    category = session.query(Categoria).all()
    return jsonify(Categoria=[i.serialize for i in category])


# endpoint to list all itens in json
@app.route('/itens')
def itensjson():
    itens = session.query(Item).all()
    return jsonify(Item=[i.serialize for i in itens])


# endpoint show all categories
@app.route('/catalogo/categorias', methods=['GET'])
@login_required
def categorias():
    if current_user.is_authenticated and request.method == "GET":
        return render_template(
            "newindex.html",
            categorias=session.query
            (Categoria).order_by
            (sqlalchemy.asc(Categoria.id)).all(),
            loggeduser=current_user.name
        )
    else:
        return render_template("login.html")


# endpoint create category
@app.route("/catalogo/categorias/newcategoria", methods=['GET', 'POST'])
@login_required
def newcategoria():
    if current_user.is_authenticated and request.method == 'POST':
        categoria = Categoria(name=request.form['name'])
        session.add(categoria)
        session.commit()
        return redirect(url_for('categorias'))

    return render_template(
        'newcategoria.html',
        loggeduser=current_user.name
    )


# endpoint edit category
@app.route(
    "/catalogo/categoria/<int:categoria_id>/edit",
    methods=['GET', 'POST']
)
@login_required
def editcategoria(categoria_id):
    if current_user.is_authenticated and request.method == 'GET':
        return render_template(
            'editcategoria.html',
            categoria=session.query(Categoria).filter_by(id=categoria_id),
            categoria_id=categoria_id,
            loggeduser=current_user.name
        )
    if current_user.is_authenticated and request.method == 'POST':
        session.query(Categoria).filter_by(id=categoria_id).update(
            {
                'name': request.form['name']
            }
        )
        session.commit()
        return redirect(url_for("categorias"))


# endpoint delete category
@app.route(
    "/catalogo/categoria/<int:categoria_id>/delete",
    methods=['GET', 'POST']
)
@login_required
def deletecategoria(categoria_id):
    if current_user.is_authenticated and request.method == 'GET':
        return render_template(
            'deletecategoria.html',
            categoria=session.query(Categoria).filter_by(id=categoria_id),
            itens=session.query(Item).filter_by(categoria_id=categoria_id),
            loggeduser=current_user.name
        )
    if current_user.is_authenticated and request.method == 'POST':
        result = session.query(Categoria).filter_by(id=categoria_id).one()
        session.delete(result)
        session.commit()
        return redirect(url_for("categorias"))


# endpoint display all itens
@app.route("/catalogo/categoria/itens", methods=['GET'])
@login_required
def allitenscategoria():
    if current_user.is_authenticated and request.method == 'GET':
        return render_template(
            'allitens.html',
            itens=session.query(Item).all(),
            loggeduser=current_user.name
        )
    else:
        return render_template("login.html")


# endpoint display all itens of one category
@app.route("/catalogo/categoria/<int:categoria_id>/itens", methods=['GET'])
@login_required
def itenscategoria(categoria_id):
    if current_user.is_authenticated and request.method == 'GET':
        return render_template(
            'itens.html',
            itens=session.query(Item).filter_by(categoria_id=categoria_id),
            categorias=session.query(Categoria).filter_by(id=categoria_id),
            categoria_id=categoria_id,
            loggeduser=current_user.name
        )


# endpoint to create new item
@app.route(
    "/catalogo/categoria/<int:categoria_id>/newitem",
    methods=['GET', 'POST']
)
@login_required
def newitem(categoria_id):
    if current_user.is_authenticated and request.method == 'POST':
        item = Item(
            name=request.form['name'],
            description=request.form['desc'],
            categoria_id=categoria_id
        )
        session.add(item)
        session.commit()
        return redirect(url_for('itenscategoria', categoria_id=categoria_id))

    return render_template(
        'newitem.html',
        categoria=session.query(Categoria).filter_by(id=categoria_id),
        loggeduser=current_user.name
    )


# endpoint to edit item
@app.route(
    "/catalogo/categoria/<int:categoria_id>/<int:item_id>/edit",
    methods=['GET', 'POST']
)
@login_required
def edititem(categoria_id, item_id):
    if current_user.is_authenticated and request.method == 'GET':
        return render_template(
            'edititem.html',
            item=session.query(Item).filter_by(id=item_id),
            categoria=session.query(Categoria).filter_by(id=categoria_id),
            categoria_id=categoria_id,
            item_id=item_id,
            loggeduser=current_user.name
        )
    if current_user.is_authenticated and request.method == 'POST':
        session.query(Item).filter_by(id=item_id).update(
            {
                'name': request.form['name'],
                'description': request.form['description']
            }
        )
        session.commit()
        return redirect(url_for(
            "itenscategoria",
            categoria_id=categoria_id)
        )


# endpoint edit itens
@app.route(
    "/catalogo/categoria/itens/<int:item_id>/edit",
    methods=['GET', 'POST']
)
@login_required
def editoneitem(item_id):
    if current_user.is_authenticated and request.method == 'GET':
        return render_template(
            'editoneitem.html',
            item=session.query(Item).filter_by(id=item_id),
            item_id=item_id,
            loggeduser=current_user.name
        )
    if current_user.is_authenticated and request.method == 'POST':
        session.query(Item).filter_by(id=item_id).update(
            {
                'name': request.form['name'],
                'description': request.form['description']
            }
        )
        session.commit()
        return redirect(url_for("allitenscategoria"))


# endpoint to delete item
@app.route(
    "/catalogo/categoria/<int:categoria_id>/<int:item_id>/delete",
    methods=['GET', 'POST']
)
@login_required
def deleteitem(categoria_id, item_id):
    if current_user.is_authenticated and request.method == 'GET':
        return render_template(
            'deleteitem.html',
            categoria=session.query(Categoria).filter_by(id=categoria_id),
            item=session.query(Item).filter_by(id=item_id),
            categoria_id=categoria_id,
            item_id=item_id,
            loggeduser=current_user.name)
    if current_user.is_authenticated and request.method == 'POST':
        result = session.query(Item).filter_by(id=item_id).one()
        session.delete(result)
        session.commit()
        return redirect(url_for("allitenscategoria"))


# main function
if __name__ == '__main__':
    # app.debug = True
    app.secret_key = "secret"
    app.run(host='0.0.0.0', port=5000, ssl_context="adhoc", debug=True)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalogo2.db'
