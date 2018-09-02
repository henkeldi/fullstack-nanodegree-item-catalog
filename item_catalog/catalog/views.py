#!/usr/bin/python2
# -*- coding: utf-8 -*-
from datetime import datetime

from flask import (Blueprint,
                   session as login_session,
                   request,
                   redirect,
                   url_for,
                   flash,
                   render_template)

from .. import database as db
from ..auth.views import login_required

catalog_blueprint = Blueprint('catalog', __name__,
                              template_folder='templates')


@catalog_blueprint.route('/')
@catalog_blueprint.route('/catalog/')
def catalogs():
    catalogs = db.get_catalogs()
    items = db.get_items()
    if 'username' in login_session:
        return render_template('catalogs.html',
                               catalogs=catalogs,
                               items=items)
    else:
        return render_template('public_catalogs.html',
                               catalogs=catalogs,
                               items=items)


@catalog_blueprint.route('/catalog/<catalog_name>/')
def catalog(catalog_name):
    catalogs = db.get_catalogs()
    catalog = db.get_catalog(catalog_name)
    catalog_items = db.get_items(catalog.id)
    item_section_title = '{catalog_name} Items ({num_items} item{suffix})'\
        .format(catalog_name=catalog.name,
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


@catalog_blueprint.route('/catalog/<catalog_name>/<item_name>')
def catalog_item(catalog_name, item_name):
    catalog = db.get_catalog(catalog_name)
    catalog_item = db.get_item(catalog.id, item_name)
    if 'username' not in login_session:
        return render_template('public_catalog_item.html',
                               catalog_item=catalog_item)
    else:
        creator = db.get_user_info(catalog_item.user_id)
        if creator is not None and login_session['user_id'] == creator.id:
            return render_template('catalog_item.html',
                                   catalog_name=catalog_name,
                                   catalog_item=catalog_item)
        else:
            return render_template('public_catalog_item.html',
                                   catalog_item=catalog_item)


@catalog_blueprint.route('/catalog///add',
                         methods=['GET', 'POST'])
@login_required
def add_catalog_item():
    catalogs = db.get_catalogs()
    if request.method == 'POST':
        category_name = request.form['category']
        catalog = db.get_catalog(category_name)
        user_id = login_session['user_id']
        db.add_catalog_item(creation_date=datetime.now(),
                            catalog_id=catalog.id,
                            name=request.form['name'],
                            description=request.form['description'],
                            user_id=user_id)
        flash("Item added", "success")
        return redirect(url_for('catalog.catalogs'))
    else:
        return render_template('add_catalog_item.html', catalogs=catalogs)


@catalog_blueprint.route('/catalog/<catalog_name>/<item_name>/edit',
                         methods=['GET', 'POST'])
@login_required
def edit_catalog_item(catalog_name, item_name):
    creator = db.get_user_info(catalog_item.user_id)
    if creator is None or login_session['user_id'] != creator.id:
        flash("You are not allowed to access there", "error")
        return redirect('/')

    catalog = db.get_catalog(catalog_name)
    catalog_item = db.get_item(catalog.id, item_name)

    catalogs = db.get_catalogs()
    if request.method == 'POST':
        catalog_item.name = request.form['name']
        catalog_item.description = request.form['description']
        catalog = db.get_catalog(request.form['category'])
        catalog_item.catalog_id = catalog.id
        db.edit_catalog_item(catalog_item)
        flash("Item successfully edited", "success")
        return redirect(url_for('catalog.catalog', catalog_name=catalog_name))
    else:
        return render_template('edit_catalog_item.html',
                               catalogs=catalogs,
                               catalog=catalog,
                               catalog_item=catalog_item)


@catalog_blueprint.route('/catalog/<catalog_name>/<item_name>/delete',
                         methods=['GET', 'POST'])
@login_required
def delete_catalog_item(catalog_name, item_name):
    creator = db.get_user_info(catalog_item.user_id)
    if creator is None or login_session['user_id'] != creator.id:
        flash("You are not allowed to access there", "error")
        return redirect('/')

    catalog = db.get_catalog(catalog_name)
    catalog_item = db.get_item(catalog.id, item_name)

    if request.method == 'POST':
        db.delete_catalog_item(catalog_item)
        flash("Item successfully deleted", "success")
        return redirect(url_for('catalog.catalog', catalog_name=catalog_name))
    else:
        return render_template('delete_catalog_item.html',
                               catalog=catalog,
                               catalog_item=catalog_item)
