from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


def init_db():
    engine = create_engine('sqlite:////./nursebot.db')
    Base.metadata.create_all(engine)
    return engine


def get_engine():
    engine = create_engine('sqlite:////./nursebot.db')
    return engine


def db_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
