#!/usr/bin/python2
# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from .. import database as db

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/catalog.json/')
def catalog_api():
    catalogs = db.get_catalogs()
    catalog_records = []
    for catalog in catalogs:
        catalog_record = catalog.serialize
        items = db.get_items(catalog_id=catalog.id)
        catalog_record['items'] = [i.serialize for i in items]
        catalog_records.append(catalog_record)
    return jsonify(catalog_records)


@api_blueprint.route('/catalog/<catalog_name>/<item_name>/json')
def catalog_item_api(catalog_name, item_name):
    catalog = db.get_catalog(catalog_name)
    catalog_item = db.get_item(catalog.id, item_name)
    return jsonify(catalog_item.serialize)
