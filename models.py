#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()
class Usuario(Base):
    __tablename__ = 'usuario'
    google_id = Column(String(), primary_key=True)
    name = Column(String())
    email = Column(String())
    profile_pic = Column(String())

class Categoria(Base):
    __tablename__ = 'categoria'
    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False, index=True)
    itens = relationship("Item", backref="item", cascade="all, delete, delete-orphan")

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
       	    'id': self.id,
            'name': self.name
       }


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False, index=True)
    description = Column(String())
    categoria_id = Column(Integer, ForeignKey('categoria.id'), nullable=False)



    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
       	    'id': self.id,
            'name': self.name,
            'description' : self.description
       }



engine = create_engine('sqlite:///catalogo3.db')
Base.metadata.create_all(engine)
