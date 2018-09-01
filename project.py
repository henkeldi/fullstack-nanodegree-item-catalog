#!/usr/bin/python2
# -*- coding: utf-8 -*-
import random
import string
import json
import httplib2
import requests
from datetime import datetime

from flask import Flask,\
    render_template,\
    jsonify,\
    redirect,\
    request,\
    make_response,\
    session as login_session,\
    url_for

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from database_setup import Base, User, Catalog, CatalogItem

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

with open('client_secret.json', 'r') as f:
    CLIENT_ID = json.load(f)['web']['client_id']


@app.route('/catalog.json/')
def catalog_api():
    catalogs = session.query(Catalog).all()
    catalog_records = []
    for catalog in catalogs:
        catalog_record = catalog.serialize
        items = session.query(CatalogItem)\
            .filter_by(catalog_id=catalog.id)\
            .all()
        catalog_record['items'] = [i.serialize for i in items]
        catalog_records.append(catalog_record)
    return jsonify(catalog_records)


@app.route('/login')
def login():
    state = ''.join(
        [
            random.choice(string.ascii_uppercase + string.digits)
            for x
            in xrange(32)
        ])
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''Google login
       src: https://github.com/udacity/ud330/
            blob/master/Lesson2/step6/project.py#L40
    '''

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        resonse.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token='
    url += access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID doesn't match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data['email']

    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    response = make_response(json.dumps('OK'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route("/gdisconnect")
def gdisconnect():
    '''Google logout
       src: https://github.com/udacity/ud330/
            blob/master/Lesson2/step6/project.py#L126
    '''

    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user is not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = json.loads(credentials)['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token='
    url += access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog/')
def catalogs():
    catalogs = session.query(Catalog).all()
    items = session.query(CatalogItem).all()
    if 'username' in login_session:
        return render_template('catalogs.html',
                               catalogs=catalogs,
                               items=items)
    else:
        return render_template('public_catalogs.html',
                               catalogs=catalogs,
                               items=items)


@app.route('/catalog/<catalog_name>/')
def catalog(catalog_name):
    catalogs = session.query(Catalog).all()
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()
    catalog_items = session.query(CatalogItem)\
        .filter_by(catalog_id=catalog.id)\
        .all()
    item_section_title = '{catalog_name} Items ({num_items} item{suffix})'\
        .format(
            catalog_name=catalog.name,
            num_items=len(catalog_items),
            suffix='' if len(catalog_items) == 1 else 's')
    if 'user_id' in login_session:
        return render_template('catalog.html',
                               catalog=catalog,
                               catalogs=catalogs,
                               catalog_items=catalog_items,
                               item_section_title=item_section_title)
    else:
        return render_template('public_catalog.html',
                               catalog=catalog,
                               catalogs=catalogs,
                               catalog_items=catalog_items,
                               item_section_title=item_section_title)


@app.route('/catalog/<catalog_name>/<item_name>')
def catalog_item(catalog_name, item_name):
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()
    catalog_item = session.query(CatalogItem)\
        .filter_by(catalog_id=catalog.id, name=item_name)\
        .one()
    if 'username' not in login_session:
        return render_template('public_catalog_item.html',
                               catalog_item=catalog_item)
    else:
        creator = getUserInfo(catalog.user_id)
        if login_session['user_id'] == creator.id:
            return render_template('catalog_item.html',
                                   catalog_name=catalog_name,
                                   catalog_item=catalog_item)
        else:
            return render_template('public_catalog_item.html',
                                   catalog_item=catalog_item)


@app.route('/catalog///add', methods=['GET', 'POST'])
def add_catalog_item():
    if 'username' not in login_session:
        return redirect('/login')
    catalogs = session.query(Catalog).all()
    if request.method == 'POST':
        category_name = request.form['category']
        catalog = session.query(Catalog).filter_by(name=category_name).one()
        catalog_item = CatalogItem(
            creation_date=datetime.now(),
            catalog_id=catalog.id,
            name=request.form['name'],
            description=request.form['description']
        )
        session.add(catalog_item)
        session.commit()
        return redirect(url_for('catalogs'))
    else:
        return render_template('add_catalog_item.html', catalogs=catalogs)


@app.route('/catalog/<catalog_name>/<item_name>/edit', methods=['GET', 'POST'])
def edit_catalog_item(catalog_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()
    catalogs = session.query(Catalog).all()
    catalog_item = session.query(CatalogItem)\
        .filter_by(catalog_id=catalog.id, name=item_name)\
        .one()
    if request.method == 'POST':
        catalog_item.name = request.form['name']
        catalog_item.description = request.form['description']
        new_catalog = session.query(Catalog)\
            .filter_by(name=request.form['category'])\
            .one()
        catalog_item.catalog_id = new_catalog.id
        session.add(catalog_item)
        session.commit()
        return redirect(url_for('catalog', catalog_name=catalog_name))
    else:
        return render_template('edit_catalog_item.html',
                               catalogs=catalogs,
                               catalog=catalog,
                               catalog_item=catalog_item)


@app.route('/catalog/<catalog_name>/<item_name>/delete',
           methods=['GET', 'POST'])
def delete_catalog_item(catalog_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()
    catalog_item = session.query(CatalogItem)\
        .filter_by(catalog_id=catalog.id, name=item_name)\
        .one()
    if request.method == 'POST':
        session.delete(catalog_item)
        session.commit()
        return redirect(url_for('catalog', catalog_name=catalog_name))
    else:
        return render_template('delete_catalog_item.html',
                               catalog=catalog,
                               catalog_item=catalog_item)


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User)\
        .filter_by(email=login_session['email'])\
        .one()
    return user.id


def getUserInfo(user_id):
    return session.query(User)\
        .filter_by(id=user_id)\
        .one()


def getUserID(email):
    try:
        return session.query(User)\
            .filter_by(email=email)\
            .one()\
            .id
    except Exception:
        return None


if __name__ == '__main__':
    app.secret_key = 'WLEF81VR1QKV8PIQEY658IXN5ZGZAXCR'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
