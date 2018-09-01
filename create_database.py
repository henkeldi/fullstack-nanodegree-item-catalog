#!/usr/bin/python2
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, CatalogItem
from datetime import datetime
import json


def main():
    """Creats catalog database entries from a JSON file
    """
    engine = create_engine('sqlite:///catalog.db')
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    with open('initial_catalog_data.json', 'r') as f:
        data = json.load(f)

    for catalog_data in data:
        catalog = Catalog(name=catalog_data['name'],
                          user_id=catalog_data['user_id'])
        session.add(catalog)
        session.commit()
        catalog_id = session.query(Catalog)\
            .filter_by(name=catalog_data['name'])\
            .one()\
            .id

        for item_data in catalog_data['items']:
            item = CatalogItem(name=item_data['name'],
                               description=item_data['description'],
                               catalog_id=catalog_id,
                               creation_date=datetime.now())
            session.add(item)
            session.commit()

    session.close()


if __name__ == '__main__':
    main()
