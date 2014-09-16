#!/usr/bin/env python

from sys import argv
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from models import Celestial, SystemCelestial, Base


try:
    ccp_connection = argv[1]
except IndexError:
    ccp_connection = 'sqlite:///sqlite-latest.sqlite'
ccp_engine = create_engine(ccp_connection)
ccp_metadata = MetaData(bind=ccp_engine)
mapDenormalize = Table('mapDenormalize', ccp_metadata, autoload=True)


try:
    app = argv[2]
except IndexError:
    app_connection = 'postgresql://localhost/ccp_locations'
app_engine = create_engine(app_connection, echo=True)
Session = sessionmaker(bind=app_engine)


# Quick rundown on what needs to be done to set up a working database (this is
# assuming you already have PostgreSQL >9.1 and PostGIS >=2.0 installed):

# CREATE DATABASE ccp_locations;
# \c ccp_locations;
# CREATE EXTENSION postgis;

# GeoAlchemy2 doesn't really support three dimensions (contrary to it's
# documentation), so I ended up manually creating the table structure:

# CREATE TABLE celestial (
#     id SERIAL NOT NULL,
#     name VARCHAR(150),
#     PRIMARY KEY(id)
# );
# SELECT AddGeometryColumn('celestial', 'location', -1, 'POINT', 3);
# CREATE INDEX "idx_celestial_location"
#     ON "public"."celestial"
#     USING GIST(location);
# CREATE TABLE system_celestial (
#     id SERIAL NOT NULL,
#     name VARCHAR(150),
#     system_id INTEGER NOT NULL,
#     PRIMARY KEY(id),
#     FOREIGN KEY(system_id) REFERENCES celestial (id)
# );
# SELECT AddGeometryColumn('system_celestial', 'location', -1, 'POINT', 3);
# CREATE INDEX "idx_system_celestial_location"
#     ON "public"."system_celestial"
#     USING GIST(location);

#Base.metadata.create_all(app_engine)


def add_galaxy_celestials(ccp_conn, session):
    sel = select([mapDenormalize.c.itemID, mapDenormalize.c.x,
                  mapDenormalize.c.y, mapDenormalize.c.z,
                  mapDenormalize.c.itemName]).\
            where(mapDenormalize.c.solarSystemID == None)
    results = ccp_conn.execute(sel)
    for itemID, x, y, z, itemName in results:
        celestial = Celestial(id=itemID, name=itemName,
                location='POINT({} {} {})'.format(x, y, z))
        session.add(celestial)
    results.close()
    session.commit()


def add_system_celstials(ccp_conn, session):
    sel = select([mapDenormalize.c.itemID, mapDenormalize.c.x,
                  mapDenormalize.c.y, mapDenormalize.c.z,
                  mapDenormalize.c.itemName, mapDenormalize.c.solarSystemID]).\
            where(mapDenormalize.c.solarSystemID != None).\
            order_by(mapDenormalize.c.solarSystemID)
    results = ccp_conn.execute(sel)
    count = 0
    for itemID, x, y, z, itemName, systemID in results:
        celestial = SystemCelestial(id=itemID, name=itemName,
                system_id=systemID, location='POINT({} {} {})'.format(x, y, z))
        session.add(celestial)
        count += 1
        if count % 500 == 0:
            session.commit()
    results.close()
    session.commit()


if __name__ == '__main__':
    ccp_conn = ccp_engine.connect()
    add_galaxy_celestials(ccp_conn, Session())
    add_system_celstials(ccp_conn, Session())
