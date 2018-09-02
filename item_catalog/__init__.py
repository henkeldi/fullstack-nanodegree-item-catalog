#!/usr/bin/python2
# -*- coding: utf-8 -*-

from flask import Flask

from item_catalog.api.views import api_blueprint
from item_catalog.auth.views import auth_blueprint
from item_catalog.catalog.views import catalog_blueprint

app = Flask(__name__)

app.register_blueprint(api_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(catalog_blueprint)
