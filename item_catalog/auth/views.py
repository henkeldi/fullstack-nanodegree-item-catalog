#!/usr/bin/python2
# -*- coding: utf-8 -*-
import os
import random
import string
import json
import httplib2
import requests
from functools import wraps

from flask import (Blueprint,
                   session as login_session,
                   make_response,
                   request,
                   redirect,
                   flash,
                   render_template)

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from .. import database as db


auth_blueprint = Blueprint('auth', __name__,
                           template_folder='templates')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there", "error")
            return redirect('/login')
    return decorated_function


@auth_blueprint.route('/login')
def login():
    state = ''.join(
        [
            random.choice(string.ascii_uppercase + string.digits)
            for x
            in xrange(32)
        ])
    login_session['state'] = state
    return render_template('login.html', STATE=state)


current_dir = os.path.dirname(os.path.abspath(__file__))
credentials_file = os.path.join(current_dir, 'client_secret.json')

with open(credentials_file, 'r') as f:
    CLIENT_ID = json.load(f)['web']['client_id']


@auth_blueprint.route('/gconnect', methods=['POST'])
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
        oauth_flow = flow_from_clientsecrets(credentials_file, scope='')
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
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['access_token'] = credentials.access_token
    login_session['username'] = data.get('name', '')
    login_session['picture'] = data["picture"]
    login_session['email'] = data['email']

    user_id = db.get_user_id(data["email"])
    if not user_id:
        user_id = db.create_user(login_session)

    login_session['user_id'] = user_id

    response = make_response(json.dumps('OK'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@auth_blueprint.route("/gdisconnect")
def gdisconnect():
    '''Google logout

    src: https://github.com/udacity/ud330/
        blob/master/Lesson2/step6/project.py#L126
    '''

    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user is not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token='
    url += access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['user_id']
        del login_session['access_token']
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
