
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

_db = create_engine('sqlite:///library.sqllite', echo=False)
session = sessionmaker(bind=_db)
_metadata = MetaData(bind=_db)
_Base = declarative_base()

class Books(_Base):
    __table__ = Table('books', _metadata, autoload=True)
class Desc(_Base):
    __table__ = Table('desc', _metadata, autoload=True)
class Data(_Base):
    __table__ = Table('data', _metadata, autoload=True)
class Meta(_Base):
    __table__ = Table('meta', _metadata, autoload=True)

