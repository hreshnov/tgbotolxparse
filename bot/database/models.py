# DATABASE
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table, Column, Integer, ForeignKey

# DB ORM[ SQLALCHEMY ]
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, Boolean, MetaData

# OTHER
import json
from threading import Lock
from typing import Union, List


DATABASE_NAME = 'text_db'
engine = create_engine(f'sqlite:///{DATABASE_NAME}')
BaseDB = declarative_base()
LocalSession = scoped_session(sessionmaker(bind=engine))


class User(BaseDB):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    is_admin = Column(Boolean, default=False)


class Ad(BaseDB):
    __tablename__ = 'ads'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    area = Column(String)
    price = Column(String)
    room = Column(Integer)
    square = Column(Integer)
    tenant_span = Column(String)
    url = Column(String)
    images = Column(String)
    city = Column(String)


BaseDB.metadata.create_all(bind=engine)

