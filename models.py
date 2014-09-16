from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, ConcreteBase
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry


Base = declarative_base()


class CommonCelestial(object):

    id = Column(Integer, primary_key=True)

    name = Column(String(150))

    location = Column(Geometry('POINT', dimension=3), nullable=False)


class Celestial(Base, CommonCelestial):

    __tablename__ = 'celestial'

    celestials = relationship('SystemCelestial', backref='system')

    celestial_points = None



class SystemCelestial(Base, CommonCelestial):
    __tablename__ = 'system_celestial'

    system_id = Column(Integer, ForeignKey(Celestial.id), nullable=False)
