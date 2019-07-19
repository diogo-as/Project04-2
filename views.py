#!/usr/bin/python
# -*- coding: utf-8 -*-
from models import Base, Categoria, Item
from flask import Flask, render_template, request, url_for, redirect, jsonify, flash, make_response
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, desc
import sqlalchemy
import json, random, string, httplib2, requests
from flask import session as login_session

app = Flask(__name__)


engine = create_engine('sqlite:///catalogo3.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    #return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/', methods = ['GET'])
def allcategoriasanditens():
    if request.method == "GET":
        return render_template("index.html", categorias = session.query(Categoria).order_by(sqlalchemy.asc(Categoria.id)).all(), itens = session.query(Item).order_by(sqlalchemy.desc(Item.id)).limit(5))

@app.route('/catalogo/categorias', methods = ['GET'])
def categorias():
    if request.method == "GET":
        return render_template("newindex.html", categorias = session.query(Categoria).order_by(sqlalchemy.asc(Categoria.id)).all())


@app.route("/catalogo/categorias/newcategoria", methods = ['GET','POST'])
def newcategoria():
 if request.method == 'POST':
     categoria = Categoria(name=request.form['name'])
     session.add(categoria)
     session.commit()
     return redirect(url_for('categorias'))
 return render_template('newcategoria.html')


@app.route("/catalogo/categoria/<int:categoria_id>/edit", methods = ['GET','POST'])
def editcategoria(categoria_id):
    if request.method == 'GET':
        return render_template('editcategoria.html', categoria = session.query(Categoria).filter_by(id=categoria_id), categoria_id = categoria_id)
    if request.method == 'POST':
        session.query(Categoria).filter_by(id=categoria_id).update({'name':request.form['name']})
        session.commit()
        return redirect(url_for("categorias"))

@app.route("/catalogo/categoria/<int:categoria_id>/delete", methods = ['GET','POST'])
def deletecategoria(categoria_id):
    if request.method == 'GET':
        return render_template('deletecategoria.html', categoria = session.query(Categoria).filter_by(id=categoria_id), itens = session.query(Item).filter_by(categoria_id=categoria_id))
    if request.method == 'POST':
        result = session.query(Categoria).filter_by(id=categoria_id).one()
        session.delete(result)
        session.commit()
        return redirect(url_for("categorias"))

@app.route("/catalogo/categoria/itens", methods = ['GET'])
#@app.route("/catalogo/<categoria>/itens", methods = ['GET'])
def allitenscategoria():
    if request.method == 'GET':
        return render_template('allitens.html', itens = session.query(Item).all())

@app.route("/catalogo/categoria/<int:categoria_id>/itens", methods = ['GET'])
#@app.route("/catalogo/<categoria>/itens", methods = ['GET'])
def itenscategoria(categoria_id):
    if request.method == 'GET':
        return render_template('itens.html', itens = session.query(Item).filter_by(categoria_id=categoria_id), categorias = session.query(Categoria).filter_by(id=categoria_id), categoria_id = categoria_id)

@app.route("/catalogo/categoria/<int:categoria_id>/newitem", methods = ['GET','POST'])
def newitem(categoria_id):
 if request.method == 'POST':
     item = Item(name=request.form['name'], description=request.form['desc'], categoria_id=categoria_id)
     session.add(item)
     session.commit()
     return redirect(url_for('itenscategoria', categoria_id=categoria_id))
 return render_template('newitem.html', categoria=session.query(Categoria).filter_by(id=categoria_id))


@app.route("/catalogo/categoria/<int:categoria_id>/<int:item_id>/edit", methods = ['GET','POST'])
def edititem(categoria_id, item_id):
    if request.method == 'GET':
        return render_template('edititem.html', item = session.query(Item).filter_by(id=item_id), categoria = session.query(Categoria).filter_by(id=categoria_id), categoria_id=categoria_id, item_id=item_id)
    if request.method == 'POST':
        session.query(Item).filter_by(id=item_id).update({'name':request.form['name'],'description':request.form['description']})
        session.commit()
        return redirect(url_for("itenscategoria", categoria_id=categoria_id))

@app.route("/catalogo/categoria/itens/<int:item_id>/edit", methods = ['GET','POST'])
def editoneitem(item_id):
    if request.method == 'GET':
        return render_template('editoneitem.html', item = session.query(Item).filter_by(id=item_id), item_id=item_id)
    if request.method == 'POST':
        session.query(Item).filter_by(id=item_id).update({'name':request.form['name'],'description':request.form['description']})
        session.commit()
        return redirect(url_for("allitenscategoria"))

@app.route("/catalogo/categoria/<int:categoria_id>/<int:item_id>/delete", methods = ['GET','POST'])
def deleteitem(categoria_id, item_id):
    if request.method == 'GET':
        return render_template('deleteitem.html', categoria = session.query(Categoria).filter_by(id=categoria_id), item = session.query(Item).filter_by(id=item_id), categoria_id=categoria_id, item_id=item_id)
    if request.method == 'POST':
        result = session.query(Item).filter_by(id=item_id).one()
        session.delete(result)
        session.commit()
        return redirect(url_for("allitenscategoria"))
    return render_template('deleteitem.html', categoria = session.query(Categoria).filter_by(id=categoria_id), item = session.query(Item).filter_by(id=item_id), categoria_id=categoria_id, item_id=item_id)

if __name__ == '__main__':
    app.debug = True
    app.secret_key="secret"
    app.run(host='0.0.0.0', port=8002)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalogo2.db'
