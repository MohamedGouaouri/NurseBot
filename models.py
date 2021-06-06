import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Poll(Base):
    __tablename__ = "polls"
    pollid = Column(Integer, primary_key=True)
    finished = Column(Boolean, default=False)
    create_at = Column(DateTime, default=datetime.datetime.utcnow())
    def __init__(self, pollid):
        self.pollid = pollid

class Task(Base):
    __tablename__ = "tasks"
    task_id = Column(Integer, primary_key=True)
    taskname = Column(String, unique=True, nullable=False)
    finished = Column(Boolean, default=False)
    def __init__(self, task_name):
        self.taskname = task_name