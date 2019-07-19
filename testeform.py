#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from models import Base, Categoria, Item
from flask import Flask, render_template, request, url_for, redirect, jsonify
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__)
app.secret_key = '12345678'

class MyForm(FlaskForm):
    id = IntegerField('id', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    submit = SubmitField("Send")
@app.route('/submit', methods=('GET', 'POST'))
def submit():
    engine = create_engine('sqlite:///catalogo2.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    form = MyForm()
    if request.method == "POST" and form.validate_on_submit():
        cat = Categoria(form.id.data,form.name.data)

            #newitem = Categoria(ident = form.id.data,name = form.name.data)
        session.add(cat)
        session.commit()
        flash('Thanks for registering')
        return redirect('/test')
    return render_template('newcategorie.html', form=form)

@app.route('/test', methods=['GET'])
def test():
    engine = create_engine('sqlite:///catalogo2.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == "GET":
        catalogo = session.query(Categoria).all()
        #seq = jsonify(Categoria=[i.serialize for i in catalogo])
        #seq = json.loads(catalogo)
        return render_template("categorias.html", seq=catalogo)

if __name__ == '__main__':
    app.debug = True
    app.run(host='192.168.0.15', port=8001)
