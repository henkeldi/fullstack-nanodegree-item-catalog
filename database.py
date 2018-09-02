# -*- coding: utf-8 -*-
"""
Helper functions to access the Model (database_setup.py)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from database_setup import Base, User, Catalog, CatalogItem

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()


def get_catalogs():
    return session.query(Catalog).all()


def get_catalog(catalog_name):
    return session\
        .query(Catalog)\
        .filter_by(name=catalog_name)\
        .one()


def get_items(catalog_id=None):
    if catalog_id is not None:
        return session.query(CatalogItem)\
            .filter_by(catalog_id=catalog_id)\
            .all()
    else:
        return session.query(CatalogItem).all()


def get_item(catalog_id, item_name):
    return session.query(CatalogItem)\
        .filter_by(catalog_id=catalog_id, name=item_name)\
        .one()


def add_catalog_item(catalog_item,
                     creation_date,
                     catalog_id,
                     name,
                     description,
                     user_id):
    catalog_item = CatalogItem(catalog_item,
                               creation_date,
                               catalog_id,
                               name,
                               description,
                               user_id)
    session.add(catalog_item)
    session.commit()


def delete_catalog_item(catalog_item):
    session.delete(catalog_item)
    session.commit()


def create_user(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User)\
        .filter_by(email=login_session['email'])\
        .one()
    return user.id


def get_user_info(user_id):
    try:
        return session.query(User)\
            .filter_by(id=user_id)\
            .one()
    except NoResultFound:
        return None


def get_user_id(email):
    try:
        return session.query(User)\
            .filter_by(email=email)\
            .one()\
            .id
    except NoResultFound:
        return None
