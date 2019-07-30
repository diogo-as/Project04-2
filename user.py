#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask_login import UserMixin
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

# Internal imports
from models import Base, Usuario


class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
         #db = get_db()
         #user = db.execute(
         #    "SELECT * FROM user WHERE id = ?", (user_id,)
         #).fetchone()
         engine = create_engine('sqlite:///catalogo3.db?check_same_thread=False')
         Base.metadata.bind = engine
         DBSession = sessionmaker(bind=engine)
         session = DBSession()
         usuario = session.query(Usuario).filter_by(google_id=user_id).first()
         if not usuario:
             return None
         else:
             user = User(id_=usuario.google_id, name=usuario.name, email=usuario.email, profile_pic=usuario.profile_pic)
             return user

    @staticmethod
    def create(id_, name, email, profile_pic):
        user = Usuario(google_id=id, name=name, email=email, profile_pic=profile_pic)
        session.add(user)
        session.commit()
