#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
The model part of the webpage
"""
import os

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    """
    Registered user information is stored in db
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    picture = Column(String(250))
    email = Column(String(250))

    @property
    def serialize(self):
        return {
           'id': self.id,
           'name': self.name,
           'email': self.email,
           'picture': self.picture
        }


class Catalog(Base):
    """
    Catalog information
    """
    __tablename__ = 'catalog'

    name = Column(String(80), nullable=False, unique=True)
    id = Column(Integer, primary_key=True)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


class CatalogItem(Base):
    """
    Catalog item
    """
    __tablename__ = 'catalog_item'

    name = Column(String(80), nullable=False, unique=True)
    id = Column(Integer, primary_key=True)
    creation_date = Column(DateTime, nullable=False)
    description = Column(String(250))
    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship(Catalog)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'creation_date': self.creation_date,
            'description': self.description,
            'catalog_id': self.catalog_id,
            'user_id': self.user_id
        }

current_dir = os.path.dirname(os.path.abspath(__file__))
engine = create_engine('sqlite:///{}/catalog.db?check_same_thread=False'.format(current_dir))
Base.metadata.create_all(engine)
