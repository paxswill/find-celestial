#!/usr/bin/env python
from __future__ import print_function
import csv
from sys import argv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from geoalchemy2 import WKTElement
from models import Celestial, SystemCelestial


try:
    app = argv[2]
except IndexError:
    app_connection = 'postgresql://localhost/ccp_locations'
app_engine = create_engine(app_connection)
Session = sessionmaker(bind=app_engine)


def get_celestial(system_id, x, y, z):
    if x == y and y == z and z == '0':
        return None
    session = Session()
    try:
        celestial = session.query(SystemCelestial).\
                filter(SystemCelestial.system_id == system_id).\
                order_by(func.ST_3DDistance(SystemCelestial.location,
                        WKTElement('POINT({} {} {})'.format(x, y, z)))).\
                limit(1).\
                one()
    except NoResultFound:
        return None
    return celestial
    

def add_celestial(row):
    celestial = get_celestial(row['locationID'], row['X'], row['Y'], row['Z'])
    new_row = dict(row)
    if celestial is not None:
        new_row['celestialName'] = celestial.name
        new_row['celestialID'] = celestial.id
    else:
        print("No celestial found for ", row)
        new_row['celestialName'] = ''
        new_row['celestialID'] = 0
    return new_row


if __name__ == '__main__':
    try:
        input_name = argv[1]
    except IndexError:
        input_name = 'Output.csv'
    with open(input_name, 'rb') as infile:
        reader = csv.DictReader(infile)
        modified_rows = list(map(add_celestial, reader))
    with open('with_celestials.csv', 'wb') as outfile:
        writer = csv.DictWriter(outfile, ('itemID', 'locationID',
                'celestialID', 'celestialName', 'X', 'Y', 'Z'))
        writer.writeheader()
        writer.writerows(modified_rows)
